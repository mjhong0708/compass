import os
import subprocess
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union

import ase.build
import ase.io
import numpy as np
from ase import Atoms
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader


loader = FileSystemLoader(Path(__file__).parent / "templates")
env = Environment(loader=loader)


class Packer:
    """
    molecules: list[tuple[Atoms, int]]
    """

    def __init__(self, molecules, box, margin=0.0):
        self.molecules = molecules
        if isinstance(box, Box):
            self.box = box
        else:
            self.box = Box.create(box)
        self.margin = margin

    def _write_molecules(self, tmpdir):
        for i, (mol, _) in enumerate(self.molecules):
            if not isinstance(mol, Atoms):
                raise TypeError(f"molecule must be str or Atoms, not {type(mol)}")
            mol.write(f"{tmpdir}/mol{i}.xyz")

    def _write_input(self, tmpdir, box, tolerance):
        template = env.get_template("pack_box.inp")
        pack_info = {f"{tmpdir}/mol{i}.xyz": n for i, (_, n) in enumerate(self.molecules)}
        box_repr = box.to_box_repr()

        with open(f"{tmpdir}/pack.inp", "w") as f:
            f.write(
                template.render(
                    tolerance=tolerance,
                    out_filename="packed.xyz",
                    pack_info=pack_info,
                    box_repr=box_repr,
                )
            )

    def _run_packmol(self, tmpdir: str):
        pwd = Path.cwd()
        os.chdir(tmpdir)
        output = subprocess.check_output("packmol < pack.inp", shell=True)
        os.chdir(pwd)
        return output.decode("utf-8")

    def _read_packed_box(self, sort_result: bool, tmpdir: str, repack: bool):
        try:
            packed = ase.io.read(f"{tmpdir}/packed.xyz")
        except FileNotFoundError:
            raise RuntimeError("packmol failed to pack molecules.")
        if sort_result:
            packed = ase.build.sort(packed)
        if repack:
            packed = self._repack_in_box(packed)
        return packed

    def _repack_in_box(self, atoms):
        new = deepcopy(atoms)
        new.cell = self.box.to_array()
        new.pbc = True
        new.center()
        return new

    def pack(self, tolerance: float, sort_result: bool = True, repack: bool = True, retreive_log: bool = False):
        box = deepcopy(self.box)
        box.xmin += self.margin
        box.xmax -= self.margin
        box.ymin += self.margin
        box.ymax -= self.margin
        box.zmin += self.margin
        box.zmax -= self.margin

        pwd = Path.cwd()
        with TemporaryDirectory() as tmpdir:
            self._write_molecules(tmpdir)
            self._write_input(tmpdir, box, tolerance)
            packmol_output = self._run_packmol(tmpdir)
            packed = self._read_packed_box(sort_result, tmpdir, repack)
            if retreive_log:
                (pwd / "packmol.log").write_text(packmol_output)
        return packed

    def smart_pack(self, tolerance, sort_result=True, retreive_log=False, step_size=0.1):
        """Automatically determine the margin to pack molecules.
        self.margin is ignored.

        Since packmol does not support pbc, we usually need to add a margin to box size, and
        pack molecules in the box. This method iteratively increases the margin until all
        the positions of molecules are inside the desiered box.
        """
        count = 0
        packed = self.pack(tolerance, sort_result, False, retreive_log)
        repacked = self._repack_in_box(packed)
        min_dist_packed = get_min_dist(packed)
        min_dist_repacked = get_min_dist(repacked)

        print(f"min_dist: {min_dist_packed:.3f} Angstrom")
        while not self.box.contains(packed) or min_dist_repacked < min_dist_packed:
            self.margin += step_size
            packed = self.pack(tolerance, sort_result, False, retreive_log)
            repacked = self._repack_in_box(packed)
            count += 1
            min_dist_packed = get_min_dist(packed)
            min_dist_repacked = get_min_dist(repacked)
            print(f"Iteration {count}: margin = {self.margin}")
        print(f"Done. Final margin: {self.margin}")
        packed = self._repack_in_box(packed)
        return packed


def get_min_dist(atoms):
    if any(atoms.pbc):
        mic = True
    else:
        mic = False
    dm = atoms.get_all_distances(mic=mic)
    dm += np.eye(len(atoms)) * 100
    return dm.min()


@dataclass
class Box:
    """Rectangular box."""

    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float

    @classmethod
    def create(cls, box: Union[float, list, tuple, np.ndarray]):
        if isinstance(box, float):
            xmin, xmax = 0, box
            ymin, ymax = 0, box
            zmin, zmax = 0, box
        elif isinstance(box, (list, tuple, np.ndarray)):
            if len(box) == 3:
                xmin, xmax = 0, box[0]
                ymin, ymax = 0, box[1]
                zmin, zmax = 0, box[2]
            elif len(box) == 6:
                xmin, xmax = box[0], box[1]
                ymin, ymax = box[2], box[3]
                zmin, zmax = box[4], box[5]
            else:
                raise ValueError("If box is sequence, length must be 3 or 6")
        else:
            raise ValueError("Box must be float, sequence, or array-like.")
        return cls(xmin, xmax, ymin, ymax, zmin, zmax)

    @property
    def xlen(self):
        return self.xmax - self.xmin

    @property
    def ylen(self):
        return self.ymax - self.ymin

    @property
    def zlen(self):
        return self.zmax - self.zmin

    @property
    def volume(self):
        return self.xlen * self.ylen * self.zlen

    def to_box_repr(self):
        repr_str = f"{self.xmin} {self.ymin} {self.zmin} {self.xmax} {self.ymax} {self.zmax}"
        return repr_str

    def to_array(self):
        return np.array([self.xlen, self.ylen, self.zlen])

    def contains(self, atoms):
        atoms_xmin, atoms_xmax = atoms.positions[:, 0].min(), atoms.positions[:, 0].max()
        atoms_ymin, atoms_ymax = atoms.positions[:, 1].min(), atoms.positions[:, 1].max()
        atoms_zmin, atoms_zmax = atoms.positions[:, 2].min(), atoms.positions[:, 2].max()

        is_in_x_range = self.xmin <= atoms_xmin and atoms_xmax <= self.xmax
        is_in_y_range = self.ymin <= atoms_ymin and atoms_ymax <= self.ymax
        is_in_z_range = self.zmin <= atoms_zmin and atoms_zmax <= self.zmax
        return all([is_in_x_range, is_in_y_range, is_in_z_range])

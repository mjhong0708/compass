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

    def _run_packmol(self, tmpdir):
        pwd = Path.cwd()
        os.chdir(tmpdir)
        output = subprocess.check_output("packmol < pack.inp", shell=True)
        os.chdir(pwd)
        return output.decode("utf-8")

    def _read_packed_box(self, sort_result, tmpdir):
        try:
            packed = ase.io.read(f"{tmpdir}/packed.xyz")
        except FileNotFoundError:
            raise RuntimeError("packmol failed to pack molecules.")
        if sort_result:
            packed = ase.build.sort(packed)
        packed.cell = self.box.to_array()
        packed.pbc = True
        packed.center()
        return packed

    def pack(self, tolerance, sort_result=True, retreive_log=False):
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
            packed = self._read_packed_box(sort_result, tmpdir)
            if retreive_log:
                (pwd / "packmol.log").write_text(packmol_output)
        return packed


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

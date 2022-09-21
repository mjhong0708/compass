from ase import units
import math
import subprocess


def check_packmol_installed():
    """Check if packmol is installed."""
    try:
        subprocess.call("packmol < /dev/null", shell=True)
    except FileNotFoundError:
        raise FileNotFoundError("packmol is not installed.")


def box_size_at_density(molecules, density):
    """Calculate box size for given density.
    Args:
        molecules (list): List of molecules and number of each molecule.
        density (float): Density in g/cm^3.
    """
    total_mass_g = sum(mol.get_masses().sum() / units.mol * n for mol, n in molecules)
    cm = units.m / 100
    density_g_ang3 = density / cm**3
    volume_ang3 = total_mass_g / density_g_ang3
    a = math.pow(volume_ang3, 1 / 3)
    return a


def n_molecules_at_box_size(molecules, density, box_size):
    """Calculate number of molecules for given box size.
    Given a indivisible unit of molecule combination, calculate the factor of multiplication
    to get the number of molecules for given box size.

    Args:
        molecules (list): List of molecules and minimum numbers.
            ex) [(water, 3), (ehtnaol, 1)].
        density (float): Density in g/cm^3.
        box_size (float): Box size in angstrom.
    """
    curr_box_size = box_size_at_density(molecules, density)
    factor = (box_size / curr_box_size) ** 3
    return [(mol, int(n * factor)) for mol, n in molecules]

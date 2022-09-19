"""Utils for manipulating units.
Default units:
    - length: Angstrom (Å)
    - energy: Electron volt (eV)
    - mass: Atomic mass unit (u)
    - temperature: Kelvin (K)
These are considered as 1.
"""

# Some constants
k_b = 8.6173324e-5  # Boltzmann constant (eV/K)
mol = 6.02214086e23  # 1 mol (Avogadro's constant)
c = 2.99792458e8  # Speed of light (m/s)

# Length conversion factors
Angstrom = 1
m = 1e10
cm = 1e-2 * m
mm = 1e-3 * m
um = 1e-6 * m
nm = 1e-9 * m
pm = 1e-12 * m

# Energy conversion factors
eV = 1
Hartree = 27.2113845
Ha = Hartree  # Alias for Hartree
J = 6.24150974e18  # Joule
kJ = 1e3 * J  # 1 kJ
kcal = 4.184 * kJ  # 1 cal
cal = 1e-3 * kcal  # 1 kcal

# Mass conversion factors
g = 1.66054e-24  # amu to gram
mg = 1e-3 * g  # amu to milligram
kg = 1e3 * g  # amu to kilogram

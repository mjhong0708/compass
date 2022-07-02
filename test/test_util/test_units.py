from compass.util import units


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def test_legnth():
    assert is_close(1 * units.m, 1000 * units.mm)
    assert is_close(1 * units.m, 1e10 * units.Angstrom)


def test_water_density():
    """Test with water density"""
    water_mass = 18 * units.g
    num_waters = 112
    box_size = 15**3  # Angstrom
    density = num_waters * water_mass / box_size  # amu/Angstrom^3
    density /= units.kg / units.m**3  # kg/m^3
    assert is_close(density, 997, rel_tol=50)


def test_energy_conversion():
    """Test energy conversion"""
    assert is_close(1 / (units.kJ / units.mol), 96.4915666370759, rel_tol=1e-3)
    assert is_close(1 / (units.kcal / units.mol), 23.062063375661, rel_tol=1e-3)
    assert is_close((1 * units.Ha) / (units.kJ / units.mol), 2625.5, rel_tol=1e-3)
    assert is_close((1 * units.Ha) / (units.kcal / units.mol), 627.51, rel_tol=1e-3)
    assert is_close(300 * units.k_b, 0.025, rel_tol=1e-1)

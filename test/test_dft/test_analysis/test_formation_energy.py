from hypothesis import strategies
from hypothesis import given
from compass.dft.analysis.formation_energy import Product


@given(energy=strategies.floats(min_value=-50, max_value=-10))
def test_formation_energy(energy):
    molecules = {"A": -5.34, "B": -10.34}
    product = "[A]/2[B]"
    reaction_product = Product(product, energy, molecules)

    E_form = energy - molecules["A"] - 2 * molecules["B"]
    assert abs(reaction_product.calculate_reaction_energy() - E_form) < 1e-8

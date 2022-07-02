import re
from typing import Dict

import toolz
from compass.util import units

component_pattern = r"[\d+]?\[[\+\w+\d+]+\]"


class Product:
    """
    Syntax is like: [Pt_111]/3[OOH](adsorption)
    Each component should be written in square brackets, and the number
    of atoms is written in front of the bracket.
    Comment should be written in parenthesis.

    Energies can be given in different units, and default unit is eV.
    If unit is specified, the energy will be considered as given unit and
    converted to eV.

    Args:
        reprentation (str): Reaction product representation.
        energy (float): Reaction product energy. Default unit is eV.
        ref_energies (Dict[str, float]): Reference energies for each component.
    """

    def __init__(self, reprentation: str, energy: float, ref_energies: Dict[str, float], unit: float = units.eV):
        self.reprentation = reprentation
        self.energy = energy * unit
        self.components = _parse_system(reprentation)
        self.ref_energies = toolz.valmap(lambda x: x * unit, ref_energies)
        self._unit = unit

    def __str__(self):
        return self.reprentation

    def __repr__(self):
        return self.__str__()

    def calculate_reaction_energy(self, target_unit: float = units.eV) -> float:
        """Calculate reaction energy."""
        E_rxn = self.energy
        for reactant, num_reactants in self.components.items():
            E_rxn -= num_reactants * self.ref_energies[reactant]
        return E_rxn / target_unit


def _parse_system(system: str) -> Dict[str, int]:
    """Parses a model system representation.


    Args:
        system_str (str): Model system representation.

    Returns:
        Dict[str, int]: Dictionary of reactant components and their numbers.
    """
    component_reprs = re.findall(component_pattern, system)
    components = {}
    for m in component_reprs:
        start_pos = m.find("[")
        num = int(m[:start_pos]) if start_pos != 0 else 1
        name = m[start_pos + 1 : -1]
        components[name] = num
    return components

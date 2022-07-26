from typing import List, Optional
from mp_api import MPRester
from . import API_KEY


def get_stable_phase(
    chemsys: str,
    max_e_above_hull: float = 0.0,
    return_only_structure: bool = False,
    fields: Optional[List[str]] = None,
    **kwargs,
):
    if return_only_structure:
        if "structure" not in fields:
            fields.append("structure")

    with MPRester(API_KEY) as mpr:
        docs = mpr.summary.search(chemsys=chemsys, fields=fields, **kwargs)
        if len(docs) == 0:
            return None

    def is_stable(doc):
        E_above_hull = doc.energy_above_hull
        if max_e_above_hull == 0.0:
            return doc.is_stable
        else:
            return E_above_hull <= max_e_above_hull

    stable_docs = filter(is_stable, docs)
    if return_only_structure:
        return [d.structure for d in stable_docs]
    return list(stable_docs)

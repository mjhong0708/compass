from typing import List, Optional
from mp_api import MPRester
from . import API_KEY


def get_stable_phase(chemsys: str, fields: Optional[List[str]] = None, return_only_structure: bool = False, **kwargs):
    if return_only_structure:
        if "structure" not in fields:
            fields.append("structure")
    with MPRester(API_KEY) as mpr:
        docs = mpr.summary.search(chemsys=chemsys, fields=fields, **kwargs)
        if len(docs) == 0:
            return None
    docs.sort(key=lambda x: x.energy_above_hull)
    return docs[0].structure if return_only_structure else docs[0]

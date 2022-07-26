import os
import warnings
from compass.util.utils import check_installed

check_installed("pymatgen")
check_installed("mp_api")

API_KEY = os.environ.get("MP_API_KEY", None)
if API_KEY is None:
    warnings.warn("MP_API_KEY not found. This will cause error in mp-api. Please set it in your environment.")

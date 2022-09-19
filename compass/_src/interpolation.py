from scipy.interpolate import interp1d

from typing import Literal, Tuple
import numpy as np

InterpolationKind = Literal[
    "linear", "nearest", "nearest-up", "zero", "slinear", "quadratic", "cubic", "previous", "next"
]


def interpolate(
    x: np.ndarray,
    y: np.ndarray,
    kind: InterpolationKind = "cubic",
    refine_ratio: int = 10,
) -> Tuple[np.ndarray, np.ndarray]:
    """Thin wrapper around scipy.interpolate.interp1d.
    Interpolate a 1d array using scipy.interpolate.interp1d, and return the interpolated values.

    Args:
        x (np.ndarray): x values
        y (np.ndarray): y values
        kind (InterpolationKind, optional): Interpolation kind. Defaults to "linear".
        refine_ratio (int, optional): Refine ratio. Defaults to 10.

    Returns:
        Tuple[np.ndarray]: New x mesh and interpolated y values
    """
    if not isinstance(refine_ratio, int):
        raise TypeError("refine_ratio must be an python integer")
    if refine_ratio < 2:
        raise ValueError("refine_ratio must be >= 2")
    x, y = check_arr_inputs(x, y)
    interpolator = interp1d(x, y, kind=kind)

    new_size = x.shape[0] * refine_ratio
    x_new = np.linspace(x[0], x[-1], new_size)
    y_new = interpolator(x_new)
    return x_new, y_new


def check_arr_inputs(x, y):
    # check if both are 1d array of same length
    if not (isinstance(x, np.ndarray) and isinstance(y, np.ndarray)):
        raise TypeError("x and y must be numpy arrays")

    x = x.squeeze()
    y = y.squeeze()
    if not (x.ndim == 1 and y.ndim == 1):
        raise ValueError("x and y must be 1d arrays")

    if not (x.shape[0] == y.shape[0]):
        raise ValueError("x and y must have same length")

    return x, y

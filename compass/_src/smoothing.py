from typing import Literal
import numpy as np
from scipy.signal import savgol_filter
from compass._src.misc import notice_available_args


class Smoother:
    savgol_kwargs = {"window_length", "polyorder", "deriv", "delta", "axis", "mode", "cval"}
    exp_kwargs = {"alpha"}

    def __init__(self, method: Literal["savgol", "exponential", "gaussian"], **kwargs):
        """Class for smoothing 1d array.

        Args:
            method (str): Smoothing method
            **kwargs: Arguments for smoothing methods
        """
        if method not in ["savgol", "exponential", "gaussian"]:
            raise ValueError("Invalid method. Must be one of 'savgol', 'exponential', 'gaussian'")
        self.method = method
        self.kwargs = kwargs

    def __call__(self, x):
        if self.method == "savgol":
            return _smooth_by_savgol_filter(x, **self.kwargs)
        elif self.method == "exponential":
            return _smooth_by_expoential_filter(x, **self.kwargs)
        elif self.method == "gaussian":
            return _smooth_by_gaussian_filter(x, **self.kwargs)
        else:
            raise ValueError(
                f"Invalid smoothing method provided: {self.method}"
                f"If you encounter this error, it is bug. Please report it."
            )


@notice_available_args(exclude=["x"])
def _smooth_by_savgol_filter(x, window_length, polyorder):
    """Smooth a 1d array using scipy.signal.savgol_filter.

    Args:
        x (np.ndarray): 1d array
        window_size (int): Window size
        poly_order (int): Polynomial order

    Returns:
        np.ndarray: Smoothed array
    """
    return savgol_filter(x, window_length, polyorder)


@notice_available_args(exclude=["x"])
def _smooth_by_expoential_filter(x, alpha):
    """Smooth a 1d array using exponential filter.

    Args:
        x (np.ndarray): 1d array
        alpha (float): Smoothing factor

    Returns:
        np.ndarray: Smoothed array
    """
    y = np.zeros_like(x)
    y[0] = x[0]
    for i in range(1, x.shape[0]):
        y[i] = alpha * x[i] + (1 - alpha) * y[i - 1]
    return y


@notice_available_args(exclude=["x"])
def _smooth_by_gaussian_filter(x, sigma, filter_size):
    def gaussian_filter_1d(size, sigma):
        double_pi_sqrt = (np.pi * 2) ** 0.5
        filter_range = np.linspace(-int(size / 2), int(size / 2), size)

        filter_arr = 1
        filter_arr = filter_arr / (sigma * double_pi_sqrt)
        filter_arr = filter_arr * np.exp(-(filter_range**2) / (2 * sigma**2))
        return filter_arr

    filter_arr = gaussian_filter_1d(filter_size, sigma)
    smoothed = np.convolve(x, filter_arr, mode="same")
    return smoothed

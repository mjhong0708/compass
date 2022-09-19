from compass.numeric import interpolate, Smoother
from hypothesis import given
from hypothesis.strategies import integers, floats
import numpy as np
import pytest


@given(integers(2, 10))
def test_interpolate(n):
    x = np.linspace(0, 10, 10)
    y = np.sin(x)
    x_new, y_new = interpolate(x, y, refine_ratio=n)
    assert x_new.shape[0] == 10 * n
    assert y_new.shape[0] == 10 * n


@given(integers(None, 1))
@pytest.mark.xfail(raises=ValueError)
def test_interpolate_invalid_integer_refine_ratio(n):
    x = np.linspace(0, 10, 10)
    y = np.sin(x)
    interpolate(x, y, refine_ratio=n)


@given(floats(None, None))
@pytest.mark.xfail(raises=TypeError)
def test_interpolate_float_refine_ratio(n):
    x = np.linspace(0, 10, 10)
    y = np.sin(x)
    interpolate(x, y, refine_ratio=n)


def test_smoothing():
    x = np.random.normal(0, 1, 101).cumsum()
    x_smooth = Smoother(method="gaussian", sigma=3, filter_size=11)(x)
    assert x_smooth.shape == x.shape

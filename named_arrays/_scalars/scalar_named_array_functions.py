from typing import Callable, TypeVar
import numpy as np
import astropy.units as u
import named_arrays as na

__all__ = [
    "HANDLED_FUNCTIONS",
]

HANDLED_FUNCTIONS = dict()


def _implements(function: Callable):
    """Register a __named_array_function__ implementation for AbstractScalarArray objects."""
    def decorator(func):
        HANDLED_FUNCTIONS[function] = func
        return func
    return decorator


@_implements(na.random.uniform)
def random_uniform(
        start: float | u.Quantity | na.AbstractScalarArray,
        stop: float | u.Quantity | na.AbstractScalarArray,
        shape_random: None | dict[str, int] = None,
        seed: None | int = None,
) -> None | na.ScalarArray:

    if isinstance(start, na.AbstractArray):
        if isinstance(start, na.AbstractScalarArray):
            pass
        else:
            return NotImplemented
    elif start is None:
        return None
    else:
        start = na.ScalarArray(start)

    if isinstance(stop, na.AbstractArray):
        if isinstance(stop, na.AbstractScalarArray):
            pass
        else:
            return NotImplemented
    elif stop is None:
        return None
    else:
        stop = na.ScalarArray(stop)

    shape_random = shape_random if shape_random is not None else dict()
    shape = na.broadcast_shapes(start.shape, stop.shape, shape_random)

    start = start.ndarray_aligned(shape)
    stop = stop.ndarray_aligned(shape)

    if isinstance(start, u.Quantity):
        unit = start.unit
        start = start.value
        if isinstance(stop, u.Quantity):
            stop = stop.to_value(unit)
        else:
            stop = (stop << u.dimensionless_unscaled).to_value(unit)
    else:
        if isinstance(stop, u.Quantity):
            unit = stop.unit
            start = (start << u.dimensionless_unscaled).to_value(unit)
            stop = stop.value
        else:
            unit = None

    if seed is None:
        uniform = np.random.uniform
    else:
        uniform = np.random.default_rng(seed).uniform

    value = uniform(
        low=start,
        high=stop,
        size=tuple(shape.values()),
    )

    if unit is not None:
        value = value << unit

    return na.ScalarArray(
        ndarray=value,
        axes=tuple(shape.keys())
    )

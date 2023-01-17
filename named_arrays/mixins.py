from typing import Sequence
from typing_extensions import Self

import abc
import dataclasses
import copy
import numpy as np
import numpy.typing as npt
import astropy.units as u

__all__ = [
    'NDArrayMethodsMixin'
]


@dataclasses.dataclass(eq=False)
class NDArrayMethodsMixin:

    def broadcast_to(
            self: Self,
            shape: dict[str, int],
    ) -> Self:
        return np.broadcast_to(self, shape=shape)

    def reshape(
            self: Self,
            shape: dict[str, int],
    ) -> Self:
        return np.reshape(self, newshape=shape)

    def min(
            self: Self,
            axis: None | str | Sequence[str] = None,
            initial: npt.ArrayLike = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.min(self, axis=axis, initial=initial, where=where)

    def max(
            self: Self,
            axis: None | str | Sequence[str] = None,
            initial: npt.ArrayLike = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.max(self, axis=axis, initial=initial, where=where)

    def sum(
            self: Self,
            axis: None | str | Sequence[str] = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.sum(self, axis=axis, where=where)

    def ptp(
            self: Self,
            axis: None | str | Sequence[str] = None,
    ) -> Self:
        return np.ptp(self, axis=axis)

    def mean(
            self: Self,
            axis: None | str | Sequence[str] = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.mean(self, axis=axis, where=where)

    def std(
            self: Self,
            axis: None | str | Sequence[str] = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.std(self, axis=axis, where=where)

    def percentile(
            self: Self,
            q: int | float | u.Quantity | Self,
            axis: None | str | Sequence[str] = None,
            out: None | Self = None,
            overwrite_input: bool = False,
            method: str = 'linear',
            keepdims: bool = False,
    ):
        return np.percentile(
            a=self,
            q=q,
            axis=axis,
            out=out,
            overwrite_input=overwrite_input,
            method=method,
            keepdims=keepdims,
        )

    def all(
            self: Self,
            axis: None | str | Sequence[str] = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.all(self, axis=axis, where=where)

    def any(
            self: Self,
            axis: None | str | Sequence[str] = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.any(self, axis=axis, where=where)

    def rms(
            self: Self,
            axis: None | str | Sequence[str] = None,
            where: Self = np._NoValue,
    ) -> Self:
        return np.sqrt(np.mean(np.square(self), axis=axis, where=where))

    def transpose(
            self: Self,
            axes: None | Sequence[str] = None,
    ) -> Self:
        return np.transpose(self, axes=axes)

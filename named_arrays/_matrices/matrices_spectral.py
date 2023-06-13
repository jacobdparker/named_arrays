from __future__ import annotations
from typing import TypeVar, Generic, Type
import abc
import dataclasses
import named_arrays as na

__all__ = [
    'AbstractSpectralMatrixArray',
    'SpectralMatrixArray',
]

WavelengthT = TypeVar('WavelengthT', bound=na.AbstractVectorArray)


@dataclasses.dataclass(eq=False, repr=False)
class AbstractSpectralMatrixArray(
    na.AbstractCartesianMatrixArray,
    na.AbstractSpectralVectorArray,
):
    @property
    @abc.abstractmethod
    def wavelength(self) -> na.AbstractVectorArray:
        """
        The `wavelength` component of the vector.
        """

    @property
    def type_abstract(self) -> Type[AbstractSpectralMatrixArray]:
        return AbstractSpectralMatrixArray

    @property
    def type_explicit(self) -> Type[SpectralMatrixArray]:
        return SpectralMatrixArray

    @property
    def type_vector(self) -> Type[na.SpectralVectorArray]:
        return na.SpectralVectorArray

    @property
    def determinant(self) -> na.ScalarLike:
        # if not self.is_square:
        #     raise ValueError("can only compute determinant of square matrices")
        # xx, xy = self.x.components.values()
        # yx, yy = self.y.components.values()
        # return xx * yy - xy * yx
        return

    @property
    def inverse(self) -> na.AbstractMatrixArray:
        # if not self.is_square:
        #     raise ValueError("can only compute inverse of square matrices")
        # type_matrix = self.x.type_matrix
        # type_row = self.type_vector
        # c1, c2 = self.x.components
        # xx, xy = self.x.components.values()
        # yx, yy = self.y.components.values()
        # result = type_matrix.from_components({
        #     c1: type_row(x=yy, y=-xy),
        #     c2: type_row(x=-yx, y=xx),
        # })
        # result = result / self.determinant
        # return result
        return


@dataclasses.dataclass(eq=False, repr=False)
class SpectralMatrixArray(
    na.SpectralVectorArray,
    AbstractSpectralMatrixArray,
    na.AbstractExplicitMatrixArray,
    Generic[WavelengthT],
):
    pass

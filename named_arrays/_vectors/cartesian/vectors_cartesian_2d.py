from __future__ import annotations
from typing import TypeVar, Type, Generic
import numpy as np
from typing_extensions import Self
import abc
import dataclasses
import astropy.units as u
import named_arrays as na

__all__ = [
    'AbstractCartesian2dVectorArray',
    'Cartesian2dVectorArray',
    'AbstractImplicitCartesian2dVectorArray',
    'AbstractCartesian2dVectorRandomSample',
    'Cartesian2dVectorUniformRandomSample',
    'Cartesian2dVectorNormalRandomSample',
    'AbstractParameterizedCartesian2dVectorArray',
    'Cartesian2dVectorArrayRange',
    'AbstractCartesian2dVectorSpace',
    'Cartesian2dVectorLinearSpace',
    'Cartesian2dVectorStratifiedRandomSpace',
    'Cartesian2dVectorLogarithmicSpace',
    'Cartesian2dVectorGeometricSpace',
]

XT = TypeVar('XT', bound=na.ArrayLike)
YT = TypeVar('YT', bound=na.ArrayLike)


@dataclasses.dataclass(eq=False, repr=False)
class AbstractCartesian2dVectorArray(
    na.AbstractCartesianVectorArray,
):

    @property
    @abc.abstractmethod
    def x(self: Self) -> na.ArrayLike:
        """
        The `x` component of the vector.
        """

    @property
    @abc.abstractmethod
    def y(self: Self) -> na.ArrayLike:
        """
        The `y` component of the vector.
        """

    @property
    def type_abstract(self: Self) -> Type[AbstractCartesian2dVectorArray]:
        return AbstractCartesian2dVectorArray

    @property
    def type_explicit(self: Self) -> Type[Cartesian2dVectorArray]:
        return Cartesian2dVectorArray

    @property
    def type_matrix(self) -> Type[na.Cartesian2dMatrixArray]:
        return na.Cartesian2dMatrixArray


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorArray(
    AbstractCartesian2dVectorArray,
    na.AbstractExplicitCartesianVectorArray,
    Generic[XT, YT],
):
    x: XT = 0
    y: YT = 0

    @classmethod
    def from_scalar(
            cls: Type[Self],
            scalar: na.AbstractScalar,
    ) -> Cartesian2dVectorArray:
        return cls(x=scalar, y=scalar)


@dataclasses.dataclass(eq=False, repr=False)
class AbstractImplicitCartesian2dVectorArray(
    AbstractCartesian2dVectorArray,
    na.AbstractImplicitCartesianVectorArray,
):

    @property
    def x(self) -> na.ArrayLike:
        return self.explicit.x

    @property
    def y(self) -> na.ArrayLike:
        return self.explicit.y


@dataclasses.dataclass(eq=False, repr=False)
class AbstractCartesian2dVectorRandomSample(
    AbstractImplicitCartesian2dVectorArray,
    na.AbstractCartesianVectorRandomSample,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorUniformRandomSample(
    AbstractCartesian2dVectorRandomSample,
    na.AbstractCartesianVectorUniformRandomSample,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorNormalRandomSample(
    AbstractCartesian2dVectorRandomSample,
    na.AbstractCartesianVectorNormalRandomSample,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class AbstractParameterizedCartesian2dVectorArray(
    AbstractImplicitCartesian2dVectorArray,
    na.AbstractParameterizedCartesianVectorArray,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorArrayRange(
    AbstractParameterizedCartesian2dVectorArray,
    na.AbstractCartesianVectorArrayRange,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class AbstractCartesian2dVectorSpace(
    AbstractParameterizedCartesian2dVectorArray,
    na.AbstractCartesianVectorSpace,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorLinearSpace(
    AbstractCartesian2dVectorSpace,
    na.AbstractCartesianVectorLinearSpace,
):
    """
    A :class:`Cartesian2dVectorArray` with attributes :attr:`x` and :attr:`y` that are both instances of :class:`ScalarLinearSpace`.

    :class:`Cartesian2dVectorLinearSpace` can be used to quickly make a uniform 2D linear grid.

    .. jupyter-execute::

        import named_arrays as na

        position = na.Cartesian2dVectorLinearSpace(
            start = -10,
            stop = 10,
            axis = na.Cartesian2dVectorArray(
                x = 'position_x',
                y = 'position_y',
                ),
            num = 21,
            )

        print(position)

    Note above that :class:`Cartesian2dVectorLinearSpace` s are implicitly defined until necessary.

    .. jupyter-execute::

        print(position.explicit)

    It can also be used to create more interesting 2D linear grids with units.

    .. jupyter-execute::

        import astropy.units as u

        spectral_grid = na.Cartesian2dVectorLinearSpace(
            start = na.Cartesian2dVectorArray(
                x = -5 * u.AA,
                y = -10 * u.arcsec,
                ),
            stop = na.Cartesian2dVectorArray(
                x = 5 * u.AA,
                y = 10 * u.arcsec,
                ),
            num = na.Cartesian2dVectorArray(
                x = 10,
                y = 30,
                ),
            axis = na.Cartesian2dVectorArray(
                x = 'wavelength',
                y = 'slit_position',
                ),
            )

        print(spectral_grid.explicit)

    Even one that changes in time.

    .. jupyter-execute::

        spectral_grid = na.Cartesian2dVectorLinearSpace(
            start = na.Cartesian2dVectorArray(
                x = na.ScalarLinearSpace(-5, 5, axis = 'time', num=3) * u.AA,
                y = na.ScalarLinearSpace(-10, 10, axis = 'time', num=3) * u.arcsec,
                ),
            stop = na.Cartesian2dVectorArray(
                x = na.ScalarLinearSpace(5, 15, axis = 'time', num=3) * u.AA,
                y = na.ScalarLinearSpace(10, 30, axis = 'time', num=3) * u.arcsec,
                ),
            num = na.Cartesian2dVectorArray(
                x = 5,
                y = 11,
                ),
            axis = na.Cartesian2dVectorArray(
                x = 'wavelength',
                y = 'slit_position',
                ),
            )

        print(spectral_grid.explicit)

    A similar grid could also be built using math.

    .. jupyter-execute::

        velocity = na.Cartesian2dVectorArray(
            x = 5 * u.m/u.s,
            y = 3 * u.m/u.s,
            )
        time = na.ScalarLinearSpace(0 * u.s, 2 * u.s, axis='time', num=3)
        position = position * u.m + velocity * time
        print(position.explicit)


    """

    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorStratifiedRandomSpace(
    Cartesian2dVectorLinearSpace,
    na.AbstractCartesianVectorStratifiedRandomSpace,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorLogarithmicSpace(
    AbstractCartesian2dVectorSpace,
    na.AbstractCartesianVectorLogarithmicSpace,
):
    pass


@dataclasses.dataclass(eq=False, repr=False)
class Cartesian2dVectorGeometricSpace(
    AbstractCartesian2dVectorSpace,
    na.AbstractCartesianVectorGeometricSpace,
):
    pass

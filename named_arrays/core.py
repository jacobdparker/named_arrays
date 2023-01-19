from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Sequence, Iterator, Union, Type, Callable, Collection, Any
from typing_extensions import Self
if TYPE_CHECKING:
    import named_arrays.scalars
    import named_arrays.vectors
    import named_arrays.matrices

import abc
import dataclasses
import copy
import random
import numpy as np
import numpy.typing as npt
import astropy.units as u

__all__ = [
    'QuantityLike',
    'get_dtype',
    'unit',
    'unit_normalized',
    'type_array',
    'broadcast_shapes',
    'shape_broadcasted',
    'ndindex',
    'indices',
    'flatten_axes',
    'axis_normalized',
    'AbstractArray',
    'ArrayLike',
    'AbstractExplicitArray',
    'AbstractImplicitArray',
    'AbstractRandomMixin',
    'AbstractRangeMixin',
    'AbstractSymmetricRangeMixin',
    'AbstractRandomSample',
    'AbstractParameterizedArray',
    'AbstractLinearParameterizedArrayMixin',
    'AbstractArrayRange',
    'AbstractSpace',
    'AbstractLinearSpace',
    'AbstractStratifiedRandomSpace',
    'AbstractLogarithmicSpace',
    'AbstractGeometricSpace',
    'AbstractUniformRandomSample',
    'AbstractNormalRandomSample',
]

QuantityLike = Union[int, float, complex, np.ndarray, u.Quantity]


def get_dtype(
        value: bool | int | float | complex | str | np.ndarray | AbstractArray,
) -> np.dtype:
    """
    Get the equivalent :attr:`numpy.ndarray.dtype` of the argument.

    If the argument is an instance of :class:`numpy.ndarray`, this function simply returns :attr:`numpy.ndarray.dtype`.
    Otherwise, this function wraps the argument in an :func:`numpy.array()` call and then evaluates the ``dtype``.

    Parameters
    ----------
    value
        Object to find the ``dtype`` of

    Returns
    -------
    ``dtype`` of the argument

    """
    if isinstance(value, (np.ndarray, AbstractArray)):
        return value.dtype
    else:
        return np.array(value).dtype


def unit(
        value: bool | int | float | complex | str | np.ndarray | u.UnitBase | u.Quantity | AbstractArray
) -> None | u.UnitBase:
    if isinstance(value, u.UnitBase):
        return value
    elif isinstance(value, (u.Quantity, AbstractArray)):
        return value.unit
    else:
        return None


def unit_normalized(
        value: bool | int | float | complex | str | np.ndarray | u.Quantity | AbstractArray
) -> u.UnitBase:
    result = unit(value)
    if result is None:
        return u.dimensionless_unscaled
    else:
        return result


def type_array(
        *values: bool | int | float | complex | str | np.ndarray | u.Quantity | AbstractArray,
) -> Type[AbstractExplicitArray]:
    cls = None
    priority_max = 0
    for value in values:
        if isinstance(value, AbstractArray):
            cls_tmp = value.type_array
            priority_tmp = cls_tmp.__named_array_priority__
            if priority_tmp > priority_max:
                priority_max = priority_tmp
                cls = cls_tmp
    return cls


def broadcast_shapes(*shapes: dict[str, int]) -> dict[str, int]:
    result = dict()
    for shape in shapes:
        for axis in reversed(shape):
            if axis in result:
                if result[axis] == shape[axis]:
                    pass
                elif shape[axis] == 1:
                    pass
                elif result[axis] == 1:
                    result[axis] = shape[axis]
                else:
                    raise ValueError(f'shapes {shapes} are not compatible')
            else:
                result[axis] = shape[axis]
    result = {axis: result[axis] for axis in reversed(result)}
    return result


def shape_broadcasted(*arrays: AbstractArray) -> dict[str, int]:
    shapes = [np.shape(array) for array in arrays if isinstance(array, AbstractArray)]
    return broadcast_shapes(*shapes)


def ndindex(
        shape: dict[str, int],
        axis_ignored: None | str | Sequence[str] = None,
) -> Iterator[dict[str, int]]:

    shape = shape.copy()

    if axis_ignored is None:
        axis_ignored = []
    elif isinstance(axis_ignored, str):
        axis_ignored = [axis_ignored]

    for axis in axis_ignored:
        if axis in shape:
            shape.pop(axis)
    shape_tuple = tuple(shape.values())
    for index in np.ndindex(*shape_tuple):
        yield dict(zip(shape.keys(), index))


def indices(shape: dict[str, int]) -> dict[str, named_arrays.scalars.ScalarArrayRange]:
    import named_arrays.scalars
    return {axis: named_arrays.scalars.ScalarArrayRange(0, shape[axis], axis=axis) for axis in shape}


def flatten_axes(axes: Sequence[str]):
    return '*'.join(axes)


def axis_normalized(
        a: AbstractArray,
        axis: None | str | Sequence[str],
) -> tuple[str]:
    """
    Convert all the possible values of the ``axis`` argument to a :class:`tuple` of :class:`str`.

    :param a: If ``axis`` is :class:`None` the result is ``a.axes``.
    :param axis: The ``axis`` value to normalize.
    :return: Normalized ``axis`` parameter.
    """

    if axis is None:
        result = a.axes
    elif isinstance(axis, str):
        result = axis,
    else:
        result = tuple(axis)
    return result


@dataclasses.dataclass(eq=False)
class AbstractArray(
    np.lib.mixins.NDArrayOperatorsMixin,
    abc.ABC,
):
    """
    The ultimate parent class for all array types defined in this package.
    """

    @property
    @abc.abstractmethod
    def __named_array_priority__(self: Self) -> float:
        """
        Attribute used to decide what type of array to return in instances where there is more than one option.

        Similar to :attr:`numpy.class.__array_priority__`

        :return: :type:`int` describing this class's array priority
        """

    @property
    @abc.abstractmethod
    def ndarray(self: Self) -> bool | int | float | complex | str | np.ndarray | u.Quantity:
        """
        Underlying data that is wrapped by this class.

        This is usually an instance of :class:`numpy.ndarray` or :class:`astropy.units.Quantity`, but it can also be a
        built-in python type such as a :class:`int`, :class:`float`, or :class:`bool`
        """

    @property
    @abc.abstractmethod
    def axes(self: Self) -> tuple[str, ...]:
        """
        A :class:`tuple` of :class:`str` representing the names of each dimension of :attr:`ndarray`.

        Must have the same length as the number of dimensions of :attr:`ndarray`.
        """

    @property
    def axes_flattened(self: Self) -> str:
        """
        Combine :attr:`axes` into a single :class:`str`.

        This is useful for functions like :func:`numpy.flatten` which returns an array with only one dimension.
        """
        return flatten_axes(self.axes)

    @property
    @abc.abstractmethod
    def shape(self: Self) -> dict[str, int]:
        """
        Shape of the array. Analogous to :attr:`numpy.ndarray.shape` but represented as a :class:`dict` where the keys
        are the axis names and the values are the axis sizes.
        """

    @property
    @abc.abstractmethod
    def ndim(self: Self) -> int:
        """
        Number of dimensions of the array. Equivalent to :attr:`numpy.ndarray.ndim`.
        """

    @property
    @abc.abstractmethod
    def size(self: Self) -> int:
        """
        Total number of elements in the array. Equivalent to :attr:`numpy.ndarray.size`
        """

    @property
    @abc.abstractmethod
    def dtype(self: Self) -> Type | dict[str, Type]:
        """
        Data type of the array. Equivalent to :attr:`numpy.ndarray.dtype`
        """

    @property
    @abc.abstractmethod
    def unit(self: Self) -> None | u.Unit:
        """
        Unit associated with the array.

        If :attr:`ndarray` is an instance of :class:`astropy.units.Quantity`, return :attr:`astropy.units.Quantity.unit`,
        otherwise return :class:`None`.
        """

    @property
    def unit_normalized(self: Self) -> u.Unit:
        """
        Similar to :attr:`unit` but returns :attr:`astropy.units.dimensionless_unscaled` if :attr:`ndarray` is not an
        instance of :class:`astropy.units.Quantity`.
        """
        return unit_normalized(self)

    @property
    @abc.abstractmethod
    def array(self: Self) -> AbstractExplicitArray:
        """
        Converts this array to an instance of :class:`named_arrays.AbstractExplicitArray`
        """

    @property
    @abc.abstractmethod
    def type_array(self: Self) -> Type[AbstractExplicitArray]:
        """
        The :class:`AbstractExplicitArray` type corresponding to this array
        """

    @property
    @abc.abstractmethod
    def type_array_abstract(self: Self) -> Type[AbstractArray]:
        """
        The :class:`AbstractArray` type corresponding to this array
        """

    @property
    @abc.abstractmethod
    def scalar(self: Self) -> named_arrays.scalars.AbstractScalar:
        """
        Converts this array to an instance of :class:`named_arrays.AbstractScalar`
        """

    @property
    @abc.abstractmethod
    def nominal(self: Self) -> AbstractArray:
        """
        The nominal value of this array.
        """

    @property
    @abc.abstractmethod
    def distribution(self: Self) -> None | AbstractArray:
        """
        The distribution of values of this array.
        """

    @property
    @abc.abstractmethod
    def centers(self: Self) -> AbstractArray:
        """
        The central value for this array. Usually returns this array unless an instance of
        :class:`named_arrays.AbstractStratifiedRandomSpace`
        """

    @abc.abstractmethod
    def astype(
            self: Self,
            dtype: str | np.dtype | Type,
            order: str = 'K',
            casting='unsafe',
            subok: bool = True,
            copy: bool = True,
    ) -> Self:
        """
        Copy of the array cast to a specific data type.

        Equivalent to :meth:`numpy.ndarray.astype`.
        """

    @abc.abstractmethod
    def to(self: Self, unit: u.UnitBase) -> Self:
        """
        Convert this array to a new unit.

        Equivalent to :meth:`astropy.units.Quantity.to`.

        Parameters
        ----------
        unit
            New unit of the returned array

        Returns
        -------
            Array with :attr:`unit` set to the new value
        """

    @property
    @abc.abstractmethod
    def length(self: Self) -> named_arrays.scalars.AbstractScalar:
        """
        L2-norm of this array.
        """

    @property
    def indices(self: Self) -> dict[str, named_arrays.scalars.ScalarArrayRange]:
        return indices(self.shape)

    def ndindex(
            self: Self,
            axis_ignored: None | str | Sequence[str] = None,
    ) -> Iterator[dict[str, int]]:
        return ndindex(
            shape=self.shape,
            axis_ignored=axis_ignored,
        )

    @abc.abstractmethod
    def add_axes(self: Self, axes: str | Sequence[str]) -> AbstractExplicitArray:
        """
        Add new singleton axes to this array

        Parameters
        ----------
        axes
            New axes to add to the array

        Returns
        -------
        Array with new axes added
        """

    @abc.abstractmethod
    def combine_axes(
            self: Self,
            axes: Sequence[str],
            axis_new: None | str,
    ) -> AbstractExplicitArray:
        """
        Combine some of the axes of the array into a single new axis.

        Parameters
        ----------
        axes
            The axes to combine into a new axis
        axis_new
            The name of the new axis

        Returns
        -------
        Array with the specified axes combined
        """

    def copy_shallow(self: Self) -> Self:
        return copy.copy(self)

    def copy(self: Self) -> Self:
        return copy.deepcopy(self)

    def __copy__(self: Self) -> Self:
        fields = {field.name: getattr(self, field.name) for field in dataclasses.fields(self)}
        return type(self)(**fields)

    def __deepcopy__(self: Self, memodict={}) -> Self:
        fields = {field.name: copy.deepcopy(getattr(self, field.name)) for field in dataclasses.fields(self)}
        return type(self)(**fields)

    @abc.abstractmethod
    def _getitem(
            self: Self,
            item: dict[str, int | slice | AbstractArray] | AbstractArray,
    ):
        pass

    @abc.abstractmethod
    def _getitem_reversed(
            self: Self,
            array: AbstractArray,
            item: dict[str, int | slice | AbstractArray] | AbstractArray
    ):
        pass

    def __getitem__(
            self: Self,
            item: dict[str, int | slice | AbstractArray] | AbstractArray,
    ) -> AbstractExplicitArray:
        result = self._getitem(item)
        if result is not NotImplemented:
            return result

        else:
            if isinstance(item, dict):
                for ax in item:
                    if isinstance(item[ax], AbstractArray):
                        result = item[ax]._getitem_reversed(self, item)
                        if result is not NotImplemented:
                            return result

            elif isinstance(item, AbstractArray):
                result = item._getitem_reversed(self, item)
                if result is not NotImplemented:
                    return result

        raise ValueError(f"item not supported by array with type {type(self)}")

    @abc.abstractmethod
    def __bool__(self: Self) -> bool:
        return True

    @abc.abstractmethod
    def __mul__(self: Self, other: ArrayLike | u.Unit) -> AbstractExplicitArray:
        return super().__mul__(other)

    @abc.abstractmethod
    def __lshift__(self: Self, other: ArrayLike | u.UnitBase) -> AbstractExplicitArray:
        return super().__lshift__(other)

    @abc.abstractmethod
    def __truediv__(self: Self, other: ArrayLike | u.UnitBase) -> AbstractExplicitArray:
        return super().__truediv__(other)

    @abc.abstractmethod
    def __array_ufunc__(
            self,
            function: np.ufunc,
            method: str,
            *inputs,
            **kwargs,
    ) -> None | AbstractArray | tuple[AbstractArray, ...]:
        """
        Method to override the behavior of numpy's ufuncs.
        """

    @abc.abstractmethod
    def __array_function__(
            self: Self,
            func: Callable,
            types: Collection,
            args: tuple,
            kwargs: dict[str, Any],
    ):
        """
        Method to override the behavior of numpy's array functions.
        """
        from . import _core_array_functions

        if func in _core_array_functions.HANDLED_FUNCTIONS:
            return _core_array_functions.HANDLED_FUNCTIONS[func](*args, **kwargs)

        return NotImplemented

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

    def _interp_linear_recursive(
            self: Self,
            item: dict[str, Self],
            item_base: dict[str, Self],
    ):
        item = item.copy()

        if not item:
            raise ValueError('Item must contain at least one key')

        axis = next(iter(item))
        x = item.pop(axis)

        if x.shape:
            where_below = x < 0
            where_above = (self.shape[axis] - 1) <= x

            x0 = np.floor(x).astype(int)
            x0[where_below] = 0
            x0[where_above] = self.shape[axis] - 2

        else:
            if x < 0:
                x0 = 0
            elif x >= self.shape[axis] - 1:
                x0 = self.shape[axis] - 2
            else:
                x0 = int(x)

        x1 = x0 + 1

        item_base_0 = {**item_base, axis: x0}
        item_base_1 = {**item_base, axis: x1}

        if item:
            y0 = self._interp_linear_recursive(item=item, item_base=item_base_0, )
            y1 = self._interp_linear_recursive(item=item, item_base=item_base_1, )
        else:
            y0 = self[item_base_0]
            y1 = self[item_base_1]

        result = y0 + (x - x0) * (y1 - y0)
        return result

    def interp_linear(
            self: Self,
            item: dict[str, Self],
    ) -> Self:
        return self._interp_linear_recursive(
            item=item,
            item_base=self[{ax: 0 for ax in item}].indices,
        )

    def __call__(self: Self, item: dict[str, Self]) -> Self:
        return self.interp_linear(item=item)

    def index_secant(
            self: Self,
            value: Self,
            axis: None | str | Sequence[str] = None,
    ) -> dict[str, Self]:

        import named_arrays.scalars
        import named_arrays.vectors
        import named_arrays.optimization

        if axis is None:
            axis = list(self.shape.keys())
        elif isinstance(axis, str):
            axis = [axis, ]

        shape = self.shape
        shape_nearest = named_arrays.vectors.CartesianND({ax: shape[ax] for ax in axis})

        if isinstance(self, named_arrays.vectors.VectorInterface):
            coordinates = self.coordinates
            coordinates = {comp: None if value.coordinates[comp] is None else coordinates[comp] for comp in coordinates}
            self_subspace = type(self).from_coordinates(coordinates)
        else:
            self_subspace = self

        def indices_factory(index: named_arrays.vectors.CartesianND) -> dict[str, named_arrays.scalars.Scalar]:
            return index.coordinates

        def get_index(index: named_arrays.vectors.CartesianND) -> named_arrays.vectors.CartesianND:
            index = indices_factory(index)
            print(self_subspace)
            value_new = self_subspace(index)
            diff = value_new - value
            if isinstance(diff, named_arrays.vectors.AbstractVector):
                diff = named_arrays.vectors.CartesianND({c: diff.coordinates[c] for c in diff.coordinates if diff.coordinates[c] is not None})
            return diff

        result = named_arrays.optimization.root_finding.secant(
            func=get_index,
            root_guess=shape_nearest // 2,
            step_size=named_arrays.vectors.CartesianND({ax: 1e-6 for ax in axis}),
        )

        return indices_factory(result)

    def index(
            self: Self,
            value: Self,
            axis: None | str | Sequence[str] = None,
    ) -> dict[str, Self]:
        return self.index_secant(value=value, axis=axis)


ArrayLike = Union[QuantityLike, AbstractArray]


@dataclasses.dataclass(eq=False)
class AbstractExplicitArray(
    AbstractArray,
):
    @classmethod
    @abc.abstractmethod
    def empty(cls: Type[Self], shape: dict[str, int], dtype: Type = float) -> Self:
        """
        Create a new empty array

        Parameters
        ----------
        shape
            shape of the new array
        dtype
            data type of the new array

        Returns
        -------
            A new empty array with the specified shape and data type
        """

    @classmethod
    @abc.abstractmethod
    def zeros(cls: Type[Self], shape: dict[str, int], dtype: Type = float) -> Self:
        """
        Create a new array of zeros

        Parameters
        ----------
        shape
            shape of the new array
        dtype
            data type of the new array

        Returns
        -------
            A new array of zeros with the specified shape and data type
        """

    @classmethod
    @abc.abstractmethod
    def ones(cls: Type[Self], shape: dict[str, int], dtype: Type = float) -> Self:
        """
        Create a new array of ones

        Parameters
        ----------
        shape
            shape of the new array
        dtype
            data type of the new array

        Returns
        -------
            A new array of ones with the specified shape and data type
        """

    @property
    def unit(self: Self) -> None | u.Unit:
        if isinstance(self.ndarray, (u.Quantity, AbstractArray)):
            return self.ndarray.unit
        else:
            return None


@dataclasses.dataclass(eq=False)
class AbstractImplicitArray(
    AbstractArray,
):
    @property
    def axes(self: Self) -> tuple[str, ...]:
        return self.array.axes

    @property
    def dtype(self: Self) -> npt.DTypeLike:
        return self.array.dtype

    @property
    def ndarray(self: Self) -> QuantityLike:
        return self.array.ndarray

    @property
    def ndim(self: Self) -> int:
        return self.array.ndim

    @property
    def size(self: Self) -> int:
        return self.array.size

    @property
    def shape(self: Self) -> dict[str, int]:
        return self.array.shape

    @property
    def unit(self: Self) -> float | u.Unit:
        return self.array.unit


@dataclasses.dataclass(eq=False)
class AbstractRandomMixin(
    abc.ABC,
):

    def __post_init__(self):
        if self.seed is None:
            self.seed = random.randint(0, 10 ** 12)

    @property
    @abc.abstractmethod
    def seed(self: Self) -> int:
        """
        Seed for the random number generator instance
        """

    @seed.setter
    @abc.abstractmethod
    def seed(self: Self, value: int) -> None:
        pass

    @property
    def _rng(self: Self) -> np.random.Generator:
        return np.random.default_rng(seed=self.seed)


@dataclasses.dataclass(eq=False)
class AbstractRangeMixin(
    abc.ABC,
):

    @property
    @abc.abstractmethod
    def start(self: Self) -> int | AbstractArray:
        """
        Starting value of the range.
        """

    @property
    @abc.abstractmethod
    def stop(self: Self) -> int | AbstractArray:
        """
        Ending value of the range.
        """

    @property
    def range(self: Self) -> AbstractArray:
        return self.stop - self.start


@dataclasses.dataclass(eq=False)
class AbstractSymmetricRangeMixin(
    AbstractRangeMixin,
):
    @property
    @abc.abstractmethod
    def center(self: Self) -> ArrayLike:
        """
        Center value of the range.
        """

    @property
    @abc.abstractmethod
    def width(self: Self) -> ArrayLike:
        """
        Width of the range.
        """

    @property
    def start(self: Self) -> ArrayLike:
        return self.center - self.width

    @property
    def stop(self: Self) -> ArrayLike:
        return self.center + self.width


@dataclasses.dataclass(eq=False)
class AbstractRandomSample(
    AbstractRandomMixin,
    AbstractImplicitArray,
):

    @property
    @abc.abstractmethod
    def shape_random(self: Self) -> None | dict[str, int]:
        """
        Dimensions along which the resulting random sample is completely uncorrelated.
        """


@dataclasses.dataclass(eq=False)
class AbstractUniformRandomSample(
    AbstractRangeMixin,
    AbstractRandomSample,
):
    pass


@dataclasses.dataclass
class AbstractNormalRandomSample(
    AbstractSymmetricRangeMixin,
    AbstractRandomSample,
):
    pass


@dataclasses.dataclass(eq=False)
class AbstractParameterizedArray(
    AbstractImplicitArray,
):

    @property
    @abc.abstractmethod
    def axis(self: Self) -> str | AbstractArray:
        """
        The axis along which the array is parameterized
        """

    @property
    @abc.abstractmethod
    def num(self: Self) -> int | AbstractArray:
        """
        Number of elements in the parameterization
        """


@dataclasses.dataclass(eq=False)
class AbstractLinearParameterizedArrayMixin(
    abc.ABC
):
    @property
    @abc.abstractmethod
    def step(self: Self) -> int | AbstractArray:
        """
        Spacing between the values.
        """


@dataclasses.dataclass(eq=False)
class AbstractArrayRange(
    AbstractLinearParameterizedArrayMixin,
    AbstractRangeMixin,
    AbstractParameterizedArray,
):
    pass


@dataclasses.dataclass(eq=False)
class AbstractSpace(
    AbstractParameterizedArray,
):
    @property
    @abc.abstractmethod
    def endpoint(self: Self) -> bool:
        """
        If ``True``, :attr:`stop` is the last sample, otherwise it is not included.
        """


@dataclasses.dataclass(eq=False)
class AbstractLinearSpace(
    AbstractLinearParameterizedArrayMixin,
    AbstractRangeMixin,
    AbstractSpace
):

    @property
    def step(self: Self) -> AbstractArray:
        if self.endpoint:
            return self.range / (self.num - 1)
        else:
            return self.range / self.num


@dataclasses.dataclass(eq=False)
class AbstractStratifiedRandomSpace(
    AbstractRandomMixin,
    AbstractLinearSpace,
):
    pass


@dataclasses.dataclass(eq=False)
class AbstractLogarithmicSpace(
    AbstractRangeMixin,
    AbstractSpace,
):

    @property
    @abc.abstractmethod
    def start_exponent(self: Self) -> ArrayLike:
        """
        Exponent of the starting value of the sequence.
        """

    @property
    @abc.abstractmethod
    def stop_exponent(self: Self) -> ArrayLike:
        """
        Exponent of the ending value of the sequence.
        """

    @property
    @abc.abstractmethod
    def base(self: Self) -> ArrayLike:
        """
        Base which is exponentiated by :attr:`start_exponent` and :attr:`stop_exponent`.
        """

    @property
    def start(self: Self) -> ArrayLike:
        return self.base ** self.start_exponent

    @property
    def stop(self: Self) -> ArrayLike:
        return self.base ** self.stop_exponent


@dataclasses.dataclass(eq=False)
class AbstractGeometricSpace(
    AbstractRangeMixin,
    AbstractSpace,
):
    pass

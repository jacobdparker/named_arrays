from __future__ import annotations
import matplotlib.axes
import matplotlib.artist
import matplotlib.pyplot as plt
import numpy.typing as npt
import named_arrays as na

__all__ = [
    "subplots",
    "plot",
]


def subplots(
        axis_rows: None | str = None,
        ncols: int = 1,
        axis_cols: None | str = None,
        nrows: int = 1,
        *,
        sharex: bool | str = False,
        sharey: bool | str = False,
        squeeze: bool = True,
        **kwargs,
) -> tuple[plt.Figure, na.ScalarArray[npt.NDArray[matplotlib.axes.Axes]]]:
    """
    A thin wrapper around :func:`matplotlib.pyplot.subplots()` which allows for
    providing axis names to the rows and columns.

    Parameters
    ----------
    axis_rows
        Name of the axis representing the rows in the subplot grid.
        If :obj:`None`, the ``squeeze`` argument must be :class:`True`.
    nrows
        Number of rows in the subplot grid
    axis_cols
        Name of the axis representing the columns in the subplot grid
        If :obj:`None`, the ``squeeze`` argument must be :obj:`True`.
    ncols
        Number of columns in the subplot grid
    sharex
        Controls whether all the :class:`matplotlib.axes.Axes` instances share the same horizontal axis properties.
        See the documentation of :func:`matplotlib.pyplot.subplots` for more information.
    sharey
        Controls whether all the :class`matplotlib.axes.Axes` instances share the same vertical axis properties.
        See the documentation of :func:`matplotlib.pyplot.subplots` for more information.
    squeeze
        If :obj:`True`, :func:`numpy.squeeze` is called on the result, which removes singleton dimensions from the
        array.
        See the documentation of :func:`matplotlib.pyplot.subplots` for more information.
    kwargs
        Additional keyword arguments passed to :func:`matplotlib.pyplot.subplots`
    """

    axes = (axis_rows, axis_cols)
    axes = tuple(axis for axis in axes if axis is not None)

    fig, axs = plt.subplots(
        ncols=ncols,
        nrows=nrows,
        sharex=sharex,
        sharey=sharey,
        squeeze=squeeze,
        **kwargs,
    )

    return fig, na.ScalarArray(axs, axes)


def plot(
        *args: na.AbstractScalar,
        ax: None | matplotlib.axes.Axes | na.ScalarArray[npt.NDArray[matplotlib.axes.Axes]] = None,
        axis: None | str = None,
        where: bool | na.AbstractScalar = True,
        **kwargs,
) -> na.ScalarArray[npt.NDArray[None | matplotlib.artist.Artist]]:
    """
    A thin wrapper around :meth:`matplotlib.axes.Axes.plot` for named arrays.

    The main difference of this function from :func:`matplotlib.pyplot.plot` is the addition of the ``axis`` parameter
    indicating along which axis the lines should be connected.

    Parameters
    ----------
    args
        either ``x, y`` or ``y``, same as :meth:`matplotlib.axes.Axes.plot`
    ax
        The instances of :class:`matplotlib.axes.Axes` to use.
        If :obj:`None`, calls :func:`matplotlib.pyplot.gca` to get the current axes.
        If an instance of :class:`named_arrays.ScalarArray`, ``ax.shape`` should be a subset of the broadcasted shape of
        ``*args``.
    axis
        The name of the axis that the plot lines should be connected along.
        If :obj:`None`, the broadcasted shape of ``args`` should have only one element,
        otherwise a :class:`ValueError` is raised.
    where
        A boolean array that selects which elements to plot
    kwargs
        Additional keyword arguments passed to :meth:`matplotlib.axes.Axes.plot`.
        These can be instances of :class:`named_arrays.AbstractArray`.

    Returns
    -------
        An array of artists that were plotted

    Examples
    --------

    Plot a single scalar

    .. jupyter-execute::

        import numpy as np
        import matplotlib.pyplot as plt
        import named_arrays as na

        x = na.linspace(0, 2 * np.pi, axis="x",  num=101)
        y = np.sin(x)

        plt.figure();
        na.plt.plot(x, y);

    Plot an array of scalars

    .. jupyter-execute::

        z = na.linspace(0, np.pi, axis="z", num=5)

        y = np.sin(x - z)

        plt.figure();
        na.plt.plot(x, y, axis="x");

    Plot an uncertain scalar

    .. jupyter-execute::

        ux = na.NormalUncertainScalarArray(x, width=0.2)
        uy = np.sin(ux)

        plt.figure();
        na.plt.plot(x, uy);

    Broadcast an array of scalars against an array of :class:`matplotlib.axes.Axes`

    .. jupyter-execute::

        fig, ax = na.plt.subplots(axis_rows="z", nrows=z.shape["z"], sharex=True)

        na.plt.plot(x, y, ax=ax, axis="x");

    """
    return na._named_array_function(
        plot,
        *args,
        ax=ax,
        axis=axis,
        where=where,
        **kwargs,
    )

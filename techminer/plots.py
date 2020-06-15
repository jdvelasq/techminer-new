"""
Plots
==================================================================================================




"""
import json
import textwrap
from os.path import dirname, join

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import squarify
from techminer.chord_diagram import ChordDiagram
from wordcloud import ImageColorGenerator, WordCloud

FONT_SIZE = 13

TEXTLEN = 40

COLORMAPS = [
    "Greys",
    "Purples",
    "Blues",
    "Greens",
    "Oranges",
    "Reds",
    "ocean",
    "gnuplot",
    "gnuplot2",
    "YlOrBr",
    "YlOrRd",
    "OrRd",
    "PuRd",
    "RdPu",
    "BuPu",
    "GnBu",
    "PuBu",
    "YlGnBu",
    "PuBuGn",
    "BuGn",
    "YlGn",
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "binary",
    "gist_yarg",
    "gist_gray",
    "gray",
    "bone",
    "pink",
    "spring",
    "summer",
    "autumn",
    "winter",
    "cool",
    "Wistia",
    "hot",
    "afmhot",
    "gist_heat",
    "copper",
    "PiYG",
    "PRGn",
    "BrBG",
    "PuOr",
    "RdGy",
    "RdBu",
    "RdYlBu",
    "RdYlGn",
    "Spectral",
    "coolwarm",
    "bwr",
    "seismic",
    "twilight",
    "twilight_shifted",
    "hsv",
    "Pastel1",
    "Pastel2",
    "Paired",
    "Accent",
    "Dark2",
    "Set1",
    "Set2",
    "Set3",
    "tab10",
    "tab20",
    "tab20b",
    "tab20c",
    "flag",
    "prism",
    "gist_earth",
    "terrain",
    "gist_stern",
    "CMRmap",
    "cubehelix",
    "brg",
    "gist_rainbow",
    "rainbow",
    "jet",
    "nipy_spectral",
    "gist_ncar",
]

STYLE = [
    "default",
    "classic",
    "Solarize_Light2",
    "_classic_test_patch",
    "bmh",
    "dark_background",
    "fast",
    "fivethirtyeight",
    "ggplot",
    "grayscale",
    "seaborn",
    "seaborn-bright",
    "seaborn-colorblind",
    "seaborn-dark",
    "seaborn-dark-palette",
    "seaborn-darkgrid",
    "seaborn-deep",
    "seaborn-muted",
    "seaborn-notebook",
    "seaborn-paper",
    "seaborn-pastel",
    "seaborn-poster",
    "seaborn-talk",
    "seaborn-ticks",
    "seaborn-white",
    "seaborn-whitegrid",
    "tableau-colorblind10",
]


def bar(
    x, width=0.8, bottom=None, align="center", cmap="Greys", figsize=(10, 6), **kwargs
):
    """Creates a bar plot from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 3,author 1,author 0,author 2".split(","),
    ...         "Num_Documents": [3, 2, 2, 1],
    ...         "ID": list(range(4)),
    ...     }
    ... )
    >>> df
        Authors  Num_Documents  ID
    0  author 3              3   0
    1  author 1              2   1
    2  author 0              2   2
    3  author 2              1   3
    >>> fig = bar(df, cmap=plt.cm.Blues)
    >>> fig.savefig('sphinx/images/barplot.png')

    .. image:: images/barplot.png
        :width: 400px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")

    if cmap is not None:
        cmap = plt.cm.get_cmap(cmap)
        kwargs["color"] = [
            cmap(
                (
                    0.2
                    + 0.75
                    * (x[x.columns[1]][i] - min(x[x.columns[1]]))
                    / (max(x[x.columns[1]]) - min(x[x.columns[1]]))
                )
            )
            for i in range(len(x[x.columns[1]]))
        ]

    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()

    ax.bar(
        x=range(len(x)),
        height=x[x.columns[1]],
        width=width,
        bottom=bottom,
        align=align,
        **({}),
        **kwargs,
    )

    if x[x.columns[0]].dtype != "int64":
        xticklabels = [
            textwrap.shorten(text=text, width=TEXTLEN) for text in x[x.columns[0]]
        ]
    else:
        xticklabels = x[x.columns[0]]

    ax.set_xticks(np.arange(len(x[x.columns[0]])))
    ax.set_xticklabels(xticklabels)
    ax.tick_params(axis="x", labelrotation=90)

    ax.set_xlabel(x.columns[0])
    ax.set_ylabel(x.columns[1])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.grid(axis="y", color="gray", linestyle=":")

    return fig


def barh(x, height=0.8, left=None, figsize=(8, 5), align="center", cmap=None, **kwargs):
    """Make a pie chart from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> x = pd.DataFrame(
    ...     {
    ...         "Authors": "author 3,author 1,author 0,author 2".split(","),
    ...         "Num_Documents": [3, 2, 2, 1],
    ...         "ID": list(range(4)),
    ...     }
    ... )
    >>> x
        Authors  Num_Documents  ID
    0  author 3              3   0
    1  author 1              2   1
    2  author 0              2   2
    3  author 2              1   3
    >>> fig = barh(x, cmap='Blues')
    >>> fig.savefig('sphinx/images/barhplot.png')

    .. image:: images/barhplot.png
        :width: 400px
        :align: center

    """
    matplotlib.rc("font", size=FONT_SIZE)

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")

    if cmap is not None:
        cmap = plt.cm.get_cmap(cmap)
        kwargs["color"] = [
            cmap(
                (
                    0.2
                    + 0.75
                    * (x[x.columns[1]][i] - min(x[x.columns[1]]))
                    / (max(x[x.columns[1]]) - min(x[x.columns[1]]))
                )
            )
            for i in range(len(x))
        ]

    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()

    ax.barh(
        y=range(len(x)),
        width=x[x.columns[1]],
        height=height,
        left=left,
        align=align,
        **kwargs,
    )

    ax.invert_yaxis()
    ax.set_yticks(np.arange(len(x[x.columns[0]])))
    ax.set_yticklabels(x[x.columns[0]])
    ax.set_xlabel(x.columns[1])
    ax.set_ylabel(x.columns[0])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(False)

    ax.grid(axis="x", color="gray", linestyle=":")

    return fig


def bubble(
    x,
    axis=0,
    rmax=80,
    figsize=(9, 9),
    cmap="Blues",
    grid_lw=1.0,
    grid_c="gray",
    grid_ls=":",
    **kwargs
):

    """Creates a gant activity plot from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "author 0": [ 1, 2, 3, 4, 5, 6, 7],
    ...         "author 1": [14, 13, 12, 11, 10, 9, 8],
    ...         "author 2": [1, 5, 8, 9, 0, 0, 0],
    ...         "author 3": [0, 0, 1, 1, 1, 0, 0],
    ...         "author 4": [0, 10, 0, 4, 2, 0, 1],
    ...     },
    ...     index =[2010, 2011, 2012, 2013, 2014, 2015, 2016]
    ... )
    >>> df
          author 0  author 1  author 2  author 3  author 4
    2010         1        14         1         0         0
    2011         2        13         5         0        10
    2012         3        12         8         1         0
    2013         4        11         9         1         4
    2014         5        10         0         1         2
    2015         6         9         0         0         0
    2016         7         8         0         0         1

    >>> fig = bubble(df, axis=0, alpha=0.5, rmax=150)
    >>> fig.savefig('sphinx/images/bubbleplot0.png')

    .. image:: images/bubbleplot0.png
        :width: 400px
        :align: center

    >>> fig = bubble(df, axis=1, alpha=0.5, rmax=150)
    >>> fig.savefig('sphinx/images/bubbleplot1.png')

    .. image:: images/bubbleplot1.png
        :width: 400px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    if axis == "index":
        axis = 0
    if axis == "columns":
        axis = 1

    x = x.copy()
    vmax = x.max().max()
    vmin = x.min().min()

    rmin = 0

    if axis == 0:
        for idx, row in enumerate(x.iterrows()):
            values = [
                10 * (rmin + (rmax - rmin) * w / (vmax - vmin)) for w in row[1].tolist()
            ]
            ax.scatter(
                range(len(x.columns)),
                [idx] * len(x.columns),
                marker="o",
                s=values,
                **kwargs,
            )

    else:
        for idx, col in enumerate(x.columns):
            values = [10 * (rmin + (rmax - rmin) * w / (vmax - vmin)) for w in x[col]]
            ax.scatter(
                [idx] * len(x.index),
                range(len(x.index)),
                marker="o",
                s=values,
                **kwargs,
            )

    for idx, row in enumerate(x.iterrows()):
        ax.hlines(
            idx, -1, len(x.columns), linewidth=grid_lw, color=grid_c, linestyle=grid_ls,
        )

    for idx, col in enumerate(x.columns):
        ax.vlines(
            idx, -1, len(x.index), linewidth=grid_lw, color=grid_c, linestyle=grid_ls,
        )

    for idx_col, col in enumerate(x.columns):
        for idx_row, row in enumerate(x.index):

            if x[col][row] != 0:
                ax.text(idx_col, idx_row, x[col][row], va="center", ha="center")

    ax.set_aspect("equal")

    ax.set_xlim(-1, len(x.columns))
    ax.set_ylim(-1, len(x.index) + 1)

    ax.set_xticks(np.arange(len(x.columns)))
    ax.set_xticklabels(x.columns)
    ax.tick_params(axis="x", labelrotation=90)
    ax.xaxis.tick_top()

    ax.invert_yaxis()
    ax.set_yticks(np.arange(len(x.index)))
    ax.set_yticklabels(x.index)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    return fig


def plot(x, *args, figsize=(9, 9), cmap="Blues", scalex=True, scaley=True, **kwargs):
    """Creates a plot from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "author 0": [ 1, 2, 3, 4, 5, 6, 7],
    ...         "author 1": [14, 13, 12, 11, 10, 9, 8],
    ...         "author 2": [1, 5, 8, 9, 0, 0, 0],
    ...         "author 3": [0, 0, 1, 1, 1, 0, 0],
    ...         "author 4": [0, 10, 0, 4, 2, 0, 1],
    ...     },
    ...     index =[2010, 2011, 2012, 2013, 2014, 2015, 2016]
    ... )
    >>> df
          author 0  author 1  author 2  author 3  author 4
    2010         1        14         1         0         0
    2011         2        13         5         0        10
    2012         3        12         8         1         0
    2013         4        11         9         1         4
    2014         5        10         0         1         2
    2015         6         9         0         0         0
    2016         7         8         0         0         1
    >>> fig = plot(df)
    >>> fig.savefig('sphinx/images/plotplot.png')

    .. image:: images/plotplot.png
        :width: 400px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")
        ax.plot(
            range(len(x)),
            x[x.columns[1]],
            *args,
            scalex=scalex,
            scaley=scaley,
            **kwargs,
        )
        plt.xticks(
            np.arange(len(x[x.columns[0]])), x[x.columns[0]], rotation="vertical"
        )
        ax.set_xlabel(x.columns[0])
        ax.set_ylabel(x.columns[1])
    else:
        for col in x.columns:
            ax.plot(x.index, x[col], label=col, **kwargs)
        ax.legend()

    ax.set_xticks(x.index)
    ax.set_xticklabels(x.index)
    ax.tick_params(axis="x", labelrotation=90)
    # ax.xaxis.tick_top()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)

    return fig


def pie(
    x,
    figsize=(8, 8),
    cmap="Greys",
    explode=None,
    autopct=None,
    pctdistance=0.6,
    shadow=False,
    labeldistance=1.1,
    startangle=None,
    radius=None,
    counterclock=True,
    wedgeprops=None,
    textprops=None,
    center=(0, 0),
    frame=False,
    rotatelabels=False,
):
    """Creates a pie plot from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 3,author 1,author 0,author 2".split(","),
    ...         "Num_Documents": [3, 2, 2, 1],
    ...         "ID": list(range(4)),
    ...     }
    ... )
    >>> df
        Authors  Num_Documents  ID
    0  author 3              3   0
    1  author 1              2   1
    2  author 0              2   2
    3  author 2              1   3
    >>> fig = pie(df, cmap="Blues")
    >>> fig.savefig('sphinx/images/pieplot.png')

    .. image:: images/pieplot.png
        :width: 400px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")
    colors = None
    if cmap is not None:
        colors = [cmap(1.0 - 0.9 * (i / len(x))) for i in range(len(x[x.columns[1]]))]
    ax.pie(
        x=x[x.columns[1]],
        explode=explode,
        labels=x[x.columns[0]],
        colors=colors,
        autopct=autopct,
        pctdistance=pctdistance,
        shadow=shadow,
        labeldistance=labeldistance,
        startangle=startangle,
        radius=radius,
        counterclock=counterclock,
        wedgeprops=wedgeprops,
        textprops=textprops,
        center=center,
        frame=frame,
        rotatelabels=rotatelabels,
    )
    return fig


def wordcloud(
    x,
    figsize=(8, 8),
    font_path=None,
    width=400,
    height=200,
    margin=2,
    ranks_only=None,
    prefer_horizontal=0.9,
    mask=None,
    scale=1,
    color_func=None,
    max_words=200,
    min_font_size=4,
    stopwords=None,
    random_state=None,
    background_color="white",
    max_font_size=None,
    font_step=1,
    mode="RGB",
    relative_scaling="auto",
    regexp=None,
    collocations=True,
    cmap="Blues",
    normalize_plurals=True,
    contour_width=0,
    contour_color="black",
    repeat=False,
    include_numbers=False,
    min_word_length=0,
):
    """Plots a wordcloud from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 3,author 1,author 0,author 2".split(","),
    ...         "Num_Documents": [10, 5, 2, 1],
    ...         "ID": list(range(4)),
    ...     }
    ... )
    >>> df
        Authors  Num_Documents  ID
    0  author 3             10   0
    1  author 1              5   1
    2  author 0              2   2
    3  author 2              1   3
    >>> fig = wordcloud(df)
    >>> fig.savefig('sphinx/images/wordcloud.png')

    .. image:: images/wordcloud.png
        :width: 400px
        :align: center

    """
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")
    words = {row[0]: row[1] for _, row in x.iterrows()}
    wordcloud = WordCloud(
        font_path=font_path,
        width=width,
        height=height,
        margin=margin,
        ranks_only=ranks_only,
        prefer_horizontal=prefer_horizontal,
        mask=mask,
        scale=scale,
        color_func=color_func,
        max_words=max_words,
        min_font_size=min_font_size,
        stopwords=stopwords,
        random_state=random_state,
        background_color=background_color,
        max_font_size=max_font_size,
        font_step=font_step,
        mode=mode,
        relative_scaling=relative_scaling,
        regexp=regexp,
        collocations=collocations,
        colormap=cmap,
        normalize_plurals=normalize_plurals,
        contour_width=contour_width,
        contour_color=contour_color,
        repeat=repeat,
        include_numbers=include_numbers,
        min_word_length=min_word_length,
    )
    wordcloud.generate_from_frequencies(words)
    ax.imshow(wordcloud, interpolation="bilinear")
    #
    ax.spines["bottom"].set_color("lightgray")
    ax.spines["top"].set_color("lightgray")
    ax.spines["right"].set_color("lightgray")
    ax.spines["left"].set_color("lightgray")
    ax.set_xticks([])
    ax.set_yticks([])
    #
    return fig


def gant(x, figsize=(8, 8), grid_lw=1.0, grid_c="gray", grid_ls=":", *args, **kwargs):
    """Creates a gant activity plot from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "author 0": [1, 1, 0, 0, 0, 0, 0],
    ...         "author 1": [0, 1, 1, 0, 0, 0, 0],
    ...         "author 2": [1, 0, 0, 0, 0, 0, 0],
    ...         "author 3": [0, 0, 1, 1, 1, 0, 0],
    ...         "author 4": [0, 0, 0, 0, 0, 0, 1],
    ...     },
    ...     index =[2010, 2011, 2012, 2013, 2014, 2015, 2016]
    ... )
    >>> df
          author 0  author 1  author 2  author 3  author 4
    2010         1         0         1         0         0
    2011         1         1         0         0         0
    2012         0         1         0         1         0
    2013         0         0         0         1         0
    2014         0         0         0         1         0
    2015         0         0         0         0         0
    2016         0         0         0         0         1

    >>> fig = gant(df)
    >>> fig.savefig('sphinx/images/gantplot.png')

    .. image:: images/gantplot.png
        :width: 400px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()

    x = x.copy()
    if "linewidth" not in kwargs.keys() and "lw" not in kwargs.keys():
        kwargs["linewidth"] = 4
    if "marker" not in kwargs.keys():
        kwargs["marker"] = "o"
    if "markersize" not in kwargs.keys() and "ms" not in kwargs.keys():
        kwargs["markersize"] = 8
    if "color" not in kwargs.keys() and "c" not in kwargs.keys():
        kwargs["color"] = "k"
    for idx, col in enumerate(x.columns):
        w = x[col]
        w = w[w > 0]
        ax.plot(w.index, [idx] * len(w.index), **kwargs)

    # ax.hlines(
    #     range(len(x.columns)),
    #     x.index.min(),
    #     x.index.max(),
    #     linewidth=hlines_lw,
    #     color=hlines_c,
    #     linestyle=hlines_ls,
    # )

    ax.grid(axis="both", color=grid_c, linestyle=grid_ls, linewidth=grid_lw)

    ax.set_yticks(np.arange(len(x.columns)))
    ax.tick_params(axis="x", labelrotation=90)
    ax.set_yticklabels(x.columns)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.set_aspect("equal")

    return fig


def heatmap(x, figsize=(8, 8), **kwargs):
    """Plots a heatmap from a matrix.

    
    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         'word 0': [1.00, 0.80, 0.70, 0.00,-0.30],
    ...         'word 1': [0.80, 1.00, 0.70, 0.50, 0.00],
    ...         'word 2': [0.70, 0.70, 1.00, 0.00, 0.00],
    ...         'word 3': [0.00, 0.50, 0.00, 1.00, 0.30],
    ...         'word 4': [-0.30, 0.00, 0.00, 0.30, 1.00],
    ...     },
    ...     index=['word {:d}'.format(i) for i in range(5)]
    ... )
    >>> df
            word 0  word 1  word 2  word 3  word 4
    word 0     1.0     0.8     0.7     0.0    -0.3
    word 1     0.8     1.0     0.7     0.5     0.0
    word 2     0.7     0.7     1.0     0.0     0.0
    word 3     0.0     0.5     0.0     1.0     0.3
    word 4    -0.3     0.0     0.0     0.3     1.0
    >>> fig = heatmap(df)
    >>> fig.savefig('sphinx/images/plotheatmap1.png')

    .. image:: images/plotheatmap1.png
        :width: 400px
        :align: center

    >>> fig = heatmap(df, cmap='Blues')
    >>> fig.savefig('sphinx/images/plotheatmap2.png')

    .. image:: images/plotheatmap2.png
        :width: 400px
        :align: center


    >>> df = pd.DataFrame(
    ...     {
    ...         'word 0': [100, 80, 70, 0,30],
    ...         'word 1': [80, 100, 70, 50, 0],
    ...         'word 2': [70, 70, 100, 0, 0],
    ...         'word 3': [0, 50, 0, 100, 3],
    ...         'word 4': [30, 0, 0, 30, 100],
    ...     },
    ...     index=['word {:d}'.format(i) for i in range(5)]
    ... )
    >>> df
            word 0  word 1  word 2  word 3  word 4
    word 0     100      80      70       0      30
    word 1      80     100      70      50       0
    word 2      70      70     100       0       0
    word 3       0      50       0     100      30
    word 4      30       0       0       3     100
    >>> fig = heatmap(df, cmap='Greys')
    >>> fig.savefig('sphinx/images/plotheatmap3.png')

    .. image:: images/plotheatmap3.png
        :width: 400px
        :align: center


    >>> df = pd.DataFrame(
    ...     {
    ...         'word 0': [100, 80, 70, 0,30, 1],
    ...         'word 1': [80, 100, 70, 50, 0, 2],
    ...         'word 2': [70, 70, 100, 0, 0, 3],
    ...         'word 3': [0, 50, 0, 100, 3, 4],
    ...         'word 4': [30, 0, 0, 30, 100, 5],
    ...     },
    ...     index=['word {:d}'.format(i) for i in range(6)]
    ... )
    >>> df
            word 0  word 1  word 2  word 3  word 4
    word 0     100      80      70       0      30
    word 1      80     100      70      50       0
    word 2      70      70     100       0       0
    word 3       0      50       0     100      30
    word 4      30       0       0       3     100
    word 5       1       2       3       4       5

    >>> fig = heatmap(df, cmap='Greys')
    >>> fig.savefig('sphinx/images/plotheatmap3.png')

    .. image:: images/plotheatmap3.png
        :width: 400px
        :align: center

    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()

    x = x.copy()
    result = ax.pcolor(np.transpose(x.values), **kwargs,)
    x.columns = [
        textwrap.shorten(text=w, width=TEXTLEN) if isinstance(w, str) else w
        for w in x.columns
    ]
    x.index = [
        textwrap.shorten(text=w, width=TEXTLEN) if isinstance(w, str) else w
        for w in x.index
    ]
    ax.set_xticks(np.arange(len(x.index)) + 0.5)
    ax.set_xticklabels(x.index)
    ax.tick_params(axis="x", labelrotation=90)
    ax.set_yticks(np.arange(len(x.columns)) + 0.5)
    ax.set_yticklabels(x.columns)
    ax.invert_yaxis()
    if "cmap" in kwargs:
        cmap = plt.cm.get_cmap(kwargs["cmap"])
    else:
        cmap = plt.cm.get_cmap()

    if all(x.dtypes == "int64"):
        fmt = "{:3.0f}"
    else:
        fmt = "{:3.2f}"
    for idx_row, row in enumerate(x.index):
        for idx_col, col in enumerate(x.columns):
            if abs(x.at[row, col]) > x.values.max().max() / 2.0:
                color = cmap(0.0)
            else:
                color = cmap(1.0)
            ax.text(
                idx_row + 0.5,
                idx_col + 0.5,
                fmt.format(x.at[row, col]),
                ha="center",
                va="center",
                color=color,
            )
    ax.xaxis.tick_top()
    return fig


def stacked_bar(
    x, figsize=(10, 10), width=0.8, bottom=None, align="center", cmap="Greys", **kwargs
):
    """Stacked vertical bar plot.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 0,author 1,author 2,author 3,author 3,author 5".split(","),
    ...         "col 0": [6, 5, 4, 3, 2, 1],
    ...         "col 1": [0, 2, 5, 1, 5, 7],
    ...         "ID": list(range(6)),
    ...     }
    ... )
    >>> df
        Authors  col 0  col 1  ID
    0  author 0      6      0   0
    1  author 1      5      2   1
    2  author 2      4      5   2
    3  author 3      3      1   3
    4  author 3      2      5   4
    5  author 5      1      7   5

    >>> fig = stacked_bar(df, cmap='Blues')
    >>> fig.savefig('sphinx/images/stkbar0.png')

    .. image:: images/stkbar0.png
        :width: 400px
        :align: center

    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 0,author 1,author 2,author 3,author 3,author 5".split(","),
    ...         "col 0": [6, 5, 2, 3, 4, 1],
    ...         "col 1": [0, 1, 2, 3, 4, 5],
    ...         "col 2": [3, 2, 3, 1, 0, 1],
    ...         "ID": list(range(6)),
    ...     }
    ... )
    >>> df
        Authors  col 0  col 1  col 2  ID
    0  author 0      6      0      3   0
    1  author 1      5      1      2   1
    2  author 2      2      2      3   2
    3  author 3      3      3      1   3
    4  author 3      4      4      0   4
    5  author 5      1      5      1   5

    >>> fig = stacked_bar(df, cmap='Blues')
    >>> fig.savefig('sphinx/images/stkbar1.png')

    .. image:: images/stkbar1.png
        :width: 400px
        :align: center

    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")
    if bottom is None:
        bottom = x[x.columns[1]].map(lambda w: 0.0)
    for icol, col in enumerate(x.columns[1:]):
        if cmap is not None:
            kwargs["color"] = cmap((0.2 + 0.75 * icol / (len(x.columns) - 1)))
        ax.bar(
            x=range(len(x)),
            height=x[col],
            width=width,
            bottom=bottom,
            align=align,
            label=col,
            **({}),
            **kwargs,
        )
        bottom = bottom + x[col]

    ax.legend()

    ax.grid(axis="y", color="gray", linestyle=":")

    ax.set_xticks(np.arange(len(x[x.columns[0]])))
    ax.set_xticklabels(x[x.columns[0]])
    ax.tick_params(axis="x", labelrotation=90)

    ax.set_xlabel(x.columns[0])
    ax.set_ylabel(x.columns[1])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)

    return fig


def stacked_barh(
    x, figsize=(10, 10), height=0.8, left=None, align="center", cmap=None, **kwargs
):
    """Stacked horzontal bar plot.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 0,author 1,author 2,author 3,author 3,author 5".split(","),
    ...         "col 0": [6, 5, 4, 3, 2, 1],
    ...         "col 1": [0, 2, 5, 1, 5, 7],
    ...         "ID": list(range(6)),
    ...     }
    ... )
    >>> df
        Authors  col 0  col 1  ID
    0  author 0      6      0   0
    1  author 1      5      2   1
    2  author 2      4      5   2
    3  author 3      3      1   3
    4  author 3      2      5   4
    5  author 5      1      7   5

    >>> fig = stacked_barh(df, cmap='Blues')
    >>> fig.savefig('sphinx/images/stkbarh0.png')

    .. image:: images/stkbarh0.png
        :width: 400px
        :align: center

    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 0,author 1,author 2,author 3,author 3,author 5".split(","),
    ...         "col 0": [6, 5, 2, 3, 4, 1],
    ...         "col 1": [0, 1, 2, 3, 4, 5],
    ...         "col 2": [3, 2, 3, 1, 0, 1],
    ...         "ID": list(range(6)),
    ...     }
    ... )
    >>> df
        Authors  col 0  col 1  col 2  ID
    0  author 0      6      0      3   0
    1  author 1      5      1      2   1
    2  author 2      2      2      3   2
    3  author 3      3      3      1   3
    4  author 3      4      4      0   4
    5  author 5      1      5      1   5

    >>> fig = stacked_barh(df, cmap='Blues')
    >>> fig.savefig('sphinx/images/stkbarh1.png')

    .. image:: images/stkbarh1.png
        :width: 400px
        :align: center

    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    x = x.copy()
    if "ID" in x.columns:
        x.pop("ID")
    if left is None:
        left = x[x.columns[1]].map(lambda w: 0.0)
    for icol, col in enumerate(x.columns[1:]):
        if cmap is not None:
            kwargs["color"] = cmap((0.2 + 0.75 * icol / (len(x.columns) - 1)))
        ax.barh(
            y=range(len(x)),
            width=x[col],
            height=height,
            left=left,
            align=align,
            **({}),
            **kwargs,
        )
        left = left + x[col]

    ax.invert_yaxis()
    ax.set_yticks(np.arange(len(x[x.columns[0]])))
    ax.set_yticklabels(x[x.columns[0]])
    ax.set_xlabel(x.columns[1])
    ax.set_ylabel(x.columns[0])
    #
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(False)

    ax.grid(axis="x", color="gray", linestyle=":")

    return fig


def chord_diagram(
    x,
    figsize=(10, 10),
    cmap="Greys",
    alpha=1.0,
    minval=0.0,
    top_n_links=None,
    solid_lines=False,
):
    """Creates a chord diagram from a correlation or an auto-correlation matrix.


    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         'word 0': [1.00, 0.80, 0.70, 0.00,-0.30],
    ...         'word 1': [0.80, 1.00, 0.70, 0.50, 0.00],
    ...         'word 2': [0.70, 0.70, 1.00, 0.00, 0.00],
    ...         'word 3': [0.00, 0.50, 0.00, 1.00, 0.30],
    ...         'word 4': [-0.30, 0.00, 0.00, 0.30, 1.00],
    ...     },
    ...     index=['word {:d}'.format(i) for i in range(5)]
    ... )
    >>> df
            word 0  word 1  word 2  word 3  word 4
    word 0     1.0     0.8     0.7     0.0    -0.3
    word 1     0.8     1.0     0.7     0.5     0.0
    word 2     0.7     0.7     1.0     0.0     0.0
    word 3     0.0     0.5     0.0     1.0     0.3
    word 4    -0.3     0.0     0.0     0.3     1.0
    >>> fig = chord_diagram(df)
    >>> fig.savefig('sphinx/images/plotcd1.png')

    .. image:: images/plotcd1.png
        :width: 400px
        :align: center

    >>> fig = chord_diagram(df, top_n_links=5)
    >>> fig.savefig('sphinx/images/plotcd2.png')

    .. image:: images/plotcd2.png
        :width: 400px
        :align: center

    >>> fig = chord_diagram(df, solid_lines=True)
    >>> fig.savefig('sphinx/images/plotcd3.png')

    .. image:: images/plotcd3.png
        :width: 400px
        :align: center

    """

    x = x.copy()

    # ---------------------------------------------------
    #
    # Node sizes
    #
    terms = x.columns
    node_sizes = [int(w[w.find("[") + 1 : w.find("]")]) for w in terms if "[" in w]
    if len(node_sizes) == 0:
        node_sizes = [10] * len(terms)
    else:
        max_size = max(node_sizes)
        min_size = min(node_sizes)
        if min_size == max_size:
            node_sizes = [30] * len(terms)
        else:
            node_sizes = [
                100 + int(1000 * (w - min_size) / (max_size - min_size))
                for w in node_sizes
            ]

    #
    # Node colors
    #
    cmap = plt.cm.get_cmap(cmap)
    node_colors = [
        cmap(0.2 + 0.75 * node_sizes[i] / max(node_sizes))
        for i in range(len(node_sizes))
    ]
    #
    # ---------------------------------------------------

    cd = ChordDiagram()
    for idx, term in enumerate(x.columns):
        cd.add_node(term, color=node_colors[idx], s=node_sizes[idx])

    if top_n_links is not None and top_n_links <= len(x.columns):
        values = []
        for idx_col in range(len(x.columns) - 1):
            for idx_row in range(idx_col + 1, len(x.columns)):
                node_a = x.index[idx_row]
                node_b = x.columns[idx_col]
                value = x[node_b][node_a]
                values.append(value)
        values = sorted(values, reverse=True)
        minval = values[top_n_links - 1]

    style = ["-", "-", "--", ":"]
    if solid_lines is True:
        style = list("----")

    width = [4, 2, 1, 1]
    if solid_lines is True:
        width = [4, 2, 1, 1]

    links = 0
    for idx_col in range(len(x.columns) - 1):
        for idx_row in range(idx_col + 1, len(x.columns)):

            node_a = x.index[idx_row]
            node_b = x.columns[idx_col]
            value = x[node_b][node_a]

            if value > 0.75 and value >= minval:
                cd.add_edge(
                    node_a,
                    node_b,
                    linestyle=style[0],
                    linewidth=width[0],
                    color="black",
                )
                links += 1
            elif value > 0.50 and value >= minval:
                cd.add_edge(
                    node_a,
                    node_b,
                    linestyle=style[1],
                    linewidth=width[1],
                    color="black",
                )
                links += 1
            elif value > 0.25 and value >= minval:
                cd.add_edge(
                    node_a,
                    node_b,
                    linestyle=style[2],
                    linewidth=width[2],
                    color="black",
                )
                links += 1
            elif value <= 0.25 and value >= minval and value > 0.0:
                cd.add_edge(
                    node_a,
                    node_b,
                    linestyle=style[3],
                    linewidth=width[3],
                    color="black",
                )
                links += 1

            if top_n_links is not None and links >= top_n_links:
                continue

    return cd.plot(figsize=figsize)


def worldmap(x, figsize=(10, 5), cmap="Pastel2", legend=True, *args, **kwargs):
    """Worldmap plot with the number of documents per country.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> x = pd.DataFrame(
    ...     {
    ...         "AU_CO": ["China", "Taiwan", "United States", "United Kingdom", "India", "Colombia"],
    ...         "Num_Documents": [1000, 900, 800, 700, 600, 1000],
    ...     },
    ... )
    >>> x
                AU_CO  Num_Documents
    0           China           1000
    1          Taiwan            900
    2   United States            800
    3  United Kingdom            700
    4           India            600
    5        Colombia           1000
    >>> fig = worldmap(x, figsize=(15, 6))
    >>> fig.savefig('sphinx/images/worldmap.png')

    .. image:: images/worldmap.png
        :width: 2000px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    x = x.copy()
    column0 = x[x.columns[0]]
    column1 = x[x.columns[1]]
    x["color"] = x[x.columns[1]].map(
        lambda w: (w - column1.min()) / (column1.max() - column1.min())
    )
    x = x.set_index(column0)

    module_path = dirname(__file__)
    with open(join(module_path, "data/worldmap.data"), "r") as f:
        countries = json.load(f)
    for country in countries.keys():
        data = countries[country]
        for item in data:
            ax.plot(item[0], item[1], "-k", linewidth=0.5)
            if country in x.index.tolist():
                ax.fill(item[0], item[1], color=cmap(x.color[country]))
    #
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    xleft = xmax - 0.02 * (xmax - xmin)
    xright = xmax
    xbar = np.linspace(xleft, xright, 10)
    ybar = np.linspace(ymin, ymin + (ymax - ymin), 100)
    xv, yv = np.meshgrid(xbar, ybar)
    z = yv / (ymax - ymin) - ymin
    ax.pcolormesh(xv, yv, z, cmap=cmap)
    #
    pos = np.linspace(ymin, ymin + (ymax - ymin), 11)
    value = [
        round(column1.min() + (column1.max() - column1.min()) * i / 10, 0)
        for i in range(11)
    ]
    for i in range(11):
        ax.text(
            xright + 0.2 * (xright - xleft), pos[i], str(int(value[i])), ha="left",
        )

    #  ax.text(xright, ymin, "0", ha="left")
    # ax.text(xright, ymax, str(x[x.columns[0]].max()), ha="left")
    ax.set_aspect("equal")
    ax.axis("on")
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


def tree(x, cmap="Blues", figsize=(8, 8), alpha=0.9):
    """Creates a classification plot from a dataframe.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...         "Authors": "author 3,author 1,author 0,author 2".split(","),
    ...         "Num_Documents": [10, 5, 2, 1],
    ...         "ID": list(range(4)),
    ...     }
    ... )
    >>> df
        Authors  Num_Documents  ID
    0  author 3             10   0
    1  author 1              5   1
    2  author 0              2   2
    3  author 2              1   3

    >>> fig = tree(df)
    >>> fig.savefig('sphinx/images/treeplot.png')

    .. image:: images/treeplot.png
        :width: 400px
        :align: center


    """
    matplotlib.rc("font", size=FONT_SIZE)
    fig = plt.Figure(figsize=figsize)
    ax = fig.subplots()
    cmap = plt.cm.get_cmap(cmap)

    x = x.copy()
    column0 = x[x.columns[0]]
    column1 = x[x.columns[1]]
    colors = [
        cmap((0.2 + 0.75 * column1[i] / max(column1))) for i in range(len(column1))
    ]
    squarify.plot(sizes=column1, label=column0, color=colors, alpha=alpha, ax=ax)
    ax.axis("off")
    return fig


#     def correspondence_plot(self):
#         """Computes and plot clusters of data using correspondence analysis.


#         Examples
#         ----------------------------------------------------------------------------------------------

#         >>> import pandas as pd
#         >>> df = pd.DataFrame(
#         ...     [[3, 8, 6, 1],
#         ...      [3, 4, 7, 5],
#         ...      [9, 9, 2, 3],
#         ...      [0, 1, 0, 4],
#         ...      [4, 4, 8, 7],
#         ...      [2, 4, 4, 9],
#         ...      [4, 2, 4, 1],
#         ...      [0, 0, 9, 2],
#         ...      [9, 3, 9, 4],
#         ...      [2, 3, 2, 0]],
#         ...     columns=list('ABCD'), index=list('abcdefghij'))
#         >>> df
#            A  B  C  D
#         a  3  8  6  1
#         b  3  4  7  5
#         c  9  9  2  3
#         d  0  1  0  4
#         e  4  4  8  7
#         f  2  4  4  9
#         g  4  2  4  1
#         h  0  0  9  2
#         i  9  3  9  4
#         j  2  3  2  0

#         >>> _ = Plot(df).correspondence_plot()
#         >>> plt.savefig('sphinx/images/corana0.png')

#         .. image:: images/corana0.png
#             :width: 500px
#             :align: center


#         """
#         n = self.df.values.sum()
#         P = self.df.values / n
#         column_masses = P.sum(axis=0)
#         row_masses = P.sum(axis=1)
#         E = np.outer(row_masses, column_masses)
#         R = P - E
#         I = R / E
#         Z = I * np.sqrt(E)
#         # u: left (rows),  s: singular values,  vh: right (columns)
#         u, d, v = np.linalg.svd(Z)
#         u = u[:, 0 : v.shape[0]]
#         std_coordinates_rows = u / np.sqrt(row_masses[:, None])
#         std_coordinates_cols = np.transpose(v) / np.sqrt(column_masses[None, :])
#         ppal_coordinates_rows = std_coordinates_rows * d[None, :]
#         ppal_coordinates_cols = std_coordinates_cols * d[:, None]
#         df_rows = pd.DataFrame(
#             ppal_coordinates_rows,
#             index=self.df.index,
#             columns=["f{:d}".format(i) for i in range(len(self.df.columns))],
#         )
#         df_columns = pd.DataFrame(
#             ppal_coordinates_cols,
#             index=self.df.columns,
#             columns=["f{:d}".format(i) for i in range(len(self.df.columns))],
#         )
#         result = pd.concat([df_columns, df_rows])

#         plt.clf()
#         plt.gca().scatter(
#             result.f0[: len(self.df.columns)], result.f1[: len(self.df.columns)]
#         )

#         plt.gca().scatter(
#             result.f0[len(self.df.columns) :],
#             result.f1[len(self.df.columns) :],
#             marker=".",
#         )

#         for i in range(len(self.df.columns)):
#             plt.text(result.f0[i], result.f1[i], self.df.columns[i])

#         plt.gca().spines["top"].set_visible(False)
#         plt.gca().spines["right"].set_visible(False)
#         plt.gca().spines["left"].set_visible(False)
#         plt.gca().spines["bottom"].set_visible(False)
#         return plt.gca()

#         # def encircle(x, y, ax=None, **kw):
#         #     p = np.c_[x, y]
#         #     hull = ConvexHull(p)
#         #     poly = plt.Polygon(p[hull.vertices, :], **kw)
#         #     plt.gca().add_patch(poly)
#         #     #

#         # plt.clf()
#         # plt.scatter(self.df[df.columns[0]], self.df[df.columns[1]], **kwargs)
#         # for i, index in enumerate(self.df.index):
#         #     plt.text(df[df.columns[0]][index], df[df.columns[1]][index], df.index[i])

#         # cluster = AgglomerativeClustering(
#         #     n_clusters=n_clusters, affinity="euclidean", linkage="ward"
#         # )
#         # df = df.copy()
#         # cluster.fit_predict(df)

#         # for icluster in range(n_clusters):
#         #     encircle(
#         #         df.loc[cluster.labels_ == icluster, df.columns[0]],
#         #         df.loc[cluster.labels_ == icluster, df.columns[1]],
#         #         alpha=0.2,
#         #         linewidth=0,
#         #     )


#
#
#
if __name__ == "__main__":

    import doctest

    doctest.testmod()

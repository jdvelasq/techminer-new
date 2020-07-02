"""
Analysis by Term per Year
==================================================================================================


"""
import textwrap

import ipywidgets as widgets
import numpy as np
import pandas as pd
from IPython.display import HTML, clear_output, display
from ipywidgets import AppLayout, GridspecLayout, Layout

import techminer.by_term as by_term
import techminer.by_year as by_year
import techminer.plots as plt
from techminer.explode import __explode
from techminer.keywords import Keywords
from techminer.params import EXCLUDE_COLS
from techminer.plots import COLORMAPS


import techminer.gui as gui

TEXTLEN = 40


def analytics(
    data,
    column,
    output=0,
    top_by=None,
    top_n=None,
    sort_by=0,
    ascending=True,
    cmap="Greys",
    figsize=(6, 6),
    fontsize=11,
    limit_to=None,
    exclude=None,
):
    """Computes the number of documents and citations by term per year.

    Args:
        column (str): the column to explode.
        sep (str): Character used as internal separator for the elements in the column.
        keywords (Keywords): filter the result using the specified Keywords object.

    Returns:
        DataFrame.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...          "Year": [2010, 2010, 2011, 2011, 2012, 2014],
    ...          "Authors": "author 0;author 1;author 2,author 0,author 1,author 3,author 4,author 4".split(","),
    ...          "Times_Cited": list(range(10,16)),
    ...          "ID": list(range(6)),
    ...     }
    ... )
    >>> df
       Year                     Authors  Times_Cited  ID
    0  2010  author 0;author 1;author 2           10   0
    1  2010                    author 0           11   1
    2  2011                    author 1           12   2
    3  2011                    author 3           13   3
    4  2012                    author 4           14   4
    5  2014                    author 4           15   5

    >>> analytics(df, 'Authors', top_by="Times_Cited_per_Year")[['Year', 'Authors', "Times_Cited", 'Num_Documents']]
       Year   Authors  Times_Cited  Num_Documents
    0  2010  author 0           21              2
    1  2010  author 1           10              1
    2  2010  author 2           10              1
    3  2011  author 1           12              1
    4  2011  author 3           13              1
    5  2012  author 4           14              1
    6  2014  author 4           15              1


    >>> analytics(df, 'Authors')[['Year', 'Authors', 'Perc_Num_Documents', 'Perc_Times_Cited']]
       Year   Authors  Perc_Num_Documents  Perc_Times_Cited
    0  2010  author 0               100.0            100.00
    1  2010  author 1                50.0             47.62
    2  2010  author 2                50.0             47.62
    3  2011  author 1                50.0             48.00
    4  2011  author 3                50.0             52.00
    5  2012  author 4               100.0            100.00
    6  2014  author 4               100.0            100.00

    >>> terms = ['author 1', 'author 2', 'author 3']
    >>> analytics(df, 'Authors', limit_to=terms)[['Year', 'Authors', "Times_Cited", 'Num_Documents', 'ID']]
       Year   Authors  Times_Cited  Num_Documents   ID
    0  2010  author 1           10              1  [0]
    1  2010  author 2           10              1  [0]
    2  2011  author 1           12              1  [2]
    3  2011  author 3           13              1  [3]

    >>> terms = ['author 1']
    >>> analytics(df, 'Authors', limit_to=terms)[['Year', 'Authors', "Times_Cited", 'Num_Documents', 'ID']]
       Year   Authors  Times_Cited  Num_Documents   ID
    0  2010  author 1           10              1  [0]
    1  2011  author 1           12              1  [2]


    >>> summary_by_term_per_year(df, 'Authors', exclude=terms)[['Year', 'Authors', 'Perc_Num_Documents', 'Perc_Times_Cited']]
       Year   Authors  Perc_Num_Documents  Perc_Times_Cited
    0  2010  author 0               100.0            100.00
    1  2010  author 2                50.0             47.62
    2  2011  author 3                50.0             52.00
    3  2012  author 4               100.0            100.00
    4  2014  author 4               100.0            100.00

    """

    #
    # Computation
    #
    x = data.copy()
    x = __explode(x[["Year", column, "Times_Cited", "ID"]], column)
    x["Num_Documents"] = 1
    result = x.groupby([column, "Year"], as_index=False).agg(
        {"Times_Cited": np.sum, "Num_Documents": np.size}
    )
    result = result.assign(
        ID=x.groupby([column, "Year"]).agg({"ID": list}).reset_index()["ID"]
    )
    result["Times_Cited"] = result["Times_Cited"].map(lambda x: int(x))

    #
    # Indicators from scientoPy
    #
    summ = by_year.analytics(data)
    num_documents_by_year = {
        key: value for key, value in zip(summ.index, summ.Num_Documents)
    }
    times_cited_by_year = {
        key: value for key, value in zip(summ.index, summ.Times_Cited)
    }

    result["summary_documents_by_year"] = result.Year.apply(
        lambda w: num_documents_by_year[w]
    )
    result["summary_documents_by_year"] = result.summary_documents_by_year.map(
        lambda w: 1 if w == 0 else w
    )
    result["summary_times_cited_by_year"] = result.Year.apply(
        lambda w: times_cited_by_year[w]
    )
    result["summary_times_cited_by_year"] = result.summary_times_cited_by_year.map(
        lambda w: 1 if w == 0 else w
    )

    result["Perc_Num_Documents"] = 0.0
    result = result.assign(
        Perc_Num_Documents=round(
            result.Num_Documents / result.summary_documents_by_year * 100, 2
        )
    )

    result["Perc_Times_Cited"] = 0.0
    result = result.assign(
        Perc_Times_Cited=round(
            result.Times_Cited / result.summary_times_cited_by_year * 100, 2
        )
    )

    result.pop("summary_documents_by_year")
    result.pop("summary_times_cited_by_year")

    result = result.rename(
        columns={
            "Num_Documents": "Num_Documents_per_Year",
            "Times_Cited": "Times_Cited_per_Year",
            "Perc_Num_Documents": "%_Num_Documents_per_Year",
            "Perc_Times_Cited": "%_Times_Cited_per_Year",
        }
    )

    # ----------------------------------------------------------------------------------------

    #
    # top_by
    #
    if isinstance(top_by, str):
        top_by = top_by.replace(" ", "_")
        top_by = {
            "Num_Documents_per_Year": 0,
            "Times_Cited_per_Year": 1,
            "%_Num_Documents_per_Year": 2,
            "%_Times_Cited_per_Year": 3,
        }[top_by]

    # --------------------------------------------------------------------------------------

    #
    # Limit to
    #
    if isinstance(limit_to, dict):
        if column in limit_to.keys():
            limit_to = limit_to[column]
        else:
            limit_to = None

    if limit_to is not None:
        result = result[result[column].map(lambda w: w in limit_to)]

    #
    # Exclude
    #
    if isinstance(exclude, dict):
        if column in exclude.keys():
            exclude = exclude[column]
        else:
            exclude = None

    if exclude is not None:
        result = result[result[column].map(lambda w: w not in exclude)]

    # --------------------------------------------------------------------------------------
    if output == 0:

        columns = {
            0: ["Num_Documents_per_Year", "Times_Cited_per_Year"],
            1: ["Times_Cited_per_Year", "Num_Documents_per_Year"],
            2: ["%_Num_Documents_per_Year", "%_Times_Cited_per_Year"],
            3: ["%_Times_Cited_per_Year", "%_Num_Documents_per_Year"],
        }[top_by]

        result.sort_values(
            columns, ascending=False, inplace=True,
        )

        if top_n is not None:
            result = result.head(top_n)
            result = result.reset_index(drop=True)
        #
        # sort_by
        #
        if isinstance(sort_by, str):
            sort_by = sort_by.replace(" ", "_")
            sort_by = {
                "Alphabetic": 0,
                "Year": 1,
                "Num_Documents_per_Year": 2,
                "Times_Cited_per_Year": 3,
                "%_Num_Documents_per_Year": 4,
                "%_Times_Cited_per_Year": 5,
            }[sort_by]

        if isinstance(ascending, str):
            ascending = {"True": True, "False": False,}[ascending]

        if sort_by == 0:
            result = result.sort_values([column], ascending=ascending)
        else:
            result = result.sort_values(
                {
                    1: ["Year", "Num_Documents_per_Year", "Times_Cited_per_Year"],
                    2: ["Num_Documents_per_Year", "Times_Cited_per_Year", "Year"],
                    3: ["Times_Cited_per_Year", "Num_Documents_per_Year", "Year"],
                    4: ["%_Num_Documents_per_Year", "%_Times_Cited_per_Year", "Year"],
                    5: ["%_Times_Cited_per_Year", "%_Num_Documents_per_Year", "Year"],
                }[sort_by],
                ascending=ascending,
            )

        ###
        summ = by_term.analytics(
            data=x,
            column=column,
            output=0,
            top_by=0,
            top_n=None,
            sort_by=0,
            ascending=ascending,
            limit_to=limit_to,
            exclude=exclude,
        )
        fmt = _get_fmt(summ)
        new_names = {
            key: fmt.format(key, nd, tc)
            for key, nd, tc in zip(summ.index, summ.Num_Documents, summ.Times_Cited)
        }
        result[column] = result[column].map(lambda w: new_names[w])
        ###

        result.pop("ID")
        result = result[
            [
                column,
                "Year",
                "Num_Documents_per_Year",
                "Times_Cited_per_Year",
                "%_Num_Documents_per_Year",
                "%_Times_Cited_per_Year",
            ]
        ]
        return result

    # --------------------------------------------------------------------------------------
    if output in [1, 2, 3, 4, 5]:

        selected_col = {
            0: "Num_Documents_per_Year",
            1: "Times_Cited_per_Year",
            2: "%_Num_Documents_per_Year",
            3: "%_Times_Cited_per_Year",
        }[top_by]

        for col in [
            "Num_Documents_per_Year",
            "Times_Cited_per_Year",
            "%_Num_Documents_per_Year",
            "%_Times_Cited_per_Year",
        ]:

            if col != selected_col:
                result.pop(col)

        result = pd.pivot_table(
            result, values=selected_col, index="Year", columns=column, fill_value=0,
        )

        max = result.max(axis=0)
        max = max.sort_values(ascending=False)
        if top_n is not None:
            max = max.head(top_n)
        result = result[max.index]

        sum_years = result.sum(axis=1)
        for year, index in zip(sum_years, sum_years.index):
            if year == 0:
                result = result.drop(axis=0, labels=index)
            else:
                break

        ###
        summ = by_term.analytics(
            data=x,
            column=column,
            output=0,
            top_by=0,
            top_n=None,
            sort_by=0,
            ascending=ascending,
            limit_to=limit_to,
            exclude=exclude,
        )
        fmt = _get_fmt(summ)
        new_names = {
            key: fmt.format(key, nd, tc)
            for key, nd, tc in zip(summ.index, summ.Num_Documents, summ.Times_Cited)
        }
        result.columns = [new_names[w] for w in result.columns]

        ###

        #
        # sort_by
        #
        if isinstance(sort_by, str):
            sort_by = sort_by.replace(" ", "_")
            sort_by = {
                "Alphabetic": 0,
                "Values": 1,
                "Num_Documents": 2,
                "Times_Cited": 3,
            }[sort_by]

        if sort_by == 0:
            columns = sorted(result.columns, reverse=not ascending)

        if sort_by == 1:
            columns = result.max(axis=0)
            columns = columns.sort_values(ascending=ascending)
            columns = columns.index.tolist()

        if sort_by == 2:
            columns = result.columns.tolist()
            columns = sorted(columns, reverse=not ascending, key=_get_num_documents)

        if sort_by == 3:
            columns = result.columns.tolist()
            columns = sorted(columns, reverse=not ascending, key=_get_times_cited)

        result = result[columns]

        #
        # Output
        #
        if output == 1:
            if cmap is None:
                return result
            else:
                return result.style.background_gradient(cmap=cmap, axis=None)

        if output == 2:
            return plt.heatmap(
                X=result.transpose(), cmap=cmap, figsize=figsize, fontsize=fontsize
            )

        if output == 3:
            return plt.bubble(
                X=result.transpose(),
                darkness=None,
                cmap=cmap,
                figsize=figsize,
                fontsize=fontsize,
            )

        if output == 4:
            return plt.gant(X=result, cmap=cmap, figsize=figsize, fontsize=fontsize,)

        if output == 5:
            return plt.gant0(x=result, figsize=figsize, fontsize=fontsize,)


def _get_num_documents(x):
    z = x.split(" ")[-1]
    z = z.split(":")
    return z[0] + z[1] + x


def _get_times_cited(x):
    z = x.split(" ")[-1]
    z = z.split(":")
    return z[1] + z[0] + x


def _get_fmt(summ):
    n_Num_Documents = int(np.log10(summ["Num_Documents"].max())) + 1
    n_Times_Cited = int(np.log10(summ["Times_Cited"].max())) + 1
    return "{} {:0" + str(n_Num_Documents) + "d}:{:0" + str(n_Times_Cited) + "d}"


##
##
##  Analytics by Value
##
##
def __TAB1__(data, limit_to=None, exclude=None):
    # -------------------------------------------------------------------------
    #
    # UI
    #
    # -------------------------------------------------------------------------
    COLUMNS = sorted([column for column in data.columns if column not in EXCLUDE_COLS])
    #
    left_panel = [
        #  0
        {
            "arg": "view",
            "desc": "View:",
            "widget": widgets.Dropdown(
                options=["Analytics",], layout=Layout(width="55%"),
            ),
        },
        # 1
        {
            "arg": "column",
            "desc": "Column to analyze:",
            "widget": widgets.Dropdown(
                options=[z for z in COLUMNS if z in data.columns],
                layout=Layout(width="55%"),
            ),
        },
        # 2
        {
            "arg": "top_by",
            "desc": "Top by:",
            "widget": widgets.Dropdown(
                options=[
                    "Num Documents per Year",
                    "Times Cited per Year",
                    "% Num Documents per Year",
                    "% Times Cited per Year",
                ],
                layout=Layout(width="55%"),
            ),
        },
        # 3
        gui.top_n(),
        # 4
        {
            "arg": "sort_by",
            "desc": "Sort by:",
            "widget": widgets.Dropdown(
                options=[
                    "Alphabetic",
                    "Year",
                    "Num Documents per Year",
                    "Times Cited per Year",
                    "% Num Documents per Year",
                    "% Times Cited per Year",
                ],
                layout=Layout(width="55%"),
            ),
        },
        # 5
        gui.ascending(),
    ]
    # -------------------------------------------------------------------------
    #
    # Logic
    #
    # -------------------------------------------------------------------------
    def server(**kwargs):
        #
        view = {"Analytics": 0,}[kwargs["view"]]
        column = kwargs["column"]
        top_by = kwargs["top_by"]
        top_n = int(kwargs["top_n"])
        sort_by = kwargs["sort_by"]
        ascending = kwargs["ascending"]

        output.clear_output()
        with output:
            display(
                analytics(
                    data,
                    column=column,
                    output=view,
                    top_by=top_by,
                    top_n=top_n,
                    sort_by=sort_by,
                    ascending=ascending,
                    limit_to=limit_to,
                    exclude=exclude,
                    cmap=None,
                    figsize=None,
                )
            )
            return

    # -------------------------------------------------------------------------
    #
    # Generic
    #
    # -------------------------------------------------------------------------
    args = {control["arg"]: control["widget"] for control in left_panel}
    output = widgets.Output()
    with output:
        display(widgets.interactive_output(server, args,))

    grid = GridspecLayout(13, 6)

    #
    # Left panel
    #
    for index in range(len(left_panel)):
        grid[index, 0] = widgets.HBox(
            [
                widgets.Label(value=left_panel[index]["desc"]),
                left_panel[index]["widget"],
            ],
            layout=Layout(
                display="flex", justify_content="flex-end", align_content="center",
            ),
        )
    #
    # Output
    #
    grid[0:, 1:] = widgets.VBox(
        [output], layout=Layout(height="650px", border="2px solid gray")
    )

    return grid


##
##
##  Analytics by time matrix
##
##
def __TAB0__(data, limit_to=None, exclude=None):
    # -------------------------------------------------------------------------
    #
    # UI
    #
    # -------------------------------------------------------------------------
    COLUMNS = sorted([column for column in data.columns if column not in EXCLUDE_COLS])
    #
    left_panel = [
        #  0
        {
            "arg": "view",
            "desc": "View:",
            "widget": widgets.Dropdown(
                options=["Analytics", "Heatmap", "Bubble plot", "Gant", "Gant0"],
                layout=Layout(width="55%"),
            ),
        },
        # 1
        {
            "arg": "column",
            "desc": "Column:",
            "widget": widgets.Dropdown(
                options=[z for z in COLUMNS if z in data.columns],
                layout=Layout(width="55%"),
            ),
        },
        # 2
        {
            "arg": "top_by",
            "desc": "Top by:",
            "widget": widgets.Dropdown(
                options=[
                    "Num Documents per Year",
                    "Times Cited per Year",
                    "% Num Documents per Year",
                    "% Times Cited per Year",
                ],
                layout=Layout(width="55%"),
            ),
        },
        # 3
        gui.top_n(),
        # 4
        {
            "arg": "sort_by",
            "desc": "Sort by:",
            "widget": widgets.Dropdown(
                options=["Alphabetic", "Values", "Num Documents", "Times Cited"],
                layout=Layout(width="55%"),
            ),
        },
        # 5
        gui.ascending(),
        gui.cmap(),
        gui.fig_width(),
        gui.fig_height(),
    ]
    # -------------------------------------------------------------------------
    #
    # Logic
    #
    # -------------------------------------------------------------------------
    def server(**kwargs):
        #
        view = {"Analytics": 1, "Heatmap": 2, "Bubble plot": 3, "Gant": 4, "Gant0": 5}[
            kwargs["view"]
        ]
        column = kwargs["column"]
        top_by = kwargs["top_by"]
        top_n = int(kwargs["top_n"])
        sort_by = kwargs["sort_by"]
        ascending = kwargs["ascending"]
        cmap = kwargs["cmap"]
        width = int(kwargs["width"])
        height = int(kwargs["height"])

        output.clear_output()
        with output:
            display(
                analytics(
                    data,
                    column=column,
                    output=view,
                    top_by=top_by,
                    top_n=top_n,
                    sort_by=sort_by,
                    ascending=ascending,
                    limit_to=limit_to,
                    exclude=exclude,
                    cmap=cmap,
                    figsize=(width, height),
                )
            )
            return

    # -------------------------------------------------------------------------
    #
    # Generic
    #
    # -------------------------------------------------------------------------
    args = {control["arg"]: control["widget"] for control in left_panel}
    output = widgets.Output()
    with output:
        display(widgets.interactive_output(server, args,))
    #
    grid = GridspecLayout(13, 6)
    #
    # Left panel
    #
    for index in range(len(left_panel)):
        grid[index, 0] = widgets.HBox(
            [
                widgets.Label(value=left_panel[index]["desc"]),
                left_panel[index]["widget"],
            ],
            layout=Layout(
                display="flex", justify_content="flex-end", align_content="center",
            ),
        )
    #
    # Output
    #
    grid[:, 1:] = widgets.VBox(
        [output], layout=Layout(height="657px", border="2px solid gray")
    )

    return grid


#
# def gant(x, column, limit_to=None, exclude=None):
#     """Computes the number of documents by term per year.
#
#     Args:
#         column (str): the column to explode.
#         sep (str): Character used as internal separator for the elements in the column.
#         as_matrix (bool): Results are returned as a matrix.
#         keywords (Keywords): filter the result using the specified Keywords object.
#
#     Returns:
#         DataFrame.
#
#
#     Examples
#     ----------------------------------------------------------------------------------------------
#
#     >>> import pandas as pd
#     >>> df = pd.DataFrame(
#     ...     {
#     ...          "Year": [2010, 2011, 2011, 2012, 2015, 2012, 2016],
#     ...          "Authors": "author 0;author 1;author 2,author 0,author 1,author 3,author 3,author 4,author 4".split(","),
#     ...          "Times_Cited": list(range(10,17)),
#     ...          "ID": list(range(7)),
#     ...     }
#     ... )
#     >>> num_documents_by_term_per_year(df, 'Authors', as_matrix=True)
#           author 0  author 1  author 2  author 3  author 4
#     2010         1         1         1         0         0
#     2011         1         1         0         0         0
#     2012         0         0         0         1         1
#     2015         0         0         0         1         0
#     2016         0         0         0         0         1
#
#     >>> gant(df, 'Authors')
#           author 0  author 1  author 2  author 3  author 4
#     2010         1         1         1         0         0
#     2011         1         1         0         0         0
#     2012         0         0         0         1         1
#     2013         0         0         0         1         1
#     2014         0         0         0         1         1
#     2015         0         0         0         1         1
#     2016         0         0         0         0         1
#
#     >>> terms = Keywords(['author 1', 'author 2'])
#     >>> gant(df, 'Authors', limit_to=terms)
#           author 1  author 2
#     2010         1         1
#     2011         1         0
#
#     >>> gant(df, 'Authors', exclude=terms)
#           author 0  author 3  author 4
#     2010         1         0         0
#     2011         1         0         0
#     2012         0         1         1
#     2013         0         1         1
#     2014         0         1         1
#     2015         0         1         1
#     2016         0         0         1
#
#     """
#
#     years = [year for year in range(result.index.min(), result.index.max() + 1)]
#     result = result.reindex(years, fill_value=0)
#     matrix1 = result.copy()
#     matrix1 = matrix1.cumsum()
#     matrix1 = matrix1.applymap(lambda x: True if x > 0 else False)
#     matrix2 = result.copy()
#     matrix2 = matrix2.sort_index(ascending=False)
#     matrix2 = matrix2.cumsum()
#     matrix2 = matrix2.applymap(lambda x: True if x > 0 else False)
#     matrix2 = matrix2.sort_index(ascending=True)
#     result = matrix1.eq(matrix2)
#     result = result.applymap(lambda x: 1 if x is True else 0)
#     return result
#


##
##
##  Growth Indicators
##
##


def growth_indicators(
    x,
    column,
    timewindow=2,
    output=0,
    top_by=None,
    top_n=None,
    sort_by=None,
    ascending=True,
    plot=None,
    cmap="Greys",
    figsize=(5, 5),
    limit_to=None,
    exclude=None,
):
    """Computes the average growth rate of a group of terms.

    Args:
        column (str): the column to explode.
        timewindow (int): time window for analysis
        keywords (Keywords): filter the result using the specified Keywords object.

    Returns:
        DataFrame.


    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> x = pd.DataFrame(
    ...   {
    ...     "Year": [2010, 2010, 2011, 2011, 2012, 2013, 2014, 2014],
    ...     "Authors": "author 0;author 1;author 2,author 0,author 1,author 3,author 4,author 4,author 0;author 3,author 3;author 4".split(","),
    ...     "Times_Cited": list(range(10,18)),
    ...     "ID": list(range(8)),
    ...   }
    ... )
    >>> x
       Year                     Authors  Times_Cited  ID
    0  2010  author 0;author 1;author 2           10   0
    1  2010                    author 0           11   1
    2  2011                    author 1           12   2
    3  2011                    author 3           13   3
    4  2012                    author 4           14   4
    5  2013                    author 4           15   5
    6  2014           author 0;author 3           16   6
    7  2014           author 3;author 4           17   7

    >>> growth_indicators(x, 'Authors')


    >>> terms = ['author 3', 'author 4']
    >>> growth_indicators(x, 'Authors', limit_to=terms)
        Authors       AGR  ADY  PDLY  Before 2013  Between 2013-2014
    0  author 3  0.666667  1.0  12.5            1                  2
    1  author 4  0.000000  1.0  12.5            1                  2

    >>> growth_indicators(x, 'Authors', exclude=terms)
        Authors       AGR  ADY  PDLY  Before 2011  Between 2011-2014
    0  author 1 -0.333333  0.5  6.25            1                  1
    1  author 0 -0.333333  0.5  6.25            2                  1

    """

    def average_growth_rate():
        #
        #         sum_{i=Y_start}^Y_end  Num_Documents[i] - Num_Documents[i-1]
        #  AGR = --------------------------------------------------------------
        #                          Y_end - Y_start + 1
        #
        #
        result = analytics(
            data=x, column=column, limit_to=limit_to, exclude=exclude, top_by=0,
        )
        #  result.pop("ID")

        years_AGR = sorted(set(result.Year))[-(timewindow + 1) :]
        years_AGR = [years_AGR[0], years_AGR[-1]]
        result = result[result.Year.map(lambda w: w in years_AGR)]
        result = pd.pivot_table(
            result,
            columns="Year",
            index=column,
            values="Num_Documents_per_Year",
            fill_value=0,
        )
        result["AGR"] = 0.0
        result = result.assign(
            AGR=(result[years_AGR[1]] - result[years_AGR[0]]) / timewindow
        )
        result.pop(years_AGR[0])
        result.pop(years_AGR[1])
        result.columns = list(result.columns)
        return result

    def average_documents_per_year():
        #
        #         sum_{i=Y_start}^Y_end  Num_Documents[i]
        #  AGR = -----------------------------------------
        #                  Y_end - Y_start + 1
        #
        result = analytics(
            data=x, column=column, limit_to=limit_to, exclude=exclude, top_by=0
        )
        years_ADY = sorted(set(result.Year))[-timewindow:]
        result = result[result.Year.map(lambda w: w in years_ADY)]
        result = result.groupby([column], as_index=False).agg(
            {"Num_Documents_per_Year": np.sum}
        )
        result = result.rename(columns={"Num_Documents_per_Year": "ADY"})
        result["ADY"] = result.ADY.map(lambda w: w / timewindow)
        return result

    def compute_num_documents():
        result = analytics(
            data=x, column=column, limit_to=limit_to, exclude=exclude, top_by=0
        )
        years_between = sorted(set(result.Year))[-timewindow:]
        years_before = sorted(set(result.Year))[0:-timewindow]
        between = result[result.Year.map(lambda w: w in years_between)]
        before = result[result.Year.map(lambda w: w in years_before)]
        between = between.groupby([column], as_index=False).agg(
            {"Num_Documents_per_Year": np.sum}
        )
        between = between.rename(
            columns={
                "Num_Documents_per_Year": "Between {}-{}".format(
                    years_between[0], years_between[-1]
                )
            }
        )
        before = before.groupby([column], as_index=False).agg(
            {"Num_Documents_per_Year": np.sum}
        )
        before = before.rename(
            columns={"Num_Documents_per_Year": "Before {}".format(years_between[0])}
        )
        result = pd.merge(before, between, on=column)
        return result

    result = average_growth_rate()
    ady = average_documents_per_year()
    result = pd.merge(result, ady, on=column)
    result = result.assign(PDLY=round(result.ADY / len(x) * 100, 2))
    num_docs = compute_num_documents()
    result = pd.merge(result, num_docs, on=column)
    result = result.reset_index(drop=True)
    result = result.set_index(column)

    result = result.head(top_n)
    if isinstance(sort_by, str):
        sort_by = sort_by.replace(" ", "_")
        sort_by = {
            "Alphabetic": 0,
            "Num_Documents": 1,
            "Times_Cited": 2,
            "Average_Growth_Rate": 3,
            "Average_Documents_per_Year": 4,
            "Percentage_of_Documents_in_Last_Years": 5,
            "Before": 6,
            "Between": 7,
        }[sort_by]

    if sort_by == 0:
        result = result.sort_index(axis=0, ascending=ascending)

    if sort_by == 1:
        terms = result.index.tolist()
        terms = sorted(terms, reverse=not ascending, key=_get_num_documents)
        result = result.loc[terms, :]

    if sort_by == 2:
        terms = result.index.tolist()
        terms = sorted(terms, reverse=not ascending, key=_get_times_cited)
        result = result.loc[terms, :]

    if sort_by == 3:
        result = result.sort_values(["AGR", "ADY", "PDLY"], ascending=ascending)

    if sort_by == 4:
        result = result.sort_values(["ADY", "AGR", "PDLY"], ascending=ascending)

    if sort_by == 5:
        result = result.sort_values(["PDLY", "ADY", "AGR"], ascending=ascending)

    if sort_by == 6:
        result = result.sort_values(
            [result.columns[-2], result.columns[-1]], ascending=ascending
        )

    if sort_by == 7:
        result = result.sort_values(
            [result.columns[-1], result.columns[-2]], ascending=ascending
        )

    if output == 0:
        return result

    if output == 1:
        if plot == "bar":
            return plt.bar(height=result.AGR, cmap=cmap, figsize=figsize)
        if plot == "barh":
            return plt.barh(width=result.AGR, cmap=cmap, figsize=figsize)

    if output == 2:
        if plot == "bar":
            return plt.bar(height=result.AGR, cmap=cmap, figsize=figsize)
        if plot == "barh":
            return plt.barh(width=result.AGR, cmap=cmap, figsize=figsize)

    if output == 3:
        if plot == "bar":
            return plt.bar(height=result.AGR, cmap=cmap, figsize=figsize)
        if plot == "barh":
            return plt.barh(width=result.AGR, cmap=cmap, figsize=figsize)

    if output == 4:
        if plot == "bar":
            return plt.stacked_bar(
                result[[result.columns[-2], result.columns[-1]]],
                cmap=cmap,
                figsize=figsize,
            )
        if plot == "barh":
            return plt.stacked_barh(
                result[[result.columns[-2], result.columns[-1]]],
                cmap=cmap,
                figsize=(figsize_width, figsize_height),
            )

    return output


def __TAB2__(x, limit_to=None, exclude=None):
    # -------------------------------------------------------------------------
    #
    # UI
    #
    # -------------------------------------------------------------------------
    COLUMNS = sorted([column for column in x.columns if column not in EXCLUDE_COLS])
    #
    left_panel = [
        # 0
        {
            "arg": "view",
            "desc": "View:",
            "widget": widgets.Dropdown(
                options=[
                    "Analytics",
                    "Average Growth Rate",
                    "Average Documents per Year",
                    "Percentage of Documents in Last Years",
                    "Num Documents",
                ],
                layout=Layout(width="55%"),
            ),
        },
        # 1
        {
            "arg": "column",
            "desc": "Column:",
            "widget": widgets.Dropdown(
                options=[z for z in COLUMNS if z in x.columns],
                layout=Layout(width="55%"),
            ),
        },
        # 1
        {
            "arg": "time_window",
            "desc": "Time window:",
            "widget": widgets.Dropdown(
                options=["2", "3", "4", "5"], value="2", layout=Layout(width="55%"),
            ),
        },
        # 2
        {
            "arg": "top_by",
            "desc": "Top by:",
            "widget": widgets.Dropdown(
                options=[
                    "Average Growth Rate",
                    "Average Documents per Year",
                    "Percentage of Documents in Last Years",
                    "Number of Document Published",
                ],
                value="Average Growth Rate",
                layout=Layout(width="55%"),
            ),
        },
        # 3
        gui.top_n(),
        # 4
        {
            "arg": "sort_by",
            "desc": "Sort by:",
            "widget": widgets.Dropdown(
                options=[
                    "Alphabetic",
                    "Num Documents",
                    "Times Cited",
                    "Average Growth Rate",
                    "Average Documents per Year",
                    "Percentage of Documents in Last Years",
                    "Before",
                    "Between",
                ],
                value="Average Growth Rate",
                layout=Layout(width="55%"),
            ),
        },
        # 5
        gui.ascending(),
        # 4
        {
            "arg": "plot",
            "desc": "Plot type:",
            "widget": widgets.Dropdown(
                options=["bar", "barh"], layout=Layout(width="55%"),
            ),
        },
        # 5
        gui.cmap(),
        gui.fig_width(),
        gui.fig_height(),
    ]
    # -------------------------------------------------------------------------
    #
    # Logic
    #
    # -------------------------------------------------------------------------
    def server(**kwargs):
        #
        view = {
            "Analytics": 0,
            "Average Growth Rate": 1,
            "Average Documents per Year": 2,
            "Percentage of Documents in Last Years": 3,
            "Num Documents": 4,
        }[kwargs["view"]]
        column = kwargs["column"]
        time_window = int(kwargs["time_window"])
        top_by = kwargs["top_by"]
        top_n = int(kwargs["top_n"])
        sort_by = kwargs["sort_by"]
        ascending = kwargs["ascending"]
        plot = kwargs["plot"]
        cmap = kwargs["cmap"]
        width = int(kwargs["width"])
        height = int(kwargs["height"])
        #
        if view == 0:
            left_panel[-4]["widget"].disabled = True
            left_panel[-3]["widget"].disabled = True
            left_panel[-2]["widget"].disabled = True
            left_panel[-1]["widget"].disabled = True
        else:
            left_panel[-4]["widget"].disabled = False
            left_panel[-3]["widget"].disabled = False
            left_panel[-2]["widget"].disabled = False
            left_panel[-1]["widget"].disabled = False
        #

        output.clear_output()
        with output:
            display(
                growth_indicators(
                    x,
                    column=column,
                    output=view,
                    timewindow=time_window,
                    top_n=top_n,
                    sort_by=sort_by,
                    ascending=ascending,
                    plot=plot,
                    cmap=cmap,
                    figsize=(width, height),
                    limit_to=limit_to,
                    exclude=exclude,
                )
            )
            return

    # -------------------------------------------------------------------------
    #
    # Generic
    #
    # -------------------------------------------------------------------------
    args = {control["arg"]: control["widget"] for control in left_panel}
    output = widgets.Output()
    with output:
        display(widgets.interactive_output(server, args,))

    grid = GridspecLayout(13, 6)

    #
    # Left panel
    #
    for index in range(len(left_panel)):
        grid[index, 0] = widgets.HBox(
            [
                widgets.Label(value=left_panel[index]["desc"]),
                left_panel[index]["widget"],
            ],
            layout=Layout(
                display="flex", justify_content="flex-end", align_content="center",
            ),
        )
    #
    # Output
    #
    grid[0:, 1:] = widgets.VBox(
        [output], layout=Layout(height="650px", border="2px solid gray")
    )

    return grid


###############################################################################
##
##  APP
##
###############################################################################


def app(data, limit_to=None, exclude=None, tab=None):
    return gui.APP(
        app_title="Analysis by Term per Year",
        tab_titles=["Matrix View", "List Cells in Matrix", "Growth Indicators",],
        tab_widgets=[
            __TAB0__(data, limit_to=limit_to, exclude=exclude),
            __TAB1__(data),
            __TAB2__(data),
        ],
        tab=tab,
    )


#
#
#
if __name__ == "__main__":

    import doctest

    doctest.testmod()

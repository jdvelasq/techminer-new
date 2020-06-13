"""
Analysis by Year
==================================================================================================


"""
import ipywidgets as widgets
import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd
import techminer.plots as plt
from IPython.display import HTML, clear_output, display
from ipywidgets import AppLayout, Layout
from techminer.plots import COLORMAPS, STYLE


def summary_by_year(df):
    """Computes the number of document and the number of total citations per year.
    This funciton adds the missing years in the sequence.


    Args:
        df (pandas.DataFrame): bibliographic dataframe.


    Returns:
        pandas.DataFrame.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {
    ...          "Year": [2010, 2010, 2011, 2011, 2012, 2016],
    ...          "Cited_by": list(range(10,16)),
    ...          "ID": list(range(6)),
    ...     }
    ... )
    >>> df
       Year  Cited_by  ID
    0  2010        10   0
    1  2010        11   1
    2  2011        12   2
    3  2011        13   3
    4  2012        14   4
    5  2016        15   5

    >>> summary_by_year(df)[['Year', 'Cited_by', 'Num_Documents', 'ID']]
       Year  Cited_by  Num_Documents      ID
    0  2010        21              2  [0, 1]
    1  2011        25              2  [2, 3]
    2  2012        14              1     [4]
    3  2013         0              0      []
    4  2014         0              0      []
    5  2015         0              0      []
    6  2016        15              1     [5]

    >>> summary_by_year(df)[['Cum_Num_Documents', 'Cum_Cited_by', 'Avg_Cited_by']]
       Cum_Num_Documents  Cum_Cited_by  Avg_Cited_by
    0                  2            21          10.5
    1                  4            46          12.5
    2                  5            60          14.0
    3                  5            60           0.0
    4                  5            60           0.0
    5                  5            60           0.0
    6                  6            75          15.0

    """
    data = df[["Year", "Cited_by", "ID"]].explode("Year")
    data["Num_Documents"] = 1
    result = data.groupby("Year", as_index=False).agg(
        {"Cited_by": np.sum, "Num_Documents": np.size}
    )
    result = result.assign(
        ID=data.groupby("Year").agg({"ID": list}).reset_index()["ID"]
    )
    result["Cited_by"] = result["Cited_by"].map(lambda x: int(x))
    years = [year for year in range(result.Year.min(), result.Year.max() + 1)]
    result = result.set_index("Year")
    result = result.reindex(years, fill_value=0)
    result["ID"] = result["ID"].map(lambda x: [] if x == 0 else x)
    result.sort_values(
        "Year", ascending=True, inplace=True,
    )
    result["Cum_Num_Documents"] = result["Num_Documents"].cumsum()
    result["Cum_Cited_by"] = result["Cited_by"].cumsum()
    result["Avg_Cited_by"] = result["Cited_by"] / result["Num_Documents"]
    result["Avg_Cited_by"] = result["Avg_Cited_by"].map(
        lambda x: 0 if pd.isna(x) else x
    )
    result = result.reset_index()
    return result


def documents_by_year(x, cumulative=False):
    """Computes the number of documents per year.
    This function adds the missing years in the sequence.

    Args:
        cumulative (bool): cumulate values per year.

    Returns:
        DataFrame.

    """
    result = summary_by_year(x)
    result.pop("Cited_by")
    result = result.reset_index(drop=True)
    return result


def citations_by_year(x, cumulative=False):
    """Computes the number of citations by year.
    This function adds the missing years in the sequence.

    Args:
        cumulative (bool): cumulate values per year.

    Returns:
        DataFrame.

    """
    result = summary_by_year(x)
    result.pop("Num_Documents")
    result = result.reset_index(drop=True)
    return result


#
#
#  APP
#
#

WIDGET_WIDTH = "200px"
LEFT_PANEL_HEIGHT = "588px"
RIGHT_PANEL_WIDTH = "870px"
FIGSIZE = (15, 9.4)
PANE_HEIGHTS = ["80px", "650px", 0]


def __APP0__(df):
    # -------------------------------------------------------------------------
    #
    # UI
    #
    # -------------------------------------------------------------------------
    controls = [
        # 0
        {
            "arg": "selected_plot",
            "desc": "Plot:",
            "widget": widgets.Dropdown(
                options=[
                    "Documents by Year",
                    "Cum. Documents by Year",
                    "Times Cited by Year",
                    "Cum. Times Cited by Year",
                    "Avg. Times Cited by Year",
                ],
                value="Documents by Year",
                layout=Layout(width=WIDGET_WIDTH),
            ),
        },
        # 1
        {
            "arg": "plot_type",
            "desc": "View:",
            "widget": widgets.Dropdown(
                options=["Bar plot", "Horizontal bar plot", "Table"],
                layout=Layout(width=WIDGET_WIDTH),
            ),
        },
        # 2
        {
            "arg": "style",
            "desc": "Style:",
            "widget": widgets.Dropdown(
                options=STYLE, layout=Layout(width=WIDGET_WIDTH),
            ),
        },
        # 3
        {
            "arg": "cmap",
            "desc": "Colors:",
            "widget": widgets.Dropdown(
                options=COLORMAPS, layout=Layout(width=WIDGET_WIDTH),
            ),
        },
    ]
    # -------------------------------------------------------------------------
    #
    # Logic
    #
    # -------------------------------------------------------------------------
    def server(**kwargs):
        #
        # Logic
        #
        plots = {"Bar plot": plt.bar, "Horizontal bar plot": plt.barh, "Table": None}
        data = {
            "Documents by Year": ["Year", "Num_Documents"],
            "Cum. Documents by Year": ["Year", "Cum_Num_Documents"],
            "Times Cited by Year": ["Year", "Cited_by"],
            "Cum. Times Cited by Year": ["Year", "Cum_Cited_by"],
            "Avg. Times Cited by Year": ["Year", "Avg_Cited_by"],
        }
        #
        x = summary_by_year(df)
        x = x[data[kwargs["selected_plot"]]]
        plot = plots[kwargs["plot_type"]]
        style = kwargs["style"]
        cmap = kwargs["cmap"]
        #
        controls[2]["widget"].disabled = True if plot is None else False
        controls[3]["widget"].disabled = True if plot is None else False
        #
        if style == "default":
            controls[3]["widget"].options = COLORMAPS
        else:
            with pyplot.style.context(style):
                controls[3]["widget"].options = [
                    a["color"] for a in pyplot.rcParams["axes.prop_cycle"]
                ]
                cmap = controls[3]["widget"].value

        output.clear_output()
        with output:
            if plot is None:
                display(x)
            else:
                display(plot(x, style=style, cmap=cmap, figsize=FIGSIZE))

    # -------------------------------------------------------------------------
    #
    # Generic
    #
    # -------------------------------------------------------------------------
    args = {control["arg"]: control["widget"] for control in controls}
    output = widgets.Output()
    widgets.interactive_output(
        server, args,
    )
    return widgets.HBox(
        [
            widgets.VBox(
                [
                    widgets.VBox(
                        [widgets.Label(value=control["desc"]), control["widget"]]
                    )
                    for control in controls
                ],
                layout=Layout(height=LEFT_PANEL_HEIGHT, border="1px solid gray"),
            ),
            widgets.VBox(
                [output], layout=Layout(width=RIGHT_PANEL_WIDTH, align_items="baseline")
            ),
        ]
    )


def app(df):
    """Jupyter Lab dashboard.
    """
    #
    body = widgets.Tab()
    body.children = [__APP0__(df)]
    body.set_title(0, "Time Analysis")
    #
    return AppLayout(
        header=widgets.HTML(
            value="<h1>{}</h1><hr style='height:2px;border-width:0;color:gray;background-color:gray'>".format(
                "Summary by Year"
            )
        ),
        center=body,
        pane_heights=PANE_HEIGHTS,
    )


#
#
#
if __name__ == "__main__":

    import doctest

    doctest.testmod()

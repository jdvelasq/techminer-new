"""
Factor analysis
==================================================================================================



"""
import ipywidgets as widgets
import matplotlib.pyplot as pyplot
import networkx as nx
import numpy as np
import pandas as pd
from IPython.display import HTML, clear_output, display
from ipywidgets import AppLayout, GridspecLayout, Layout
from sklearn.decomposition import PCA

import techminer.by_term as by_term
from techminer.co_occurrence import document_term_matrix
from techminer.explode import __explode
from techminer.keywords import Keywords
from techminer.plots import COLORMAPS


def factor_analysis(
    data,
    column,
    n_components=None,
    output=0,
    top_by=None,
    top_n=None,
    sort_by=None,
    ascending=True,
    figsize=(10, 10),
    layout="Kamada Kawai",
    cmap=None,
    limit_to=None,
    exclude=None,
):
    """Computes the matrix of factors for terms in a given column.

    Args:
        column (str): the column to explode.
        sep (str): Character used as internal separator for the elements in the column.
        n_components: Number of components to compute.
        as_matrix (bool): the result is reshaped by melt or not.
        keywords (Keywords): filter the result using the specified Keywords object.

    Returns:
        DataFrame.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> x = [ 'A', 'A;B', 'B', 'A;B;C', 'B;D', 'A;B']
    >>> y = [ 'a', 'a;b', 'b', 'c', 'c;d', 'd']
    >>> df = pd.DataFrame(
    ...    {
    ...       'Authors': x,
    ...       'Author_Keywords': y,
    ...       "Times_Cited": list(range(len(x))),
    ...       'ID': list(range(len(x))),
    ...       'Year': [1990, 1990, 1991, 1991, 1992, 1992],
    ...    }
    ... )
    >>> df
      Authors Author_Keywords  Times_Cited  ID  Year
    0       A               a            0   0  1990
    1     A;B             a;b            1   1  1990
    2       B               b            2   2  1991
    3   A;B;C               c            3   3  1991
    4     B;D             c;d            4   4  1992
    5     A;B               d            5   5  1992


    >>> document_term_matrix(df, 'Authors')
       A  B  C  D
    0  1  0  0  0
    1  1  1  0  0
    2  0  1  0  0
    3  1  1  1  0
    4  0  1  0  1
    5  1  1  0  0


    >>> factor_analysis(df, 'Authors', n_components=3)
             F0            F1       F2
    A -0.774597 -0.000000e+00  0.00000
    B  0.258199  7.071068e-01 -0.57735
    C -0.258199  7.071068e-01  0.57735
    D  0.516398  1.110223e-16  0.57735

    >>> factor_analysis(df, 'Authors', n_components=3, limit_to=['A', 'B', 'C'])
             F0        F1       F2
    A -0.774597 -0.000000  0.00000
    B  0.258199  0.707107 -0.57735
    C -0.258199  0.707107  0.57735

    >>> factor_analysis(df, 'Authors', n_components=3, exclude=['C'])
             F0            F1       F2
    A -0.774597 -0.000000e+00  0.00000
    B  0.258199  7.071068e-01 -0.57735
    D  0.516398  1.110223e-16  0.57735

    """

    #
    # Computo
    #
    x = data.copy()
    dtm = document_term_matrix(x, column)
    terms = dtm.columns.tolist()
    if n_components is None:
        n_components = int(np.sqrt(len(set(terms))))
    pca = PCA(n_components=n_components)
    result = np.transpose(pca.fit(X=dtm.values).components_)
    result = pd.DataFrame(
        result, columns=["F" + str(i) for i in range(n_components)], index=terms
    )

    if isinstance(top_by, str):
        top_by = top_by.replace(" ", "_")
        top_by = {"Values": -1, "Num_Documents": 0, "Times_Cited": 1,}[top_by]

    #
    # top by
    #
    limit = 0.25
    if top_by == -1:

        max_by_rows = result.max(axis=1)
        max_by_rows = max_by_rows[(max_by_rows >= limit) | (max_by_rows <= -limit)]
        if len(max_by_rows) < 5:
            limit = 0.10
            max_by_rows = result.max(axis=1)
            max_by_rows = max_by_rows[(max_by_rows >= limit) | (max_by_rows <= -limit)]
        result = result.loc[max_by_rows.index, :]

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

    else:

        summ = by_term.analytics(
            data=x,
            column=column,
            output=0,
            top_by=top_by,
            top_n=top_n,
            sort_by=top_by,
            ascending=ascending,
            limit_to=limit_to,
            exclude=exclude,
        )

        result = result.loc[summ.index, :]

    if isinstance(output, str):
        output = output.replace(" ", "_")
        output = {"Matrix": 0, "Network": 1,}[output]

    if output == 0:

        #
        # Rename row axis
        #

        fmt = _get_fmt(summ)
        new_names = {
            key: fmt.format(key, nd, tc)
            for key, nd, tc in zip(summ.index, summ.Num_Documents, summ.Times_Cited)
        }
        #

        #  new_names = {key: value for key, value in zip(summ.index, summ[top_by])}
        result.index = [new_names[idx] for idx in result.index.tolist()]

        #
        # top_by
        #
        if sort_by == "Alphabetic":
            result = result.sort_index(axis=0, ascending=ascending)

        if sort_by == "Num Documents":
            terms = result.index.tolist()
            terms = sorted(terms, reverse=not ascending, key=_get_num_documents)
            result = result.loc[terms, :]

        if sort_by == "Times Cited":
            terms = result.index.tolist()
            terms = sorted(terms, reverse=not ascending, key=_get_times_cited)
            result = result.loc[terms, :]

        if sort_by in ["F{}".format(i) for i in range(n_components)]:
            result = result.sort_values(sort_by, ascending=ascending)

        if cmap is None:
            return result
        else:
            return result.style.background_gradient(cmap=cmap, axis=None)

    if output == 1:
        return factor_map(
            matrix=result, summary=summ, layout=layout, cmap=cmap, figsize=figsize,
        )


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


def factor_map(matrix, summary, layout="Kamada Kawai", cmap="Greys", figsize=(17, 12)):
    """
    """

    #
    # Data preparation
    #
    terms = matrix.index.tolist()
    terms = [w[: w.find("[")].strip() if "[" in w else w for w in terms]
    terms = [w.strip() for w in terms]

    num_documents = {k: v for k, v in zip(summary.index, summary["Num_Documents"])}
    times_cited = {k: v for k, v in zip(summary.index, summary["Times_Cited"])}

    #
    # Node sizes
    #
    node_sizes = [num_documents[t] for t in terms]
    if len(node_sizes) == 0:
        node_sizes = [500] * len(terms)
    else:
        max_size = max(node_sizes)
        min_size = min(node_sizes)
        if min_size == max_size:
            node_sizes = [500] * len(terms)
        else:
            node_sizes = [
                600 + int(2500 * (w - min_size) / (max_size - min_size))
                for w in node_sizes
            ]

    #
    # Node colors
    #

    cmap = pyplot.cm.get_cmap(cmap)
    node_colors = [times_cited[t] for t in terms]
    node_colors = [
        cmap(0.2 + 0.75 * node_colors[i] / max(node_colors))
        for i in range(len(node_colors))
    ]

    matrix.index = terms

    #
    # Draw the network
    #
    fig = pyplot.Figure(figsize=figsize)
    ax = fig.subplots()

    draw_dict = {
        "Circular": nx.draw_circular,
        "Kamada Kawai": nx.draw_kamada_kawai,
        "Planar": nx.draw_planar,
        "Random": nx.draw_random,
        "Spectral": nx.draw_spectral,
        "Spring": nx.draw_spring,
        "Shell": nx.draw_shell,
    }
    draw = draw_dict[layout]

    G = nx.Graph(ax=ax)
    G.clear()

    #
    # network nodes
    #
    G.add_nodes_from(terms)

    #
    # network edges
    #
    for idx, column in enumerate(matrix.columns):

        matrix = matrix.sort_values(column, ascending=False)

        x = matrix[column][matrix[column] >= 0.25]
        # if len(x) > 1:
        #     for t in x.index:
        #         node_colors[t] = cmap(0.05 + 0.9 * float(idx) / len(matrix.columns))

        if len(x) > 1:
            for t0 in range(len(x.index) - 1):
                for t1 in range(1, len(x.index)):
                    value = 0.5 * (x[t0] + x[t1])
                    if value >= 0.75:
                        G.add_edge(x.index[t0], x.index[t1], width=3)
                    elif value >= 0.50:
                        G.add_edge(x.index[t0], x.index[t1], width=2)
                    elif value >= 0.25:
                        G.add_edge(x.index[t0], x.index[t1], width=1)
        #
        x = matrix[column][matrix[column] < -0.25]
        # if len(x) > 1:
        #     for t in x.index:
        #         node_colors[t] = cmap(0.1 + 0.9 * float(idx) / len(matrix.columns))

        if len(x) > 1:
            for t0 in range(len(x.index) - 1):
                for t1 in range(1, len(x.index)):
                    value = 0.5 * (x[t0] + x[t1])
                    if value <= -0.75:
                        G.add_edge(x.index[t0], x.index[t1], width=3)
                    elif value <= -0.50:
                        G.add_edge(x.index[t0], x.index[t1], width=2)
                    elif value <= -0.25:
                        G.add_edge(x.index[t0], x.index[t1], width=1)

    #
    # network edges
    #
    for e in G.edges.data():
        a, b, dic = e
        edge = [(a, b)]
        draw(
            G,
            ax=ax,
            edgelist=edge,
            width=dic["width"],
            edge_color="k",
            with_labels=False,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors="k",
            linewidths=1,
        )

    #
    # Labels
    #
    layout_dict = {
        "Circular": nx.circular_layout,
        "Kamada Kawai": nx.kamada_kawai_layout,
        "Planar": nx.planar_layout,
        "Random": nx.random_layout,
        "Spectral": nx.spectral_layout,
        "Spring": nx.spring_layout,
        "Shell": nx.shell_layout,
    }
    label_pos = layout_dict[layout](G)

    #
    # Figure size
    #
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    for idx, term in enumerate(terms):
        x, y = label_pos[term]
        ax.text(
            x
            + 0.01 * (xlim[1] - xlim[0])
            + 0.001 * node_sizes[idx] / 300 * (xlim[1] - xlim[0]),
            y
            - 0.01 * (ylim[1] - ylim[0])
            - 0.001 * node_sizes[idx] / 300 * (ylim[1] - ylim[0]),
            s=term,
            fontsize=10,
            bbox=dict(
                facecolor="w", alpha=1.0, edgecolor="gray", boxstyle="round,pad=0.5",
            ),
            horizontalalignment="left",
            verticalalignment="top",
        )

    #
    # Figure size
    #

    ax.set_xlim(
        xlim[0] - 0.15 * (xlim[1] - xlim[0]), xlim[1] + 0.15 * (xlim[1] - xlim[0])
    )
    ax.set_ylim(
        ylim[0] - 0.15 * (ylim[1] - ylim[0]), ylim[1] + 0.15 * (ylim[1] - ylim[0])
    )
    ax.set_aspect("equal")
    return fig


#
#
# APP
#
#

LEFT_PANEL_HEIGHT = "655px"
RIGHT_PANEL_WIDTH = "1200px"
PANE_HEIGHTS = ["80px", "720px", 0]

COLUMNS = [
    "Authors",
    "Countries",
    "Institutions",
    "Author_Keywords",
    "Index_Keywords",
    "Abstract_words_CL",
    "Abstract_words",
    "Title_words_CL",
    "Title_words",
    "Affiliations",
    "Author_Keywords_CL",
    "Index_Keywords_CL",
]


def __TAB0__(data, limit_to, exclude):
    # -------------------------------------------------------------------------
    #
    # UI
    #
    # -------------------------------------------------------------------------
    left_panel = [
        # 0
        {
            "arg": "view",
            "desc": "View:",
            "widget": widgets.Dropdown(
                options=["Matrix", "Network"], disable=True, layout=Layout(width="90%"),
            ),
        },
        # 1
        {
            "arg": "term",
            "desc": "Term to analyze:",
            "widget": widgets.Dropdown(
                options=[z for z in COLUMNS if z in data.columns],
                ensure_option=True,
                disabled=False,
                layout=Layout(width="90%"),
            ),
        },
        # 2
        {
            "arg": "n_components",
            "desc": "Number of factors:",
            "widget": widgets.Dropdown(
                options=list(range(2, 21)),
                value=2,
                ensure_option=True,
                disabled=False,
                layout=Layout(width="90%"),
            ),
        },
        # 3
        {
            "arg": "cmap",
            "desc": "Colormap:",
            "widget": widgets.Dropdown(
                options=COLORMAPS, disable=False, layout=Layout(width="90%"),
            ),
        },
        # 4
        {
            "arg": "top_by",
            "desc": "Top by:",
            "widget": widgets.Dropdown(
                options=["Values", "Num Documents", "Times Cited"],
                layout=Layout(width="90%"),
            ),
        },
        # 5
        {
            "arg": "top_n",
            "desc": "Top N:",
            "widget": widgets.Dropdown(
                options=list(range(5, 51, 5)),
                ensure_option=True,
                layout=Layout(width="90%"),
            ),
        },
        # 6
        {
            "arg": "sort_by",
            "desc": "Sort by:",
            "widget": widgets.Dropdown(
                options=["Alphabetic", "Num Documents/Times Cited", "Factor",],
                disable=False,
                layout=Layout(width="90%"),
            ),
        },
        # 7
        {
            "arg": "ascending",
            "desc": "Ascending :",
            "widget": widgets.Dropdown(
                options=[True, False], layout=Layout(width="90%"),
            ),
        },
        #  8
        {
            "arg": "layout",
            "desc": "Map layout:",
            "widget": widgets.Dropdown(
                options=[
                    "Circular",
                    "Kamada Kawai",
                    "Planar",
                    "Random",
                    "Spectral",
                    "Spring",
                    "Shell",
                ],
                layout=Layout(width="90%"),
            ),
        },
        # 9
        {
            "arg": "width",
            "desc": "Width",
            "widget": widgets.Dropdown(
                options=range(5, 15, 1), ensure_option=True, layout=Layout(width="90%"),
            ),
        },
        # 10
        {
            "arg": "height",
            "desc": "Height",
            "widget": widgets.Dropdown(
                options=range(5, 15, 1), ensure_option=True, layout=Layout(width="90%"),
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
        view = kwargs["view"]
        term = kwargs["term"]
        n_components = int(kwargs["n_components"])
        cmap = kwargs["cmap"]
        top_by = kwargs["top_by"]
        top_n = int(kwargs["top_n"])
        sort_by = kwargs["sort_by"]
        ascending = kwargs["ascending"]
        layout = kwargs["layout"]
        width = int(kwargs["width"])
        height = int(kwargs["height"])

        left_panel[6]["widget"].options = [
            "Alphabetic",
            "Num Documents",
            "Times Cited",
        ] + ["F{}".format(i) for i in range(n_components)]

        left_panel[5]["widget"].disabled = True if top_by == "Values" else False
        left_panel[-3]["widget"].disabled = False if view == "Network" else True
        left_panel[-2]["widget"].disabled = False if view == "Network" else True
        left_panel[-1]["widget"].disabled = False if view == "Network" else True

        output.clear_output()
        with output:
            return display(
                factor_analysis(
                    data=data,
                    column=term,
                    output=view,
                    n_components=n_components,
                    top_by=top_by,
                    top_n=top_n,
                    layout=layout,
                    sort_by=sort_by,
                    ascending=ascending,
                    cmap=cmap,
                    figsize=(width, height),
                    limit_to=limit_to,
                    exclude=exclude,
                )
            )

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
    grid = GridspecLayout(11, 8)
    #
    # Left panel
    #
    for index in range(len(left_panel)):
        grid[index, 0] = widgets.VBox(
            [
                widgets.Label(value=left_panel[index]["desc"]),
                left_panel[index]["widget"],
            ]
        )
    #
    # Output
    #
    grid[0:, 1:] = widgets.VBox(
        [output], layout=Layout(height="650px", border="2px solid gray")
    )

    return grid


def app(data, limit_to=None, exclude=None, tab=None):
    """Jupyter Lab dashboard.
    """
    app_title = "Factor Analysis"
    tab_titles = [
        "Factor Analysis",
    ]
    tab_list = [
        __TAB0__(data, limit_to=limit_to, exclude=exclude),
    ]

    if tab is not None:
        return AppLayout(
            header=widgets.HTML(
                value="<h1>{}</h1><hr style='height:2px;border-width:0;color:gray;background-color:gray'>".format(
                    app_title + " / " + tab_titles[tab]
                )
            ),
            center=tab_list[tab],
            pane_heights=["80px", "660px", 0],  # tamaño total de la ventana: Ok!
        )

    body = widgets.Tab()
    body.children = tab_list
    for i in range(len(tab_list)):
        body.set_title(i, tab_titles[i])
    return AppLayout(
        header=widgets.HTML(
            value="<h1>{}</h1><hr style='height:2px;border-width:0;color:gray;background-color:gray'>".format(
                app_title
            )
        ),
        center=body,
        pane_heights=["80px", "720px", 0],
    )


#
#
#
if __name__ == "__main__":

    import doctest

    doctest.testmod()

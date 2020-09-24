import ipywidgets as widgets
import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd
from pyvis.network import Network

import techminer.core.dashboard as dash
from techminer.core import (
    DASH,
    Network,
    TF_matrix,
    add_counters_to_axis,
    corpus_filter,
    limit_to_exclude,
    normalize_network,
    sort_by_axis,
)

from techminer.core import cluster_table_to_list
from techminer.plots import ChordDiagram
from techminer.plots import bubble_plot as bubble_plot_
from techminer.plots import counters_to_node_colors, counters_to_node_sizes
from techminer.plots import heatmap as heatmap_

###############################################################################
##
##  MODEL
##
###############################################################################


class Model:
    def __init__(
        self,
        data,
        limit_to,
        exclude,
        years_range,
        clusters=None,
        cluster=None,
    ):
        #
        if years_range is not None:
            initial_year, final_year = years_range
            data = data[(data.Year >= initial_year) & (data.Year <= final_year)]

        #
        # Filter for cluster members
        #
        if clusters is not None and cluster is not None:
            data = corpus_filter(data=data, clusters=clusters, cluster=cluster)

        self.data = data
        self.limit_to = limit_to
        self.exclude = exclude

        self.X_ = None
        self.c_axis_ascending = None
        self.clustering = None
        self.cmap = None
        self.column = None
        self.height = None
        self.layout = None
        self.max_nodes = None
        self.normalization = None
        self.nx_iterations = None
        self.r_axis_ascending = None
        self.sort_c_axis_by = None
        self.sort_r_axis_by = None
        self.top_by = None
        self.width = None
        self.min_occurrence = None
        self.max_items = None
        self.n_labels = None

    def apply(self):

        ##
        ##  Computes TF_matrix with occurrence >= min_occurrence
        ##
        TF_matrix_ = TF_matrix(
            data=self.data,
            column=self.column,
            scheme=None,
            min_occurrence=self.min_occurrence,
        )

        ##
        ##  Limit to/Exclude
        ##
        TF_matrix_ = limit_to_exclude(
            data=TF_matrix_,
            axis=1,
            column=self.column,
            limit_to=self.limit_to,
            exclude=self.exclude,
        )

        ##
        ##  Adds counters to axis
        ##
        TF_matrix_ = add_counters_to_axis(
            X=TF_matrix_, axis=1, data=self.data, column=self.column
        )

        TF_matrix_ = sort_by_axis(
            data=TF_matrix_, sort_by=self.top_by, ascending=False, axis=1
        )

        ##
        ##  Select max_items
        ##
        TF_matrix_ = TF_matrix_[TF_matrix_.columns[: self.max_items]]
        if len(TF_matrix_.columns) > self.max_items:
            top_items = TF_matrix_.sum(axis=0)
            top_items = top_items.sort_values(ascending=False)
            top_items = top_items.head(self.max_items)
            TF_matrix_ = TF_matrix_.loc[:, top_items.index]
            rows = TF_matrix_.sum(axis=1)
            rows = rows[rows > 0]
            TF_matrix_ = TF_matrix_.loc[rows.index, :]

        ##
        ##  Co-occurrence matrix and association index
        ##
        X = np.matmul(TF_matrix_.transpose().values, TF_matrix_.values)
        X = pd.DataFrame(X, columns=TF_matrix_.columns, index=TF_matrix_.columns)
        X = normalize_network(X, self.normalization)

        ##
        ##  Sort by
        ##
        X = sort_by_axis(
            data=X, sort_by=self.sort_r_axis_by, ascending=self.r_axis_ascending, axis=0
        )
        X = sort_by_axis(
            data=X, sort_by=self.sort_c_axis_by, ascending=self.c_axis_ascending, axis=1
        )

        self.X_ = X

    def matrix(self):
        self.apply()
        if self.normalization == "None":
            return self.X_.style.background_gradient(cmap=self.cmap, axis=None)
        else:
            return self.X_.style.set_precision(2).background_gradient(
                cmap=self.cmap, axis=None
            )

    def heatmap(self):
        self.apply()
        return heatmap_(self.X_, cmap=self.cmap, figsize=(self.width, self.height))

    def bubble_plot(self):
        self.apply()
        return bubble_plot_(
            self.X_, axis=0, cmap=self.cmap, figsize=(self.width, self.height)
        )

    def network(self):
        self.apply()
        return Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).networkx_plot(
            layout=self.layout,
            iterations=self.nx_iterations,
            k=self.nx_k,
            scale=self.nx_scale,
            seed=int(self.random_state),
            figsize=(self.width, self.height),
        )

    def communities_table(self):
        self.apply()
        return Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).cluster_members_

    def communities_list(self):
        self.apply()
        members = Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).cluster_members_

        return cluster_table_to_list(table=members)

    def communities_python_code(self):
        self.apply()
        members = Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).cluster_members_

        dict_ = {}
        for i_cluster, cluster in enumerate(members.columns):

            x = members[cluster].tolist()
            x = [m for m in x if m.strip() != ""]
            x = [" ".join(m.split(" ")[:-1]) for m in x]

            dict_[i_cluster] = x

        HTML = "CLUSTERS = [<br>"
        HTML += '    "' + self.column + '",<br>'
        HTML += "    {<br>"
        for key in dict_.keys():
            HTML += "        " + str(key) + ": [<br>"
            for value in dict_[key]:
                HTML += "            " + repr(value) + ",<br>"
            HTML += "        ],<br>"
        HTML += "    }<br>"
        HTML += "]"
        return widgets.HTML("<pre>" + HTML + "</pre>")

    def network_interactive(self):

        self.apply()
        return Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).pyvis_plot()

    def chord_diagram(self):
        self.apply()
        x = self.X_.copy()
        terms = self.X_.columns.tolist()
        node_sizes = counters_to_node_sizes(x=terms)
        node_colors = counters_to_node_colors(x, cmap=pyplot.cm.get_cmap(self.cmap))

        cd = ChordDiagram()

        ## add nodes
        for idx, term in enumerate(x.columns):
            cd.add_node(term, color=node_colors[idx], s=node_sizes[idx])

        ## add links
        m = x.stack().to_frame().reset_index()
        m = m[m.level_0 < m.level_1]
        m.columns = ["from_", "to_", "link_"]
        m = m.reset_index(drop=True)

        for idx in range(len(m)):

            if m.link_[idx] > 0.001:
                d = {
                    "linestyle": "-",
                    "linewidth": 0.0
                    + 2
                    * (m.link_[idx] - m.link_.min())
                    / (m.link_.max() - m.link_.min()),
                    "color": "gray",
                }

                cd.add_edge(m.from_[idx], m.to_[idx], **d)

        return cd.plot(figsize=(self.width, self.height))


###############################################################################
##
##  DASHBOARD
##
###############################################################################


class DASHapp(DASH, Model):
    def __init__(
        self,
        data,
        limit_to=None,
        exclude=None,
        years_range=None,
        clusters=None,
        cluster=None,
    ):
        """Dashboard app"""

        Model.__init__(
            self,
            data=data,
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=clusters,
            cluster=cluster,
        )
        DASH.__init__(self)

        self.app_title = "Graph Analysis"
        self.menu_options = [
            "Matrix",
            "Heatmap",
            "Bubble plot",
            "Network",
            "Chord diagram",
            "Communities (table)",
            "Communities (list)",
            "Communities (Python code)",
        ]

        COLUMNS = sorted(
            [
                column
                for column in data.columns
                if column
                not in [
                    "Abb_Source_Title",
                    "Abstract",
                    "Affiliations",
                    "Authors_ID",
                    "Bradford_Law_Zone",
                    "Document_Type",
                    "Frac_Num_Documents",
                    "Global_Citations",
                    "Global_References",
                    "Historiograph_ID",
                    "ID",
                    "Local_Citations",
                    "Local_References",
                    "Num_Authors",
                    "Source_Title",
                    "Title",
                    "Year",
                ]
            ]
        )

        self.panel_widgets = [
            dash.dropdown(
                desc="Column:",
                options=[z for z in COLUMNS if z in data.columns],
            ),
            dash.min_occurrence(),
            dash.max_items(),
            dash.normalization(),
            dash.dropdown(
                desc="Clustering:",
                options=[
                    "Label propagation",
                    "Leiden",
                    "Louvain",
                    "Walktrap",
                ],
            ),
            dash.separator(text="Visualization"),
            dash.dropdown(
                desc="Top by:",
                options=[
                    "Num Documents",
                    "Global Citations",
                ],
            ),
            dash.dropdown(
                desc="Sort C-axis by:",
                options=[
                    "Alphabetic",
                    "Num Documents",
                    "Global Citations",
                    "Data",
                ],
            ),
            dash.c_axis_ascending(),
            dash.dropdown(
                desc="Sort R-axis by:",
                options=[
                    "Alphabetic",
                    "Num Documents",
                    "Global Citations",
                    "Data",
                ],
            ),
            dash.r_axis_ascending(),
            dash.cmap(),
            dash.n_labels(),
            dash.nx_iterations(),
            dash.nx_k(),
            dash.nx_scale(),
            dash.random_state(),
            dash.fig_width(),
            dash.fig_height(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)

        if self.menu == "Matrix":

            self.set_disabled("Clustering:")

            self.set_enabled("Top by:")
            self.set_enabled("Sort C-axis by:")
            self.set_enabled("C-axis ascending:")
            self.set_enabled("Sort R-axis by:")
            self.set_enabled("R-axis ascending:")
            self.set_disabled("Colormap:")
            self.set_disabled("N labels:")
            self.set_disabled("NX iterations:")
            self.set_disabled("NX K:")
            self.set_disabled("NX scale:")
            self.set_disabled("Random State:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")

        if self.menu in ["Heatmap", "Bubble plot"]:

            self.set_disabled("Clustering:")

            self.set_enabled("Top by:")
            self.set_enabled("Sort C-axis by:")
            self.set_enabled("C-axis ascending:")
            self.set_enabled("Sort R-axis by:")
            self.set_enabled("R-axis ascending:")

            self.set_enabled("Colormap:")
            self.set_disabled("N labels:")
            self.set_disabled("NX iterations:")
            self.set_disabled("NX K:")
            self.set_disabled("NX scale:")
            self.set_enabled("Random State:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")

        if self.menu in ["Chord diagram"]:

            self.set_disabled("Clustering:")

            self.set_enabled("Top by:")
            self.set_disabled("Sort C-axis by:")
            self.set_disabled("C-axis ascending:")
            self.set_disabled("Sort R-axis by:")
            self.set_disabled("R-axis ascending:")

            self.set_enabled("Colormap:")
            self.set_disabled("N labels:")
            self.set_disabled("NX iterations:")
            self.set_disabled("NX K:")
            self.set_disabled("NX scale:")
            self.set_disabled("Random State:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")

        if self.menu in ["Network"]:

            self.set_enabled("Clustering:")

            self.set_disabled("Top by:")
            self.set_disabled("Sort C-axis by:")
            self.set_disabled("C-axis ascending:")
            self.set_disabled("Sort R-axis by:")
            self.set_disabled("R-axis ascending:")

            self.set_enabled("Colormap:")
            self.set_enabled("NX iterations:")
            self.set_enabled("NX K:")
            self.set_enabled("NX scale:")
            self.set_enabled("Random State:")
            self.set_enabled("N labels:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")

        if self.menu in [
            "Communities (list)",
            "Communities (table)",
            "Communities (Python code)",
        ]:

            self.set_enabled("Clustering:")

            self.set_disabled("Top by:")
            self.set_disabled("Sort C-axis by:")
            self.set_disabled("C-axis ascending:")
            self.set_disabled("Sort R-axis by:")
            self.set_disabled("R-axis ascending:")

            self.set_disabled("Colormap:")
            self.set_disabled("N labels:")
            self.set_disabled("NX iterations:")
            self.set_disabled("NX K:")
            self.set_disabled("NX scale:")
            self.set_disabled("Random State:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")

        if self.menu == "Network (interactive)":

            self.set_enabled("Clustering:")

            self.set_disabled("Top by:")
            self.set_disabled("Sort C-axis by:")
            self.set_disabled("C-axis ascending:")
            self.set_disabled("Sort R-axis by:")
            self.set_disabled("R-axis ascending:")

            self.set_disabled("Colormap:")
            self.set_enabled("N labels:")
            self.set_disabled("NX iterations:")
            self.set_disabled("NX K:")
            self.set_disabled("NX scale:")
            self.set_disabled("Random State:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")
            self.set_disabled("nx iterations:")


###############################################################################
##
##  EXTERNAL INTERFACE
##
###############################################################################


def graph_analysis(
    input_file="techminer.csv",
    limit_to=None,
    exclude=None,
    clusters=None,
    cluster=None,
):
    return DASHapp(
        data=pd.read_csv(input_file),
        limit_to=limit_to,
        exclude=exclude,
        clusters=clusters,
        cluster=cluster,
    ).run()

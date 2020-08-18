import matplotlib
import matplotlib.pyplot as pyplot

import numpy as np
import pandas as pd
from cdlib import algorithms
from pyvis.network import Network
import techminer.common as cmn
import techminer.dashboard as dash

from techminer.dashboard import DASH
from techminer.tfidf import TF_matrix
from techminer.params import EXCLUDE_COLS

from techminer.normalize_network import normalize_network
from techminer.heatmap import heatmap as heatmap_
from techminer.bubble_plot import bubble_plot as bubble_plot_
from techminer.network import Network
from techminer.limit_to_exclude import limit_to_exclude

###############################################################################
##
##  MODEL
##
###############################################################################


class Model:
    def __init__(self, data, limit_to, exclude, years_range):
        ##
        if years_range is not None:
            initial_year, final_year = years_range
            data = data[(data.Year >= initial_year) & (data.Year <= final_year)]

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

    def apply(self):

        #
        # 1.-- Computes TF_matrix with occurrence >= min_occurrence
        #
        TF_matrix_ = TF_matrix(
            data=self.data,
            column=self.column,
            scheme=None,
            min_occurrence=self.min_occurrence,
        )

        #
        # 2.-- Limit to/Exclude
        #
        TF_matrix_ = limit_to_exclude(
            data=TF_matrix_,
            axis=1,
            column=self.column,
            limit_to=self.limit_to,
            exclude=self.exclude,
        )

        #
        # 3.-- Adds counters to axis
        #
        TF_matrix_ = cmn.add_counters_to_axis(
            X=TF_matrix_, axis=1, data=self.data, column=self.column
        )

        TF_matrix_ = cmn.sort_by_axis(
            data=TF_matrix_, sort_by=self.top_by, ascending=False, axis=1
        )

        #
        # 3.-- Select max_items
        #
        TF_matrix_ = TF_matrix_[TF_matrix_.columns[: self.max_items]]
        if len(TF_matrix_.columns) > self.max_items:
            top_items = TF_matrix_.sum(axis=0)
            top_items = top_items.sort_values(ascending=False)
            top_items = top_items.head(self.max_items)
            TF_matrix_ = TF_matrix_.loc[:, top_items.index]
            rows = TF_matrix_.sum(axis=1)
            rows = rows[rows > 0]
            TF_matrix_ = TF_matrix_.loc[rows.index, :]

        #
        # 4.-- Co-occurrence matrix and association index
        #
        X = np.matmul(TF_matrix_.transpose().values, TF_matrix_.values)
        X = pd.DataFrame(X, columns=TF_matrix_.columns, index=TF_matrix_.columns)
        X = normalize_network(X, self.normalization)

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

    def network_nx(self):
        self.apply()
        return Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).networkx_plot(
            layout=self.layout,
            iterations=self.nx_iterations,
            figsize=(self.width, self.height),
        )

    def communities(self):
        self.apply()
        return Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).cluster_members_

    def network_interactive(self):

        self.apply()
        return Network(
            X=self.X_,
            top_by=self.top_by,
            n_labels=self.n_labels,
            clustering=self.clustering,
        ).pyvis_plot()


###############################################################################
##
##  DASHBOARD
##
###############################################################################


class DASHapp(DASH, Model):
    def __init__(self, data, limit_to=None, exclude=None, years_range=None):
        """Dashboard app"""

        Model.__init__(
            self, data=data, limit_to=limit_to, exclude=exclude, years_range=years_range
        )
        DASH.__init__(self)

        self.app_title = "Graph Analysis"
        self.menu_options = [
            "Matrix",
            "Heatmap",
            "Bubble plot",
            "Network (nx)",
            "Network (interactive)",
            "Communities",
        ]

        COLUMNS = sorted(
            [column for column in data.columns if column not in EXCLUDE_COLS]
        )

        self.panel_widgets = [
            dash.dropdown(
                desc="Column:", options=[z for z in COLUMNS if z in data.columns],
            ),
            dash.min_occurrence(),
            dash.max_items(),
            dash.normalization(),
            dash.dropdown(
                desc="Clustering:",
                options=["Label propagation", "Leiden", "Louvain", "Walktrap",],
            ),
            dash.separator(text="Visualization"),
            dash.dropdown(desc="Top by:", options=["Num Documents", "Times Cited",],),
            dash.dropdown(
                desc="Sort C-axis by:",
                options=["Alphabetic", "Num Documents", "Times Cited", "Data",],
            ),
            dash.c_axis_ascending(),
            dash.dropdown(
                desc="Sort R-axis by:",
                options=["Alphabetic", "Num Documents", "Times Cited", "Data",],
            ),
            dash.r_axis_ascending(),
            dash.cmap(),
            dash.nx_layout(),
            dash.n_labels(),
            dash.nx_iterations(),
            dash.fig_width(),
            dash.fig_height(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)

        if self.menu == "Matrix":

            self.set_disabled("Clustering:")
            self.set_disabled("Colormap:")
            self.set_disabled("Layout:")
            self.set_disabled("nx iterations:")
            self.set_disabled("N labels:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")

        if self.menu in ["Heatmap", "Bubble plot"]:

            self.set_disabled("Clustering:")
            self.set_enabled("Colormap:")
            self.set_disabled("Layout:")
            self.set_disabled("nx iterations:")
            self.set_disabled("N labels:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")

        if self.menu == "Network (nx)" or self.menu == "Communities":

            self.set_enabled("Clustering:")
            self.set_enabled("Colormap:")
            self.set_enabled("Layout:")
            self.set_enabled("N labels:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")

            if self.menu == "Network" and self.layout == "Spring":
                self.set_enabled("nx iterations:")
            else:
                self.set_disabled("nx iterations:")

        if self.menu == "Network (interactive)":

            self.set_enabled("Clustering:")
            self.set_disabled("Colormap:")
            self.set_disabled("Layout:")
            self.set_enabled("N labels:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")
            self.set_disabled("nx iterations:")


###############################################################################
##
##  EXTERNAL INTERFACE
##
###############################################################################


def app(data, limit_to=None, exclude=None):
    return DASHapp(data=data, limit_to=limit_to, exclude=exclude).run()
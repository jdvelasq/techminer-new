"""
Factor analysis
==================================================================================================



"""
import ipywidgets as widgets
import matplotlib.pyplot as pyplot
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA, FactorAnalysis, FastICA, TruncatedSVD
from techminer.clustering import clustering
from sklearn.manifold import MDS

import matplotlib.pyplot as pyplot

import techminer.common as cmn

import techminer.core.dashboard as dash
from techminer.core import DASH

from techminer.tfidf import TF_matrix, TFIDF_matrix
from techminer.normalize_network import normalize_network
from techminer.core import limit_to_exclude
from techminer.conceptual_structure_map import conceptual_structure_map
from techminer.xy_clusters_plot import xy_clusters_plot


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

    def apply(self):
        #
        X = self.data.copy()

        #
        # 1.-- TF matrix
        #
        TF_matrix_ = TF_matrix(
            data=X, column=self.column, scheme=None, min_occurrence=self.min_occurrence,
        )

        #
        # 2.-- Limit to / Exclude
        #
        TF_matrix_ = limit_to_exclude(
            data=TF_matrix_,
            axis=1,
            column=self.column,
            limit_to=self.limit_to,
            exclude=self.exclude,
        )

        #
        # 3.-- Add counters to axes
        #
        TF_matrix_ = cmn.add_counters_to_axis(
            X=TF_matrix_, axis=1, data=self.data, column=self.column
        )

        #
        # 4.-- Select top terms
        #
        TF_matrix_ = cmn.sort_axis(
            data=TF_matrix_, num_documents=True, axis=1, ascending=False
        )
        if len(TF_matrix_.columns) > self.max_items:
            TF_matrix_ = TF_matrix_.loc[:, TF_matrix_.columns[0 : self.max_items]]
            rows = TF_matrix_.sum(axis=1)
            rows = rows[rows > 0]
            TF_matrix_ = TF_matrix_.loc[rows.index, :]

        #
        # 5.-- Co-occurrence matrix and normalization
        #
        M = np.matmul(TF_matrix_.transpose().values, TF_matrix_.values)
        M = pd.DataFrame(M, columns=TF_matrix_.columns, index=TF_matrix_.columns)
        M = normalize_network(M, normalization=self.normalization)

        #
        # 6.-- Dissimilarity matrix
        #
        M = 1 - M
        for i in M.columns.tolist():
            M.at[i, i] = 0.0

        #
        # 5.-- Number of factors
        #
        # self.n_components = 2 if self.decomposition_method == "MDS" else 10

        #
        # 6.-- Factor decomposition
        #
        model = {
            "Factor Analysis": FactorAnalysis,
            "PCA": PCA,
            "Fast ICA": FastICA,
            "SVD": TruncatedSVD,
            "MDS": MDS,
        }[self.decomposition_method]

        model = (
            model(
                n_components=self.n_components,
                random_state=int(self.random_state),
                dissimilarity="precomputed",
            )
            if self.decomposition_method == "MDS"
            else model(
                n_components=self.n_components, random_state=int(self.random_state)
            )
        )

        R = model.fit_transform(X=M.values)
        R = pd.DataFrame(
            R,
            columns=["Dim-{}".format(i) for i in range(self.n_components)],
            index=M.columns,
        )

        #
        # 7.-- Clustering
        #
        (
            self.n_clusters,
            self.labels_,
            self.cluster_members_,
            self.cluster_centers_,
            self.cluster_names_,
        ) = clustering(
            X=R,
            method=self.clustering_method,
            n_clusters=self.n_clusters,
            affinity=self.affinity,
            linkage=self.linkage,
            random_state=self.random_state,
            top_n=self.top_n,
            name_prefix="Cluster {}",
        )

        R["Cluster"] = self.labels_

        self.coordinates_ = R

        #
        # 8.-- Results
        #
        self.X_ = R

    def cluster_members(self):
        self.apply()
        return self.cluster_members_

    def conceptual_structure_map(self):
        self.apply()
        X = self.X_
        cluster_labels = X.Cluster
        X.pop("Cluster")
        return conceptual_structure_map(
            coordinates=X,
            cluster_labels=cluster_labels,
            top_n=self.top_n,
            figsize=(self.width, self.height),
        )

    def conceptual_structure_members(self):
        self.apply()
        return self.cluster_members_

    def cluster_plot(self):
        self.apply()
        return xy_clusters_plot(
            x=self.cluster_centers_["Dim-{}".format(self.x_axis)],
            y=self.cluster_centers_["Dim-{}".format(self.y_axis)],
            x_axis_at=0,
            y_axis_at=0,
            labels=self.cluster_names_,
            node_sizes=cmn.counters_to_node_sizes(self.cluster_names_),
            color_scheme=self.color_scheme,
            xlabel="Dim-{}".format(self.x_axis),
            ylabel="Dim-{}".format(self.y_axis),
            figsize=(self.width, self.height),
        )


###############################################################################
##
##  DASHBOARD
##
###############################################################################

COLUMNS = sorted(
    [
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
)


class DASHapp(DASH, Model):
    def __init__(self, data, limit_to=None, exclude=None, years_range=None):
        """Dashboard app"""

        Model.__init__(
            self, data=data, limit_to=limit_to, exclude=exclude, years_range=years_range
        )
        DASH.__init__(self)

        self.app_title = "Factor Analysis"
        self.menu_options = [
            "Cluster members",
            "Cluster plot",
            "Conceptual Structure Map",
            "Conceptual Structure Members",
        ]
        #
        self.panel_widgets = [
            dash.dropdown(
                desc="Column:", options=[z for z in COLUMNS if z in data.columns],
            ),
            dash.min_occurrence(),
            dash.max_items(),
            dash.normalization(include_none=False),
            dash.random_state(),
            dash.separator(text="Clustering"),
            dash.decomposition_method(),
            dash.clustering_method(),
            dash.n_clusters(m=3, n=10, i=1),
            dash.affinity(),
            dash.linkage(),
            dash.separator(text="Visualization"),
            dash.top_n(),
            dash.color_scheme(),
            dash.x_axis(),
            dash.y_axis(),
            dash.fig_width(),
            dash.fig_height(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)

        if self.menu == "Cluster members":
            #
            self.n_components = 10
            #
            self.set_disabled("X-axis:")
            self.set_disabled("Y-axis:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")
            self.set_disabled("Color Scheme:")

        if self.menu == "Cluster plot":
            #
            self.n_components = 10
            #
            self.set_enabled("X-axis:")
            self.set_enabled("Y-axis:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")
            self.set_enabled("Color Scheme:")

        if self.menu in ["Conceptual Structure Map", "Conceptual Structure Members"]:
            #
            self.n_components = 2
            #
            self.set_disabled("X-axis:")
            self.set_disabled("Y-axis:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")
            self.set_disabled("Color Scheme:")

        self.enable_disable_clustering_options()


###############################################################################
##
##  EXTERNAL INTERFACE
##
###############################################################################


def app(data, limit_to=None, exclude=None, years_range=None):
    return DASHapp(
        data=data, limit_to=limit_to, exclude=exclude, years_range=years_range
    ).run()

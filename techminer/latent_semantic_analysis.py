"""
Factor analysis
==================================================================================================



"""
import ipywidgets as widgets
import matplotlib.pyplot as pyplot
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA, FactorAnalysis, FastICA, TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import MDS
from scipy.spatial import ConvexHull
import matplotlib.pyplot as pyplot

import techminer.common as cmn
import techminer.dashboard as dash
from techminer.dashboard import DASH
from techminer.document_term import TF_matrix, TFIDF_matrix

###############################################################################
##
##  MODEL
##
###############################################################################


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
        M = TF_matrix(
            data=X, column=self.column, scheme=None, min_occurrence=self.min_occurrence,
        )

        #
        # 2.-- Computtes TFIDF matrix and select max_term frequent terms
        #
        #      tf-idf = tf * (log(N / df) + 1)
        #
        if self.apply_to == "TF*IDF matrix":
            M = TFIDF_matrix(
                TF_matrix=M,
                norm=None,
                use_idf=False,
                smooth_idf=False,
                sublinear_tf=False,
                max_items=self.max_items,
            )

        #
        # 3.-- Add counters to axes
        #
        M = cmn.add_counters_to_axis(X=M, axis=1, data=self.data, column=self.column)

        #
        # 4.-- Factor decomposition
        #
        model = {
            "Factor Analysis": FactorAnalysis,
            "PCA": PCA,
            "Fast ICA": FastICA,
            "SVD": TruncatedSVD,
            "MDS": MDS,
        }[self.method](
            n_components=self.n_components, random_state=int(self.random_state)
        )

        R = np.transpose(model.fit(X=M.values).components_)
        R = pd.DataFrame(
            R,
            columns=["Dim-{:>02d}".format(i) for i in range(self.n_components)],
            index=M.columns,
        )

        #
        # 5.-- limit to/exclude terms
        #
        R = cmn.limit_to_exclude(
            data=R,
            axis=0,
            column=self.column,
            limit_to=self.limit_to,
            exclude=self.exclude,
        )
        # R = cmn.add_counters_to_axis(X=R, axis=0, data=X, column=self.column)

        #
        # 6.-- Clustering
        #
        clustering = AgglomerativeClustering(
            n_clusters=int(self.n_clusters),
            affinity=self.affinity,
            linkage=self.linkage,
        )
        clustering.fit(R)
        R["Cluster"] = clustering.labels_

        #
        # 7.-- Cluster centers
        #
        self.centers_ = R.groupby("Cluster").mean()

        #
        # 8.-- Cluster name
        #
        names = []
        for i_cluster in range(self.n_clusters):
            X = R[R.Cluster == i_cluster]
            X = cmn.sort_axis(
                data=X,
                num_documents=(self.top_by == "Num Documents"),
                axis=0,
                ascending=False,
            )
            names.append(X.index[0])
        self.centers_["Name"] = names

        #
        # 8.-- Results
        #
        self.X_ = R

    def memberships(self):
        ##
        self.apply()
        ##
        HTML = ""
        for i_cluster in range(self.n_clusters):
            X = self.X_[self.X_.Cluster == i_cluster]
            X = cmn.sort_axis(
                data=X,
                num_documents=(self.top_by == "Num Documents"),
                axis=0,
                ascending=False,
            )
            X = X.head(self.top_n)

            HTML += (
                "==================================================================<br>"
            )
            HTML += "Cluster: " + str(i_cluster) + "<br>"
            for t in X.index:
                HTML += "    {:>45s}".format(t) + "<br>"
            HTML += "<br>"
        return widgets.HTML("<pre>" + HTML + "</pre>")

    def cluster_plot(self):
        ##
        self.apply()
        ##

        fig = pyplot.Figure(figsize=(self.width, self.height))
        ax = fig.subplots()
        #  cmap=pyplot.cm.get_cmap(self.cmap)
        cmap = pyplot.cm.get_cmap("Greys")

        x = self.centers_["Dim-{:>02d}".format(self.x_axis)]
        y = self.centers_["Dim-{:>02d}".format(self.y_axis)]
        names = self.centers_["Name"]
        node_sizes = cmn.counters_to_node_sizes(names)
        node_colors = cmn.counters_to_node_colors(names, cmap)
        # edge_colors = cmn.counters_to_edgecolors(names, cmap)

        from cycler import cycler

        ax.scatter(
            x,
            y,
            marker="o",
            s=node_sizes,
            c=node_colors,
            alpha=0.5,
            linewidths=2,
            #  edgecolors=node_colors),
        )

        pos = {term: (x[idx], y[idx]) for idx, term in enumerate(self.centers_.Name)}
        cmn.ax_text_node_labels(
            ax=ax, labels=self.centers_.Name, dict_pos=pos, node_sizes=node_sizes
        )

        cmn.ax_expand_limits(ax)
        cmn.set_ax_splines_invisible(ax)
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5, zorder=-1)
        ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.5, zorder=-1)
        ax.set_axis_off()
        fig.set_tight_layout(True)

        return fig


###############################################################################
##
##  DASHBOARD
##
###############################################################################

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

        #
        self.app_title = "Latent Semantic Analysis"
        self.menu_options = [
            "Memberships",
            "Cluster plot",
        ]
        #
        self.panel_widgets = [
            dash.dropdown(
                desc="Column:", options=[z for z in COLUMNS if z in data.columns],
            ),
            dash.min_occurrence(),
            dash.max_items(),
            dash.separator(text="Decomposition"),
            dash.dropdown(desc="Apply to:", options=["TF matrix", "TF*IDF matrix",],),
            dash.dropdown(
                desc="Method:",
                options=["Factor Analysis", "PCA", "Fast ICA", "SVD", "MDS"],
            ),
            dash.n_components(),
            dash.random_state(),
            dash.separator(text="Aglomerative Clustering"),
            dash.n_clusters(),
            dash.affinity(),
            dash.linkage(),
            dash.separator(text="Visualization"),
            dash.dropdown(desc="Top by:", options=["Num Documents", "Times Cited"],),
            dash.top_n(),
            dash.x_axis(),
            dash.y_axis(),
            dash.fig_width(),
            dash.fig_height(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)

        if self.menu == "Memberships":
            self.set_disabled("X-axis:")
            self.set_disabled("Y-axis:")
            self.set_disabled("Width:")
            self.set_disabled("Height:")

        if self.menu == "Cluster plot":
            self.set_enabled("X-axis:")
            self.set_enabled("Y-axis:")
            self.set_enabled("Width:")
            self.set_enabled("Height:")

        self.set_options(name="X-axis:", options=list(range(self.n_components)))
        self.set_options(name="Y-axis:", options=list(range(self.n_components)))


###############################################################################
##
##  EXTERNAL INTERFACE
##
###############################################################################


def app(data, limit_to=None, exclude=None, years_range=None):
    return DASHapp(
        data=data, limit_to=limit_to, exclude=exclude, years_range=years_range
    ).run()


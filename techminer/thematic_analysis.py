import re
import textwrap
import matplotlib
import matplotlib.pyplot as pyplot
import pandas as pd
import ipywidgets as widgets

import techminer.core.dashboard as dash
from techminer.core import (
    CA,
    DASH,
    TF_matrix,
    TFIDF_matrix,
    limit_to_exclude,
    add_counters_to_axis,
    clustering,
    corpus_filter,
    sort_by_axis,
)
from techminer.plots import ax_text_node_labels
from techminer.plots import bubble_plot as bubble_plot_
from techminer.plots import (
    counters_to_node_colors,
    counters_to_node_sizes,
    expand_ax_limits,
    set_spines_invisible,
    xy_clusters_plot,
    xy_cluster_members_plot,
)
from techminer.core.thesaurus import read_textfile

from techminer.core.explode import explode

###############################################################################
##
##  MODEL
##
###############################################################################


class Model:
    def __init__(
        self,
        data,
        thesaurus_file,
        limit_to,
        exclude,
        years_range,
        clusters=None,
        cluster=None,
    ):
        ##
        if years_range is not None:
            initial_year, final_year = years_range
            data = data[(data.Year >= initial_year) & (data.Year <= final_year)]

        ## Filter for cluster members
        if clusters is not None and cluster is not None:
            data = corpus_filter(data=data, clusters=clusters, cluster=cluster)

        self.data = data
        self.thesaurus_file = thesaurus_file
        self.limit_to = limit_to
        self.exclude = exclude

        self.y_axis = None
        self.column = None
        self.min_occurrence = None
        self.max_items = None
        self.n_labels = None
        self.clustering_method = None
        self.affinity = None
        self.linkage = None
        self.top_by = None
        self.random_state = None
        self.top_n = None
        self.width = None
        self.height = None
        self.cmap = None
        self.x_axis = None
        self.global_citations_ = None
        self.min_co_occurrence_within = None

    def apply(self):

        ##
        ## Fuente:
        ##   https://tlab.it/en/allegati/help_en_online/mrepert.htm
        ##
        data = self.data[[self.column, "ID"]].dropna()

        ##
        ##  Construye TF_matrix binaria
        ##
        TF_matrix_ = TF_matrix(
            data,
            self.column,
            scheme="binary",
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
        ## Add counters to axis
        ##

        column = {
            "Abstract_Author_Keywords_CL": "Author_Keywords_CL",
            "Abstract_Author_Keywords": "Author_Keywords",
            "Abstract_Index_Keywords_CL": "Index_Keywords_CL",
            "Abstract_Index_Keywords": "Index_Keywords",
            "Abstract_Keywords_CL": "Keywords_CL",
            "Abstract_Keywords": "Keywords",
        }[self.column]

        TF_matrix_ = add_counters_to_axis(
            X=TF_matrix_, axis=1, data=self.data, column=column
        )

        ##
        ## Minimal co-occurence within phrases
        ##
        TF_matrix_ = sort_by_axis(
            data=TF_matrix_, sort_by="Num_Documents", ascending=False, axis=1
        )
        TF_matrix_ = TF_matrix_.loc[:, TF_matrix_.columns[0 : self.max_items]]

        ##
        ## Minimal co-occurrence within abstracts
        ##
        m = TF_matrix_.sum(axis=1)
        m = m[m >= self.min_co_occurrence_within]
        TF_matrix_ = TF_matrix_.loc[m.index.tolist(), :]

        ##
        ##  Construye TF-IDF y escala filas to longitud unitaria (norma euclidiana).
        ##      En sklearn: norm='l2'
        ##
        ##      tf-idf = tf * (log(N / df) + 1)
        ##
        TF_IDF_matrix_ = TFIDF_matrix(
            TF_matrix=TF_matrix_,
            norm="l2",
            use_idf=True,
            smooth_idf=False,
            sublinear_tf=False,
            max_items=self.max_items,
        )

        #  for a, b in zip(TF_matrix_.index, TF_IDF_matrix_.index):
        #    print(a, b)

        ##
        ##  Clustering de las filas de TF_IDF_matrix_.
        ##      En TLAB se usa bisecting k-means.
        ##      Se implementa sklearn.cluster.KMeans
        ##
        (
            self.n_clusters,
            self.labels_,
            self.cluster_members_,
            self.cluster_centers_,
            self.cluster_names_,
        ) = clustering(
            X=TF_IDF_matrix_,
            method=self.clustering_method,
            n_clusters=self.n_clusters,
            affinity=self.affinity,
            linkage=self.linkage,
            random_state=self.random_state,
            top_n=None,
            name_prefix="Theme {}",
            documents=True,
        )

        ##
        ## Column names in cluster members table
        ##
        self.cluster_members_.columns = [
            "Theme {:>2d}".format(i) for i in range(self.n_clusters)
        ]

        ##
        ##  Matriz de contingencia.
        ##
        matrix = TF_matrix_.loc[TF_IDF_matrix_.index, TF_IDF_matrix_.columns].copy()
        matrix["*cluster*"] = self.labels_
        matrix = matrix.groupby(by="*cluster*").sum()
        matrix.index = ["Theme {:>2d}".format(i) for i in range(self.n_clusters)]
        self.contingency_table_ = matrix.transpose()

        ##
        ## Keywords by Theme
        ##
        self.keywords_by_theme_ = self.contingency_table_.copy()
        self.keywords_by_theme_.index = self.keywords_by_theme_.index.map(
            lambda w: " ".join(w.split(" ")[:-1])
        )
        for column in self.keywords_by_theme_.columns:
            x = self.keywords_by_theme_[column]
            x = x.sort_values(ascending=False)
            x = [k if v > 0 else pd.NA for k, v in zip(x.index, x)]
            self.keywords_by_theme_[column] = x
        self.keywords_by_theme_.index = list(range(len(self.keywords_by_theme_)))

        ##
        ## Remove NA from keywords_by_theme
        ##
        selected = []
        for i in self.keywords_by_theme_.index:
            x = self.keywords_by_theme_.loc[i, :].tolist()
            x = all([pd.isna(m) for m in x])
            if x is False:
                selected.append(i)
        self.keywords_by_theme_ = self.keywords_by_theme_.loc[selected, :]
        self.keywords_by_theme_ = self.keywords_by_theme_.applymap(
            lambda w: "" if pd.isna(w) else w
        )

        ##
        ##  Top n for contingency table
        ##
        self.contingency_table_ = sort_by_axis(
            data=self.contingency_table_, sort_by=self.top_by, ascending=False, axis=0
        )
        self.contingency_table_ = self.contingency_table_.head(self.top_n)

        ##
        ## Tamaño de los clusters
        ##
        W = pd.DataFrame({"CLUSTER": self.labels_})
        W["ID"] = TF_IDF_matrix_.index.tolist()
        W = W.groupby(["CLUSTER"]).count()["ID"].tolist()
        self.num_documents_ = W

        ##
        ##  Correspondence Analysis
        ##
        try:
            ca = CA()
            ca.fit(X=self.contingency_table_)
            self.cluster_ppal_coordinates_ = ca.principal_coordinates_cols_
            self.term_ppal_coordinates_ = ca.principal_coordinates_rows_
        except:
            self.cluster_ppal_coordinates_ = None
            self.term_ppal_coordinates_ = None

    def keywords_by_theme(self):
        self.apply()
        return self.keywords_by_theme_

    def documents_by_theme(self):
        self.apply()
        return self.cluster_members_

    def contingency_table(self):
        self.apply()
        return self.contingency_table_

    def meaningful_contexts(self):

        self.apply()

        ##
        ## Obtain keywords by theme
        ##
        M = self.cluster_members_.copy()
        M = M.applymap(lambda w: pd.NA if w == "" else w)

        HTML = ""

        for i_theme, _ in enumerate(M.columns):

            keywords = self.keywords_by_theme_[
                self.keywords_by_theme_.columns[i_theme]
            ].tolist()
            keywords = [k for k in keywords if k != ""]

            ##
            ## Adds keyword equivalents
            ##
            complementary_keywords = []
            if self.column[-3:] == "_CL":
                th = read_textfile(self.thesaurus_file)
                for k in keywords.copy():
                    if k in th._thesaurus.keys():
                        complementary_keywords += th._thesaurus[k]
                complementary_keywords = list(
                    set(complementary_keywords) - set(keywords)
                )
            else:
                complementary_keywords = None

            if complementary_keywords is not None:
                sorted_keywords = sorted(
                    keywords + complementary_keywords,
                    key=lambda w: len(w.split(" ")),
                    reverse=True,
                )
            else:
                sorted_keywords = sorted(
                    keywords, key=lambda w: len(w.split(" ")), reverse=True
                )

            HTML += "*" * 83 + "<br><br>"
            HTML += "Theme {}".format(i_theme) + "<br><br>"
            HTML += "*" * 83 + "<br><br>"
            HTML += "Keywords:<br>"
            for k in keywords:
                HTML += "    " + k + "<br>"
            if complementary_keywords is not None:
                HTML += "    " + "-" * 30 + "<br>"
                for k in sorted(complementary_keywords):
                    HTML += "    " + k + "<br>"
            HTML += "<br>"

            i_documents = M[M.columns[i_theme]].dropna()

            data = self.data.loc[i_documents, :].copy()
            data = data.sort_values(["Global_Citations"], ascending=False)
            data = data.head(10)

            for i_document in data.index:

                document = data.loc[i_document, :]

                doc_ID = (
                    document.Authors.replace(";", ", ")
                    + ". "
                    + document.Historiograph_ID
                    + ". ID: "
                    + str(i_document)
                    + ". Times Cited: "
                    + str(int(document.Global_Citations))
                )
                doc_ID = textwrap.wrap(doc_ID, 80)

                HTML += "-" * 83 + "<br>"
                for text in doc_ID:
                    HTML += text + "<br>"
                HTML += "<br>"

                abstract = document.Abstract

                for keyword in sorted_keywords:
                    pattern = re.compile(r"\b" + keyword + r"\b", re.IGNORECASE)
                    abstract = pattern.sub(
                        "<b>" + keyword.upper().replace(" ", "_") + "</b>", abstract
                    )

                abstract = abstract.replace("_", " ")

                phrases = textwrap.wrap(abstract, 80)
                for line in phrases:
                    HTML += line + "<br>"
                HTML += "<br><br>"

        return widgets.HTML("<pre>" + HTML + "</pre>")

    def cluster_members(self):
        self.apply()
        return self.cluster_members_

    def clusters_plot(self):

        self.apply()

        if self.cluster_ppal_coordinates_ is None:
            return widgets.HTML(
                "<pre>Plot unavailable. Failed convergence for correspondence analysis.</pre>"
            )

        labels = [
            "THEME_{} {}".format(index, label)
            for index, label in enumerate(self.cluster_names_)
        ]

        node_sizes = self.num_documents_
        min_size = min(node_sizes)
        max_size = max(node_sizes)
        if max_size == min_size:
            node_sizes = [1000] * node_sizes
        else:
            node_sizes = [
                500 + int(2500 * (w - min_size) / (max_size - min_size))
                for w in node_sizes
            ]

        return xy_clusters_plot(
            x=self.cluster_ppal_coordinates_["Dim-{}".format(self.x_axis)],
            y=self.cluster_ppal_coordinates_["Dim-{}".format(self.y_axis)],
            x_axis_at=0,
            y_axis_at=0,
            labels=labels,
            node_sizes=node_sizes,
            color_scheme=self.colors,
            xlabel="Dim-{}".format(self.x_axis),
            ylabel="Dim-{}".format(self.y_axis),
            figsize=(self.width, self.height),
        )

        x = self.cluster_ppal_coordinates_[
            self.cluster_ppal_coordinates_.columns[self.x_axis]
        ]
        y = self.cluster_ppal_coordinates_[
            self.cluster_ppal_coordinates_.columns[self.y_axis]
        ]

        matplotlib.rc("font", size=11)
        fig = pyplot.Figure(figsize=(self.width, self.height))
        ax = fig.subplots()
        cmap = pyplot.cm.get_cmap(self.cmap)

        node_sizes = self.num_documents_
        max_size = max(node_sizes)
        min_size = min(node_sizes)
        node_sizes = [
            500 + int(2500 * (w - min_size) / (max_size - min_size)) for w in node_sizes
        ]

        node_colors = self.global_citations_.values()
        max_colors = max(node_colors)
        min_colors = min(node_colors)
        node_colors = [
            cmap(0.2 + 0.80 * (i - min_colors) / (max_colors - min_colors))
            for i in node_colors
        ]

        ax.scatter(
            x,
            y,
            marker="o",
            s=node_sizes,
            alpha=1.0,
            c=node_colors,
            edgecolors="k",
            zorder=1,
        )

        ax.axhline(
            y=0,
            color="gray",
            linestyle="--",
            linewidth=0.5,
            zorder=-1,
        )
        ax.axvline(
            x=0,
            color="gray",
            linestyle="--",
            linewidth=1,
            zorder=-1,
        )

        dict_pos = {
            key: (x_, y_) for key, x_, y_ in zip(self.cluster_names_.keys(), x, y)
        }
        ax_text_node_labels(
            ax=ax, labels=self.cluster_names_, dict_pos=dict_pos, node_sizes=node_sizes
        )

        set_spines_invisible(ax)
        expand_ax_limits(ax)
        ax.axis("off")

        fig.set_tight_layout(True)

        return fig

    def keywords_plot(self):

        if self.cluster_ppal_coordinates_ is None:
            return widgets.HTML(
                "<pre>Plot unavailable. Failed convergence for correspondence analysis.</pre>"
            )

        self.apply()
        x = self.term_ppal_coordinates_[
            self.term_ppal_coordinates_.columns[self.x_axis]
        ]
        y = self.term_ppal_coordinates_[
            self.term_ppal_coordinates_.columns[self.y_axis]
        ]

        matplotlib.rc("font", size=11)
        fig = pyplot.Figure(figsize=(self.width, self.height))
        ax = fig.subplots()
        cmap = pyplot.cm.get_cmap(self.cmap)

        node_sizes = counters_to_node_sizes(self.term_ppal_coordinates_.index)
        node_colors = counters_to_node_colors(self.term_ppal_coordinates_.index, cmap)

        ax.scatter(
            x,
            y,
            marker="o",
            s=node_sizes,
            alpha=1.0,
            c=node_colors,
            edgecolors="k",
            zorder=1,
        )

        ax.axhline(
            y=0,
            color="gray",
            linestyle="--",
            linewidth=0.5,
            zorder=-1,
        )
        ax.axvline(
            x=0,
            color="gray",
            linestyle="--",
            linewidth=1,
            zorder=-1,
        )

        dict_pos = {
            key: (x_, y_)
            for key, x_, y_ in zip(self.term_ppal_coordinates_.index, x, y)
        }
        ax_text_node_labels(
            ax=ax,
            labels=self.term_ppal_coordinates_.index,
            dict_pos=dict_pos,
            node_sizes=node_sizes,
        )

        set_spines_invisible(ax)
        expand_ax_limits(ax)
        ax.axis("off")

        fig.set_tight_layout(True)

        return fig


###############################################################################
##
##  DASHBOARD
##
###############################################################################

COLUMNS = [
    "Abstract_Author_Keywords_CL",
    "Abstract_Author_Keywords",
    "Abstract_Index_Keywords_CL",
    "Abstract_Index_Keywords",
    "Abstract_Keywords_CL",
    "Abstract_Keywords",
]


class DASHapp(DASH, Model):
    def __init__(
        self,
        data,
        thesaurus_file,
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
            thesaurus_file=thesaurus_file,
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=clusters,
            cluster=cluster,
        )
        DASH.__init__(self)

        self.app_title = "Thematic Analysis"
        self.menu_options = [
            "Keywords by theme",
            "Documents by theme",
            "Meaningful contexts",
            "Contingency table",
            "Clusters plot",
            "Keywords plot",
        ]

        self.panel_widgets = [
            dash.dropdown(
                desc="Column:",
                options=[z for z in sorted(COLUMNS) if z in data.columns],
            ),
            dash.min_occurrence(),
            dash.max_items(),
            dash.dropdown(
                desc="Min co-occurrence within:",
                options=[1, 2, 3, 4, 5],
            ),
            dash.separator(text="Clustering"),
            dash.clustering_method(),
            dash.n_clusters(m=3, n=50, i=1),
            dash.affinity(),
            dash.linkage(),
            dash.random_state(),
            dash.separator(text="Visualization"),
            dash.dropdown(
                desc="Top by:",
                options=[
                    "Num Documents",
                    "Global Citations",
                ],
            ),
            dash.top_n(
                n=101,
            ),
            dash.dropdown(
                desc="Colors:",
                options=[
                    "4 Quadrants",
                    "Clusters",
                    "Greys",
                    "Purples",
                    "Blues",
                    "Greens",
                    "Oranges",
                    "Reds",
                ],
            ),
            dash.x_axis(),
            dash.y_axis(),
            dash.fig_width(),
            dash.fig_height(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)

        self.panel_widgets[-4]["widget"].options = list(range(self.n_clusters))
        self.panel_widgets[-3]["widget"].options = list(range(self.n_clusters))

        for i in [-1, -2, -3, -4, -5]:
            self.panel_widgets[i]["widget"].disabled = self.menu in [
                "Contingency table",
                "Cluster members",
                "Cluster ppal coordinates",
                "Term ppal coordinates",
            ]


###############################################################################
##
##  EXTERNAL INTERFACE
##
###############################################################################


def thematic_analysis(
    input_file="techminer.csv",
    thesaurus_file="keywords_thesaurus.txt",
    limit_to=None,
    exclude=None,
    years_range=None,
    clusters=None,
    cluster=None,
):
    return DASHapp(
        data=pd.read_csv(input_file),
        thesaurus_file=thesaurus_file,
        limit_to=limit_to,
        exclude=exclude,
        years_range=years_range,
        clusters=clusters,
        cluster=cluster,
    ).run()

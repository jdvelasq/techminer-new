import numpy as np
import pandas as pd

import techminer.core.dashboard as dash
from techminer.by_year_analysis import by_year_analysis
from techminer.core import (
    DASH,
    add_counters_to_axis,
    corpus_filter,
    explode,
    sort_axis,
    sort_by_axis,
)
from techminer.core.dashboard import max_items, min_occurrence

from techminer.plots import bubble_plot, gant0_plot, gant_plot, heatmap

TEXTLEN = 40


class BaseModel:
    def __init__(
        self,
        data,
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

        #
        # Filter for cluster members
        #
        if clusters is not None and cluster is not None:
            data = corpus_filter(data=data, clusters=clusters, cluster=cluster)

        self.data = data
        self.limit_to = limit_to
        self.exclude = exclude

    def build_table(self):

        x = self.data.copy()

        ##
        ##  Number of documents and times cited by term per year
        ##
        x = explode(x[["Year", self.column, "Global_Citations", "ID"]], self.column)
        x["Num_Documents"] = 1
        result = x.groupby([self.column, "Year"], as_index=False).agg(
            {"Global_Citations": np.sum, "Num_Documents": np.size}
        )
        result = result.assign(
            ID=x.groupby([self.column, "Year"]).agg({"ID": list}).reset_index()["ID"]
        )
        result["Global_Citations"] = result["Global_Citations"].map(lambda x: int(x))

        ##
        ##  Summary per year
        ##
        summ = explode(x[["Year", "Global_Citations", "ID"]], "Year")
        summ.loc[:, "Num_Documents"] = 1
        summ = summ.groupby("Year", as_index=True).agg(
            {"Global_Citations": np.sum, "Num_Documents": np.size}
        )

        ##
        ##  Dictionaries using the year as a key
        ##
        num_documents_by_year = {
            key: value for key, value in zip(summ.index, summ.Num_Documents)
        }
        global_citations_by_year = {
            key: value for key, value in zip(summ.index, summ.Global_Citations)
        }

        ##
        ##  Indicators from ScientoPy
        ##
        result["summary_documents_by_year"] = result.Year.apply(
            lambda w: num_documents_by_year[w]
        )
        result["summary_documents_by_year"] = result.summary_documents_by_year.map(
            lambda w: 1 if w == 0 else w
        )
        result["summary_global_citations_by_year"] = result.Year.apply(
            lambda w: global_citations_by_year[w]
        )
        result[
            "summary_global_citations_by_year"
        ] = result.summary_global_citations_by_year.map(lambda w: 1 if w == 0 else w)

        result["Perc_Num_Documents"] = 0.0
        result = result.assign(
            Perc_Num_Documents=round(
                result.Num_Documents / result.summary_documents_by_year * 100, 2
            )
        )

        result["Perc_Global_Citations"] = 0.0
        result = result.assign(
            Perc_Global_Citations=round(
                result.Global_Citations / result.summary_global_citations_by_year * 100,
                2,
            )
        )

        result.pop("summary_documents_by_year")
        result.pop("summary_global_citations_by_year")

        result = result.rename(
            columns={
                "Num_Documents": "Num_Documents_per_Year",
                "Global_Citations": "Global_Citations_per_Year",
                "Perc_Num_Documents": "%_Num_Documents_per_Year",
                "Perc_Global_Citations": "%_Global_Citations_per_Year",
            }
        )

        ## Limit to
        limit_to = self.limit_to
        if isinstance(limit_to, dict):
            if self.column in limit_to.keys():
                limit_to = limit_to[self.column]
            else:
                limit_to = None

        if limit_to is not None:
            result = result[result[self.column].map(lambda w: w in limit_to)]

        ## Exclude
        exclude = self.exclude
        if isinstance(exclude, dict):
            if self.column in exclude.keys():
                exclude = exclude[self.column]
            else:
                exclude = None

        if exclude is not None:
            result = result[result[self.column].map(lambda w: w not in exclude)]

        return result

    def table(self):
        ###
        self.apply()
        ###
        if self.cmap is not None:
            return self.X_.style.background_gradient(cmap=self.cmap, axis=0)
        return self.X_


##
##
##
##  M A T R I X
##
##
##

###############################################################################
##
##  MODEL
##
###############################################################################


class MatrixModel(BaseModel):
    def __init__(
        self,
        data,
        limit_to,
        exclude,
        years_range,
        clusters=None,
        cluster=None,
    ):
        ##
        BaseModel.__init__(
            self,
            data=data,
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=clusters,
            cluster=cluster,
        )

        self.top_by = None
        self.sort_by = None
        self.ascending = None
        self.column = None
        self.cmap = None

    def apply(self):

        result = self.build_table()

        if isinstance(self.top_by, str):
            top_by = self.top_by.replace(" ", "_")
            top_by = {
                "Num_Documents_per_Year": 0,
                "Global_Citations_per_Year": 1,
                "%_Num_Documents_per_Year": 2,
                "%_Global_Citations_per_Year": 3,
                "Num_Documents": 4,
                "Global_Citations": 5,
            }[top_by]
        else:
            top_by = self.top_by

        selected_col = {
            0: "Num_Documents_per_Year",
            1: "Global_Citations_per_Year",
            2: "%_Num_Documents_per_Year",
            3: "%_Global_Citations_per_Year",
            4: "Num_Documents_per_Year",
            5: "Global_Citations_per_Year",
        }[top_by]

        for col in [
            "Num_Documents_per_Year",
            "Global_Citations_per_Year",
            "%_Num_Documents_per_Year",
            "%_Global_Citations_per_Year",
        ]:

            if col != selected_col:
                result.pop(col)

        ##
        ## Table pivot
        ##
        result = pd.pivot_table(
            result,
            values=selected_col,
            index="Year",
            columns=self.column,
            fill_value=0,
        )

        ##
        ## Min occurrence
        ##
        result = add_counters_to_axis(
            X=result, axis=1, data=self.data, column=self.column
        )
        result = sort_axis(data=result, num_documents=True, axis=1, ascending=False)
        columns = [
            column
            for column in result.columns
            if int(column.split(" ")[-1].split(":")[0]) >= self.min_occurrence
        ]
        result = result.loc[:, columns]

        if top_by == 4:
            ##
            ## top_by num documents
            ##
            result = sort_axis(data=result, num_documents=True, axis=1, ascending=False)
            selected_columns = result.columns[: self.max_items]
            result = result[selected_columns]

        elif top_by == 5:
            ##
            ## top_by times cited
            ##
            result = sort_axis(
                data=result, num_documents=False, axis=1, ascending=False
            )
            selected_columns = result.columns[: self.max_items]
            result = result[selected_columns]

        else:

            max = result.max(axis=0)
            max = max.sort_values(ascending=False)
            max = max.head(self.max_items)
            result = result[max.index]

        sum_years = result.sum(axis=1)
        for year, index in zip(sum_years, sum_years.index):
            if year == 0:
                result = result.drop(axis=0, labels=index)
            else:
                break

        #
        # sort_by
        #
        if self.sort_by == "Values":
            columns = result.max(axis=0)
            columns = columns.sort_values(ascending=self.ascending)
            columns = columns.index.tolist()
            result = result[columns]
        else:
            result = sort_by_axis(
                data=result, sort_by=self.sort_by, ascending=self.ascending, axis=1
            )

        self.X_ = result

    def matrix(self):
        ##
        self.apply()
        ##
        if self.cmap is None:
            return self.X_
        else:
            return self.X_.style.background_gradient(cmap=self.cmap, axis=None)

    def heatmap(self):
        ##
        self.apply()
        ##
        return heatmap(
            X=self.X_.transpose(), cmap=self.cmap, figsize=(self.width, self.height)
        )

    def bubble_plot(self):
        ##
        self.apply()
        ##
        return bubble_plot(
            X=self.X_.transpose(),
            darkness=None,
            cmap=self.cmap,
            figsize=(self.width, self.height),
        )

    def gant(self):
        ##
        self.apply()
        ##
        return gant_plot(X=self.X_, cmap=self.cmap, figsize=(self.width, self.height))

    def gant0(self):
        ##
        self.apply()
        ##
        return gant0_plot(x=self.X_, figsize=(self.width, self.height))


###############################################################################
##
##  DASHBOARD
##
###############################################################################


class MatrixDASHapp(DASH, MatrixModel):
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

        MatrixModel.__init__(
            self,
            data=data,
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=clusters,
            cluster=cluster,
        )
        DASH.__init__(self)

        COLUMNS = sorted(
            [column for column in data.columns if column != "Abstract_phrase_words"]
        )

        self.app_title = "Term by Year Analysis"
        self.menu_options = ["Matrix", "Heatmap", "Bubble plot", "Gant", "Gant0"]

        self.panel_widgets = [
            dash.dropdown(
                desc="Column:",
                options=[z for z in COLUMNS if z in data.columns],
            ),
            dash.min_occurrence(),
            dash.max_items(),
            dash.separator(text="Visualization"),
            dash.dropdown(
                desc="Top by:",
                options=[
                    "Num Documents per Year",
                    "Global Citations per Year",
                    "% Num Documents per Year",
                    "% Global Citations per Year",
                    "Num Documents",
                    "Global Citations",
                ],
            ),
            dash.dropdown(
                desc="Sort by:",
                options=["Alphabetic", "Values", "Num Documents", "Global Citations"],
            ),
            dash.ascending(),
            dash.cmap(),
            dash.fig_width(),
            dash.fig_height(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)

        if self.menu == "Matrix":
            self.set_disabled("Width:")
            self.set_disabled("Height:")
        else:
            self.set_enabled("Width:")
            self.set_enabled("Height:")


##
##
##
##  M A T R I X   L I S T
##
##
##

###############################################################################
##
##  MODEL
##
###############################################################################


class MatrixListModel(BaseModel):
    def __init__(self, data, limit_to, exclude, years_range):
        ##
        BaseModel.__init__(
            self,
            data=data,
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=None,
            cluster=None,
        )

    def apply(self):
        #
        result = self.build_table()

        ## top_n
        if isinstance(self.top_by, str):
            top_by = self.top_by.replace(" ", "_")
            top_by = {
                "Num_Documents_per_Year": 0,
                "Global_Citations_per_Year": 1,
                "%_Num_Documents_per_Year": 2,
                "%_Global_Citations_per_Year": 3,
                "Num_Documents": 4,
                "Global_Citations": 5,
            }[top_by]
        else:
            top_by = self.top_by

        columns = {
            0: ["Num_Documents_per_Year", "Global_Citations_per_Year"],
            1: ["Global_Citations_per_Year", "Num_Documents_per_Year"],
            2: ["%_Num_Documents_per_Year", "%_Global_Citations_per_Year"],
            3: ["%_Global_Citations_per_Year", "%_Num_Documents_per_Year"],
            4: ["Num_Documents", "Global_Citations"],
            5: ["Global_Citations", "Num_Documents"],
        }[top_by]

        result.sort_values(
            columns,
            ascending=False,
            inplace=True,
        )

        if self.top_n is not None:
            result = result.head(self.top_n)
            result = result.reset_index(drop=True)

        ## sort_by
        if isinstance(self.sort_by, str):
            sort_by = self.sort_by.replace(" ", "_")
            sort_by = {
                "Alphabetic": 0,
                "Year": 1,
                "Num_Documents_per_Year": 2,
                "Global_Citations_per_Year": 3,
                "%_Num_Documents_per_Year": 4,
                "%_Global_Citations_per_Year": 5,
            }[sort_by]
        else:
            sort_by = self.sort_by

        if isinstance(self.ascending, str):
            self.ascending = {
                "True": True,
                "False": False,
            }[self.ascending]

        if sort_by == 0:
            result = result.sort_values([self.column], ascending=self.ascending)
        else:
            result = result.sort_values(
                {
                    1: ["Year", "Num_Documents_per_Year", "Global_Citations_per_Year"],
                    2: ["Num_Documents_per_Year", "Global_Citations_per_Year", "Year"],
                    3: ["Global_Citations_per_Year", "Num_Documents_per_Year", "Year"],
                    4: [
                        "%_Num_Documents_per_Year",
                        "%_Global_Citations_per_Year",
                        "Year",
                    ],
                    5: [
                        "%_Global_Citations_per_Year",
                        "%_Num_Documents_per_Year",
                        "Year",
                    ],
                }[sort_by],
                ascending=self.ascending,
            )

        ###
        result.index = result[self.column]
        result = add_counters_to_axis(
            X=result, axis=0, data=self.data, column=self.column
        )
        result[self.column] = result.index
        result = result.reset_index(drop=True)
        ###
        result.pop("ID")
        result = result[
            [
                self.column,
                "Year",
                "Num_Documents_per_Year",
                "Global_Citations_per_Year",
                "%_Num_Documents_per_Year",
                "%_Global_Citations_per_Year",
            ]
        ]
        ###
        self.X_ = result


###############################################################################
##
##  DASHBOARD
##
###############################################################################


class MatrixListDASHapp(DASH, MatrixListModel):
    def __init__(
        self,
        data,
        limit_to=None,
        exclude=None,
        years_range=None,
        clusters=None,
        cluster=None,
    ):

        MatrixListModel.__init__(
            self,
            data=data,
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=clusters,
            cluster=cluster,
        )
        DASH.__init__(self)

        COLUMNS = sorted([column for column in data.columns])

        self.app_title = "Terms by Year Analysis"
        self.menu_options = [
            "Table",
        ]

        self.panel_widgets = [
            dash.dropdown(
                desc="Column:",
                options=[z for z in COLUMNS if z in data.columns],
            ),
            dash.separator(text="Visualization"),
            dash.dropdown(
                desc="Top by:",
                options=[
                    "Num Documents per Year",
                    "Global Citations per Year",
                    "% Num Documents per Year",
                    "% Global Citations per Year",
                ],
            ),
            dash.top_n(),
            dash.dropdown(
                desc="Sort by:",
                options=[
                    "Alphabetic",
                    "Year",
                    "Num Documents per Year",
                    "Global Citations per Year",
                    "% Num Documents per Year",
                    "% Global Citations per Year",
                ],
            ),
            dash.ascending(),
            dash.cmap(),
        ]
        super().create_grid()

    def interactive_output(self, **kwargs):

        DASH.interactive_output(self, **kwargs)


###############################################################################
##
##  EXTERNAL INTERFACE
##
###############################################################################


def by_term_per_year_analysis(
    input_file="techminer.csv",
    limit_to=None,
    exclude=None,
    tab=None,
    years_range=None,
    clusters=None,
    cluster=None,
):

    if tab == 1:
        return MatrixListDASHapp(
            data=pd.read_csv(input_file),
            limit_to=limit_to,
            exclude=exclude,
            years_range=years_range,
            clusters=clusters,
            cluster=cluster,
        ).run()

    return MatrixDASHapp(
        data=pd.read_csv(input_file),
        limit_to=limit_to,
        exclude=exclude,
        years_range=years_range,
        clusters=clusters,
        cluster=cluster,
    ).run()

import pandas as pd

from techminer.core.thesaurus import Thesaurus

#
# The algorithm searches in order until
# detect a match
#
NAMES = [
    "univ",
    "institut",
    "college",
    "bank",
    "banco",
    "centre",
    "center",
    "centro",
    "agency",
    "council",
    "commission",
    "politec",
    "polytechnic",
    "inc.",
    "ltd.",
    "office",
    "school",
    "department",
    "direction",
    "laboratory",
    "laboratoire",
    "colegio",
    "scuola",
    "ecole",
    "hospital",
    "association",
    "asociacion",
    "escuela",
    "company",
    "organization",
    "academy",
]


def create_institutions_thesaurus(
    input_file="techminer.csv", thesaurus_file="institutions_thesaurus.txt"
):
    #
    def search_name(w):

        ##
        ## Preprocessing
        ##
        w = w.lower().strip()

        ##
        ## Affiliation has a unique string without ','
        ##
        if len(w.split(",")) == 1:
            return w.strip().lower()

        ##
        ## Search for a possible match
        ##
        for name in NAMES:
            for elem in w.split(","):
                if name in elem:
                    selected_name = elem.strip().title()
                    selected_name = selected_name.replace(" De ", " de ")
                    selected_name = selected_name.replace(" Of ", " of ")
                    selected_name = selected_name.replace(" For ", " for ")

                    return selected_name

        ##
        ## No match found -> first part of the string
        ##
        if len(w.split(",")) == 2:
            selected_name = w.split(",")[0].strip()
            selected_name = selected_name.strip().title()
            selected_name = selected_name.replace(" De ", " de ")
            selected_name = selected_name.replace(" Of ", " of ")
            selected_name = selected_name.replace(" For ", " for ")
            return selected_name

        ##
        return w

    ##
    data = pd.read_csv(input_file)

    ##
    ## Creates a list of unique affiliations
    ##
    x = data.Affiliations
    x = x.dropna()
    x = x.map(lambda w: w.split(";"))
    x = x.explode()
    x = x.map(lambda w: w.strip())
    x = x.unique()

    ##
    ## Creates a dataframe for words and keys
    ##
    x = pd.DataFrame({"word": x.tolist(), "key": x.tolist()})

    ##
    ## Searches a possible name for the institution
    ##
    x["key"] = x.key.map(search_name)

    ##
    ## groupsby key
    ##
    grp = x.groupby(by="key").agg({"word": list})
    result = {
        key: value for key, value in zip(grp.index.tolist(), grp["word"].tolist())
    }

    Thesaurus(result, ignore_case=False, full_match=True, use_re=False).to_textfile(
        thesaurus_file
    )
    #


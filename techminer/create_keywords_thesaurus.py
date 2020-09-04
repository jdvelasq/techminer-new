import pandas as pd

from techminer.core.thesaurus import text_clustering
import os.path
from techminer.core.thesaurus import load_file_as_dict, Thesaurus


def create_keywords_thesaurus(
    input_file="techminer.csv", thesaurus_file="keywords_thesaurus.txt"
):

    ##
    ##  Loads keywords
    ##
    data = pd.read_csv(input_file)

    words_list = []

    if "Author_Keywords" in data.columns:
        words_list += data.Author_Keywords.tolist()

    if "Index_Keywords" in data.columns:
        words_list += data.Index_Keywords.tolist()

    if "Title_words" in data.columns:
        words_list += data.Title_words.tolist()

    if "Abstract_words" in data.columns:
        words_list += data.Abstract_words.tolist()

    ##
    ## Rules for keywords
    ##
    words_list = [words for words in words_list if not pd.isna(words)]
    words_list = [word for words in words_list for word in words.split(";")]
    words_list = [word for word in words_list if len(word.strip()) > 2]
    words_list = [
        word.replace('"', "")
        .replace(chr(8212), "")
        .replace(chr(8220), "")
        .replace(chr(8221), "")
        for word in words_list
    ]
    words_list = [
        word.replace("-", "") if word[0] == "-" and len(word) > 1 else word
        for word in words_list
    ]

    if os.path.isfile(thesaurus_file):

        ##
        ##  Loads existent thesaurus
        ##
        dict_ = load_file_as_dict(thesaurus_file)

        ##
        ##  Selects words to cluster
        ##
        clustered_words = [word for key in dict_.keys() for word in dict_[key]]
        words_list = [word for word in words_list if word not in clustered_words]

        if len(words_list) > 0:

            th = text_clustering(pd.Series(words_list))

            th = Thesaurus(
                x={**th._thesaurus, **dict_},
                ignore_case=True,
                full_match=False,
                use_re=False,
            )
            th.to_textfile(thesaurus_file)

    else:
        #
        # Creates a new thesaurus
        #
        text_clustering(pd.Series(words_list)).to_textfile(thesaurus_file)


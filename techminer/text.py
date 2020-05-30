# """
# Text manipulation
# ==================================================================================================

# This module contains functions for manipulating texts.


# Functions in this module
# ----------------------------------------------------------------------------------------

# """

import json
import re
from os.path import dirname, join

import pandas as pd


def extract_country(x):
    """Extracts country name from a string,

    Examples
    ----------------------------------------------------------------------------------------------

    >>> import pandas as pd
    >>> x = pd.DataFrame({
    ...     'AU_CO': [
    ...         'University, Cuba; University, Venezuela',
    ...         'University, United States; Univesrity, Singapore',
    ...         'University;',
    ...         'University; Univesity',
    ...         'University,',
    ...         'University',
    ...         None]
    ... })
    >>> x['AU_CO'].map(lambda x: extract_country(x))
    0             Cuba;Venezuela
    1    United States;Singapore
    2                       None
    3                       None
    4                       None
    5                       None
    6                       None
    Name: AU_CO, dtype: object
    
    """
    if x is None:
        return None
    #
    # lista generica de nombres de paises
    #
    module_path = dirname(__file__)
    with open(join(module_path, "data/worldmap.data"), "r") as f:
        countries = json.load(f)
    country_names = list(countries.keys())
    #
    # paises faltantes
    #
    country_names.append("Singapore")
    country_names.append("Malta")
    country_names.append("United States")
    #
    # Reemplazo de nombres de regiones administrativas
    # por nombres de paises
    #
    x = re.sub("Bosnia and Herzegovina", "Bosnia and Herz.", x)
    x = re.sub("Czech Republic", "Czechia", x)
    x = re.sub("Russian Federation", "Russia", x)
    x = re.sub("Hong Kong", "China", x)
    x = re.sub("Macau", "China", x)
    x = re.sub("Macao", "China", x)
    countries = [affiliation.split(",")[-1].strip() for affiliation in x.split(";")]
    countries = ";".join(
        [country if country in country_names else "" for country in countries]
    )
    if countries == "" or countries == ";":
        return None
    else:
        return countries


def extract_institution(x):
    """
    """

    def search_name(affiliation):
        if len(affiliation.split(",")) == 1:
            return item
        affiliation = affiliation.lower()
        for elem in affiliation.split(","):
            for name in names:
                if name in elem:
                    return elem
        return None

    #
    names = [
        "univ",
        "institut",
        "centre",
        "center",
        "centro",
        "agency",
        "council",
        "commission",
        "college",
        "politec",
        "inc.",
        "ltd.",
        "office",
        "department",
        "direction" "laboratory",
        "laboratoire",
        "colegio",
        "school",
        "scuola",
        "ecole",
        "hospital",
        "association",
        "asociacion",
        "company",
        "organization",
        "academy",
    ]

    if x is pd.isna(x) is True or x is None:
        return None
    institutions = []
    x = x.split(";")
    for item in x:
        institution = search_name(item)
        if institution is None:
            if len(item.split(",")) == 2:
                institution = item.split(",")[0]
        if institution is not None:
            institutions.append(institution)
    if institutions is not None:
        institutions = ";".join(institutions)
    return institutions


# import string


# from nltk.stem import PorterStemmer, SnowballStemmer


# def one_gram(x):
#     """Computes the 1-gram representation of string x.

#     See https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth

#     Args:
#         x (string): string to convert.

#     Returns:
#         string.


#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> one_gram('neural net')
#     'aelnrtu'


#     """
#     if x is None:
#         return None
#     x = x.strip().lower()
#     x = re.sub("-", " ", x)
#     x = re.sub("[" + string.punctuation + "]", "", x)
#     x = remove_accents(x)
#     x = x.replace(" ", "")
#     x = sorted(list(set(x)))
#     return "".join(x)


# def two_gram(x):
#     """Computes the 2-gram representation of string x.

#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> two_gram('neural net')
#     'aleteulnneraur'


#     """
#     if x is None:
#         return None
#     x = x.strip().lower()
#     x = re.sub("-", " ", x)
#     x = re.sub("[" + string.punctuation + "]", "", x)
#     x = remove_accents(x)
#     x = x.replace(" ", "")
#     x = list(x)
#     x = ["".join([x[i], x[i + 1]]) for i in range(len(x) - 1)]
#     x = sorted(list(set(x)))
#     return "".join(x)


# def stemmer_porter(x):
#     """Computes the stemmer transformation of string x.

#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> stemmer_porter('neural net')
#     'net neural'


#     """
#     if x is None:
#         return None
#     x = x.strip().lower()
#     x = re.sub("-", " ", x)
#     x = re.sub("[" + string.punctuation + "]", "", x)
#     x = remove_accents(x)
#     s = PorterStemmer()
#     x = sorted(set([s.stem(w) for w in x.split()]))
#     return " ".join(x)


# def stemmer_snowball(x):
#     """Computes the stemmer transformation of string x.

#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> stemmer_snowball('neural net')
#     'net neural'


#     """
#     if x is None:
#         return None
#     x = x.strip().lower()
#     x = re.sub("-", " ", x)
#     x = re.sub("[" + string.punctuation + "]", "", x)
#     x = remove_accents(x)
#     s = SnowballStemmer("english")
#     x = sorted(set([s.stem(w) for w in x.split()]))
#     return " ".join(x)


# def fingerprint(x):
#     """Computes 'fingerprint' representation of string x.

#     See https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth

#     Args:
#         x (string): string to convert.

#     Returns:
#         string.

#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> fingerprint('a A b')
#     'a b'
#     >>> fingerprint('b a a')
#     'a b'
#     >>> fingerprint(None) is None
#     True
#     >>> fingerprint('b c')
#     'b c'
#     >>> fingerprint(' c b ')
#     'b c'


#     """
#     if x is None:
#         return None
#     x = x.strip().lower()
#     x = re.sub("-", " ", x)
#     x = re.sub("[" + string.punctuation + "]", "", x)
#     x = remove_accents(x)
#     x = sorted(set(w for w in x.split()))
#     return " ".join(x)


# # def find_string(self, x):
# #     r"""Find patterns in string.

# #     Args:
# #         x (string)

# #     Returns:
# #         string or None


# #     Examples
# #     ----------------------------------------------------------------------------------------------

# #     >>> keywords = Keywords(r'\btwo\b', use_re=True)
# #     >>> keywords = keywords.compile()
# #     >>> keywords.find_string('one two three four five')
# #     'two'

# #     >>> keywords = Keywords(r'\bTWO\b', use_re=True)
# #     >>> keywords = keywords.compile()
# #     >>> keywords.find_string('one two three four five')
# #     'two'

# #     >>> keywords = Keywords(r'\btwo\b', ignore_case=False, use_re=True)
# #     >>> keywords = keywords.compile()
# #     >>> keywords.find_string('one TWO three four five') is None
# #     True

# #     >>> keywords = Keywords(r'\btwo\Wthree\b', ignore_case=False, use_re=True)
# #     >>> keywords = keywords.compile()
# #     >>> keywords.find_string('one two three four five')
# #     'two three'

# #     """
# #     for pattern in self._patterns:
# #         result = pattern.findall(x)
# #         if len(result):
# #             return result[0]
# #     return None

# # def replace_string(
# #     pattern, x, repl=None, ignore_case=True, full_match=False, use_re=False
# # ):
# #     """Replace pattern in string.

# #     Args:
# #         pattern (string)
# #         x (string)
# #         repl (string, None)
# #         ignore_case (bool)
# #         full_match (bool)
# #         use_re (bool)

# #     Returns:
# #         string or []

# #     """

# #     if use_re is False:
# #         pattern = re.escape(pattern)

# #     if full_match is True:
# #         pattern = "^" + pattern + "$"

# #     if ignore_case is True:
# #         return re.sub(pattern, repl, x, re.I)
# #     return re.sub(pattern, repl, x)


# def steamming(pattern, text):
#     """

#     Examples
#     ----------------------------------------------------------------------------------------------


#     """
#     text = remove_accents(text)
#     pattern = remove_accents(pattern)

#     text = text.strip().lower()
#     pattern = pattern.strip().lower()

#     porter = PorterStemmer()

#     pattern = [porter.stem(w) for w in pattern.split()]
#     text = [porter.stem(w) for w in text.split()]

#     return [m in text for m in pattern]


# def steamming_all(pattern, text):
#     """

#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> steamming_all('computers cars', 'car computing')
#     True

#     >>> steamming_all('computers cars', 'car houses')
#     False

#     """
#     return all(steamming(pattern, text))


# def steamming_any(pattern, text):
#     """

#     Examples
#     ----------------------------------------------------------------------------------------------

#     >>> steamming_any('computers cars', 'car computing')
#     True

#     >>> steamming_any('computers cars', 'computing house')
#     True

#     >>> steamming_all('computers cars', 'tree houses')
#     False

#     """
#     return any(steamming(pattern, text))


def remove_accents(text):
    """Translate non-ascii charaters to ascii equivalent. Based on Google Open Refine.

    Examples
    ----------------------------------------------------------------------------------------------

    >>> remove_accents('áéíóúñÁÉÍÓÚÑ')
    'aeiounAEIOUN'

    """

    def translate(c):

        if c in [
            "\u0100",
            "\u0102",
            "\u00C5",
            "\u0104",
            "\u00C0",
            "\u00C1",
            "\u00C2",
            "\u00C3",
            "\u00C4",
        ]:
            return "A"

        if c in [
            "\u00E0",
            "\u00E1",
            "\u00E2",
            "\u00E3",
            "\u00E4",
            "\u0103",
            "\u0105",
            "\u00E5",
            "\u0101",
        ]:
            return "a"

        if c in [
            "\u00C7",
            "\u0106",
            "\u0108",
            "\u010A",
            "\u010C",
        ]:
            return "C"

        if c in [
            "\u010D",
            "\u00E7",
            "\u0107",
            "\u010B",
            "\u0109",
        ]:
            return "c"

        if c in [
            "\u00D0",
            "\u010E",
            "\u0110",
        ]:
            return "D"

        if c in [
            "\u0111",
            "\u00F0",
            "\u010F",
        ]:
            return "d"

        if c in [
            "\u00C8",
            "\u00C9",
            "\u00CA",
            "\u00CB",
            "\u0112",
            "\u0114",
            "\u0116",
            "\u0118",
            "\u011A",
        ]:
            return "E"

        if c in [
            "\u011B",
            "\u0119",
            "\u00E8",
            "\u00E9",
            "\u00EA",
            "\u00EB",
            "\u0113",
            "\u0115",
            "\u0117",
        ]:
            return "e"

        if c in [
            "\u011C",
            "\u011E",
            "\u0120",
            "\u0122",
        ]:
            return "G"

        if c in [
            "\u0123",
            "\u011D",
            "\u011F",
            "\u0121",
        ]:
            return "g"

        if c in [
            "\u0124",
            "\u0126",
        ]:
            return "H"

        if c in [
            "\u0127",
            "\u0125",
        ]:
            return "h"

        if c in [
            "\u00CC",
            "\u00CD",
            "\u00CE",
            "\u00CF",
            "\u0128",
            "\u012A",
            "\u012C",
            "\u012E",
            "\u0130",
        ]:
            return "I"

        if c in [
            "\u0131",
            "\u012F",
            "\u012D",
            "\u00EC",
            "\u012B",
            "\u0129",
            "\u00EF",
            "\u00EE",
            "\u00ED",
            "\u017F",
        ]:
            return "i"

        if c in [
            "\u0134",
        ]:
            return "J"
        if c in [
            "\u0135",
        ]:
            return "j"

        if c in [
            "\u0136",
        ]:
            return "K"

        if c in [
            "\u0137",
            "\u0138",
        ]:
            return "k"

        if c in [
            "\u0139",
            "\u013B",
            "\u013D",
            "\u013F",
            "\u0141",
        ]:
            return "L"

        if c in [
            "\u0142",
            "\u013A",
            "\u013C",
            "\u013E",
            "\u0140",
        ]:
            return "l"

        if c in [
            "\u00D1",
            "\u0143",
            "\u0145",
            "\u0147",
        ]:
            return "N"

        if c in [
            "\u014B",
            "\u014A",
            "\u0149",
            "\u0148",
            "\u0146",
            "\u0144",
            "\u00F1",
        ]:
            return "n"

        if c in [
            "\u00D2",
            "\u00D3",
            "\u00D4",
            "\u00D5",
            "\u00D6",
            "\u00D8",
            "\u014C",
            "\u014E",
            "\u0150",
        ]:
            return "O"

        if c in [
            "\u0151",
            "\u00F2",
            "\u00F3",
            "\u00F4",
            "\u00F5",
            "\u00F6",
            "\u00F8",
            "\u014F",
            "\u014D",
        ]:
            return "o"

        if c in [
            "\u0154",
            "\u0156",
            "\u0158",
        ]:
            return "R"

        if c in [
            "\u0159",
            "\u0155",
            "\u0157",
        ]:
            return "r"

        if c in [
            "\u015A",
            "\u015C",
            "\u015E",
            "\u0160",
        ]:
            return "S"

        if c in [
            "\u0161",
            "\u015B",
            "\u015F",
            "\u015D",
        ]:
            return "s"

        if c in [
            "\u0162",
            "\u0164",
            "\u0166",
        ]:
            return "T"

        if c in [
            "\u0167",
            "\u0163",
            "\u0165",
        ]:
            return "t"

        if c in [
            "\u00D9",
            "\u00DA",
            "\u00DB",
            "\u00DC",
            "\u0168",
            "\u016A",
            "\u016E",
            "\u0170",
            "\u0172",
            "\u016C",
        ]:
            return "U"

        if c in [
            "\u0173",
            "\u00F9",
            "\u00FA",
            "\u00FB",
            "\u00FC",
            "\u0169",
            "\u016B",
            "\u016D",
            "\u0171",
            "\u016F",
        ]:
            return "u"

        if c in [
            "\u0174",
        ]:
            return "W"

        if c in [
            "\u0175",
        ]:
            return "w"

        if c in [
            "\u0178",
            "\u00DD",
            "\u0176",
        ]:
            return "Y"

        if c in [
            "\u0177",
            "\u00FD",
            "\u00FF",
        ]:
            return "y"

        if c in [
            "\u0179",
            "\u017B",
            "\u017D",
        ]:
            return "Z"

        if c in [
            "\u017E",
            "\u017A",
            "\u017C",
        ]:
            return "z"

        return c

    return "".join([translate(c) for c in text])


if __name__ == "__main__":

    import doctest

    doctest.testmod()

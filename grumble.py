import collections
from ctypes import Union
from pathlib import Path
import string
import sys
from typing import Dict, List, Tuple


normalMap = {'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
             'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'ª': 'A',
             'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
             'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
             'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
             'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
             'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
             'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'º': 'O',
             'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
             'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
             'Ñ': 'N', 'ñ': 'n',
             'Ç': 'C', 'ç': 'c',
             '§': 'S',  '³': '3', '²': '2', '¹': '1'}
normalize = str.maketrans(normalMap)

try:
    DICTIONARY = Path(__file__).parent / "data" / "gutenberg.txt"  # from http://www.3zsoftware.com/fr/listes.php
except:
    DICTIONARY =  Path(".") / "data" / "gutenberg.txt"  # from http://www.3zsoftware.com/fr/listes.php
SCOREMAP = {'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 10, 'l': 1, 'm': 2, 'n': 1, 'o': 1, 'p': 3, 'q': 8, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 10, 'x': 10, 'y': 10, 'z': 10}


CMD_INSTRUCTION = """
Usage
-----

Case 1: Command to find words containing all the following letters: A, X, T, M, E, and S
'python grumble.py -l AXTMES'
"""


class Arguments:
    def __init__(self, argv: List) -> None:
        self.args = self.list_to_dict(argv[1:])

        for k, v in self.args.items():
            if not k.startswith("-"):
                print('Error with arguments. Argument definition must start with "-"')
                continue
            attr = k.strip("-")
            if not hasattr(self, attr):
                setattr(self, attr, v)

    def list_to_dict(self, lst: List) -> Dict:
        dict = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return dict


def parse_args():
    if len(sys.argv) < 3:
        print("""
Sorry, at least one argument must be given.
{}        """.format(CMD_INSTRUCTION))
        sys.exit(1)

    return Arguments(sys.argv)


def get_letters(letters: str) -> List:
    return list(letters.upper())


def search_words2(letters: List, min_size: int=5):
    MATCHES = []
    letters = "".join([_.lower().translate(normalize) for _ in letters])

    with open(DICTIONARY, "r") as file_words:
        for word in file_words:
            word = word.replace("-", "").strip().lower().translate(normalize)

            # all letters composing word must be present in the set of input letters
            if False in [ _ in letters for _ in word ]:
                continue

            # frequency of letters composing word must not exceed frequency of input letters
            if not is_frequency_valid(word=word, letters=letters):
                continue

            if len(word) < min_size :
                continue

            match = (word, score_word(word=word))
            MATCHES.append(match)

    return MATCHES



def search_words(letters: List, exclude: List):
    MATCHES = []
    maximum_letter_to_found = len(letters)
    threshold = maximum_letter_to_found - 5


    while maximum_letter_to_found > threshold:
        print("Searching match for {} of the {} letters".format(maximum_letter_to_found, len(letters)))

        with open(DICTIONARY, "r") as file_words:
            for word in file_words:
                word = word.replace("-", "").strip().lower().translate(normalize)

                if sum( [letter.lower().translate(normalize) in word for letter in letters] ) == maximum_letter_to_found:
                    letters = "".join(letters).lower()
                    if exclude:                        
                        if not True in [ _.lower() in word for _ in exclude ]:
                            if word not in [x[0] for x in MATCHES] and is_frequency_valid(word=word, letters=letters):
                                MATCHES.append( (word, score_word(word=word)) )
                    else:
                        if word not in [x[0] for x in MATCHES] and is_frequency_valid(word=word, letters=letters):
                            MATCHES.append( (word, score_word(word=word)) )

        maximum_letter_to_found -= 1

    return MATCHES


def is_frequency_valid(word, letters):
    # using Counter to find frequency of elements
    ele_freq_word = collections.Counter(word)
    ele_freq_letters = collections.Counter(letters.lower())

    is_valid = True
    for k, v in ele_freq_word.items():
        if v > ele_freq_letters[k]:
            is_valid = False
            break

    return is_valid

def score_word(word: str) -> int:
    return sum([SCOREMAP[letter] for letter in word.lower() ])


if __name__ == "__main__":
    args = parse_args()

    letters = get_letters(args.l)
    try:
        min_size = int(args.min_size)
    except:
        min_size = 5

    print("Search words that best match: {}".format(", ".join(letters)))
    MATCHES = search_words2(letters=letters, min_size=min_size)

    if not MATCHES:
        print("No word have with an minimum size of {} been found containing all the letters below:".format(min_size))
        print("List of searched letters: {}".format(" - ".join(letters).upper()))

    MATCHES = sorted(MATCHES, key=lambda x: x[1], reverse=True)

    print("{} words of at least {} eligible letters have been found!\n".format(len(MATCHES), min_size))
    print("Top 10 matches:")
    for match in MATCHES[:10]:
        print("- {} (score: {})".format(match[0], match[1]))

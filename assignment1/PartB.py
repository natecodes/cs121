import sys

from PartA import ALPHANUMERIC_CHARS


# it would be slightly more optimal to reimplement the algorithm from PartA
# using sets instead of lists so that we do not have to convert lists to sets
# if we use the same tokenize() from PartA, we will have to do two O(n) operations
# (the initial tokenization + converting into a set)
# the complexity of this function is O(n) where n is the size of the file
def tokenize_into_set(TextFilePath: str) -> set:
    tokens = set()
    with open(TextFilePath) as file:
        token = ""
        for chunk in iter(lambda: file.read(4096), ""):
            for byte in chunk:
                if byte in ALPHANUMERIC_CHARS:
                    token += byte.lower()
                else:
                    # we reached a character that isn't alphanuemric so we should cut off the token
                    if token:
                        # if we add a duplicate token to the set, it is automatically handled by interpreter
                        tokens.add(token)
                        token = ""
    return tokens


# the set() constructor on an iterable list is an O(n) operation
# thus, the time complexity is O(2n) reduced to O(n)
# for set.intersection(), the time complexity is O(min(len(set1), len(set2)))
# thus, the overall time complexity for PartB is O(n) linear where n is the size of the smallest set
if __name__ == '__main__':
    """
    Takes in two filepaths from cmd sys args, tokenizes them, and
    outputs the number of tokens in common.
    """
    file1, file2 = sys.argv[1], sys.argv[2]
    common = tokenize_into_set(file1).intersection(tokenize_into_set(file2))
    print(common)
    print(len(common))

import string
import sys

ALPHANUMERIC_CHARS = [x for x in string.digits] + [x for x in string.ascii_letters]

# the time complexity of this function is O(n)
# where n is the size of the file
def tokenize(TextFilePath: str) -> list:
    tokens = list()
    with open(TextFilePath) as file:
        token = ""
        for chunk in iter(lambda: file.read(4096), ""):
            for byte in chunk:
                if byte in ALPHANUMERIC_CHARS:
                    token += byte.lower()
                else:
                    # we reached a character that isn't alphanuemric so we should cut off the token
                    if token:
                        tokens.append(token)
                        token = ""
    return tokens

# the time complexity of this function is O(n)
# where n is the length of the tokens list
# the in lookup method of dictionaries in Python is O(1)
def computeWordFrequencies(tokens: list) -> dict:
    frequencies = dict()
    for token in tokens:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1
    return frequencies

# the time complexity of this function is O(n log n)
# in-built sorted() function is O(n log n)
# the complexity of the for loop is O(n) where n is the size of the frequency map
# but it is overriden by the O(n log n) larger complexity
def printFrequencies(frequencies: dict) -> None:
    for token, frequency in sorted(frequencies.items(), key=lambda x: (x[1] * -1, x[0])):
        print(token + ' -> ' + str(frequency))


if __name__ == '__main__':
    path = sys.argv[1]
    printFrequencies(computeWordFrequencies(tokenize(path)))

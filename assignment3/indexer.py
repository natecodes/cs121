import json
import os
import pickle
from collections import Counter
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')

document_count = 0

def iterate_through_directory(directory):
    """Iterate through the directory and return a list of files"""
    files = []
    for root, dirs, filenames in os.walk(directory):
        for f in filenames:
            files.append(os.path.join(root, f))
    return files

def get_text_from_html(html):
    """Get the text from the html"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def tokenize(raw_text):
    """Tokenize text with nltk and use stemming"""
    ps = PorterStemmer()
    tokens = word_tokenize(raw_text)

    # Stem tokens
    tokens = [ps.stem(token) for token in tokens]
    return Counter(tokens)

def create_index(directory):
    """Create the index"""
    global document_count
    index = {}
    for filename in iterate_through_directory(directory):

        # Read json file
        with open(filename, "r") as f:
            raw = json.load(f)
            html = raw["content"]
            url = raw["url"]

        document_count += 1
        text = get_text_from_html(html)
        tokens = tokenize(text)
        for token, count in tokens.items():
            if token not in index:
                index[token] = []
            index[token].append((url, count))
        if document_count % 1000 == 0:
            print("Processed", document_count, "documents")
    return index

if __name__ == "__main__":
    index = create_index("DEV")
    print("Number of tokens:", len(index))
    print("Number of words:", document_count)
    # pickle the index
    with open("index.pickle", "wb") as f:
        pickle.dump(index, f)

    # print pickle file size
    print("Pickle file size", os.path.getsize("index.pickle"))
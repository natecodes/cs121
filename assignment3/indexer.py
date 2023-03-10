import json
import os
import pickle
import math
import re
import time
import itertools
import shutil
from collections import Counter
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')

document_count = 0  # total count of all documents
urls = {}  # map of document_id to actual url
BATCH_SIZE = 1_000  # number of documents to parse before offloading to disk
MERGE_CHUNK_SIZE = 100_000  # number of lines to read at a time when merging files 

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

def is_valid_token(input_token):
    pattern = r'^[a-zA-Z0-9_.-!@#$%^&*()+=?\'\"]+$'
    return bool(re.match(pattern, input_token))

def tokenize(raw_text):
    """Tokenize text with nltk and use stemming"""
    ps = PorterStemmer()
    tokens = word_tokenize(raw_text)

    # Stem tokens
    tokens = [ps.stem(token) for token in tokens]

    # # remove non alphanumeric tokens

    # tokens = [token for token in tokens if is_valid_token(token)]

    # # remove tokens that are only 1 character long
    # tokens = [token for token in tokens if len(token) > 1]

    # # lowercase all tokens
    # tokens = [token.lower() for token in tokens]

    return Counter(tokens)


class Posting:
    def __init__(self, docid: int, tf, fields):
        self._docid = docid
        self._tf = tf # just count for now
        self._fields = fields

    def docid(self):
        return self._docid

    def tf(self):
        return self._tf

    def fields(self):
        return self._fields

    def __lt__(self, other):
        if not isinstance(other, Posting):
            return NotImplemented
        return self._docid < other._docid

    def __repr__(self):
        return f"Posting({self._docid}, {self._tf}, {self._fields})"


def create_indexes(directory) -> None:
    """Create the indexes"""
    global document_count, urls
    index = {}
    
    # Prepare the batches directory
    if os.path.exists("batches"):
        shutil.rmtree("batches/")
    os.mkdir("batches")

    for filename in iterate_through_directory(directory):

        # Read json file
        with open(filename, "r") as f:
            raw = json.load(f)
            html = raw["content"]
            url = raw["url"]

        document_count += 1
        urls[document_count] = url

        # parse out the tokens
        text = get_text_from_html(html)
        tokens = tokenize(text)
        for token, count in tokens.items(): # add each token to the index
            if token not in index:
                index[token] = []
            index[token].append(Posting(document_count, count, None))

        if document_count % 1000 == 0: # print checkpoint every 100 document
            print("Processed", document_count, "documents")

        if document_count % BATCH_SIZE == 0: # offload batch to disk
            print(f"{document_count} documents processed, offloading to disk.")
            sort_and_write_to_disk(index, f"batches/batch{document_count // BATCH_SIZE}.pickle")
            print(f"Batch {document_count // BATCH_SIZE} offloaded.")
            index = {}

    # finished all documents, load any extras in one last batch
    print("All documents processed, offloading final batch to disk.")
    sort_and_write_to_disk(index, f"batches/batch{math.ceil(document_count / BATCH_SIZE)}.pickle")
    print(f"Final batch (#{math.ceil(document_count / BATCH_SIZE)}) offloaded.")

def sort_and_write_to_disk(index: dict, filename: str) -> None:
    """Sort the given index and pickle it out to disk"""
    with open(filename, 'wb') as batch:
        for doc_id in sorted(index):
            pickle.dump((doc_id, sorted(index[doc_id])), batch)

def merge_indexes() -> int:
    """Merge all temporary indices in the batches/ directory into one index, returning its length."""
    index_length = 0
    read_buffers = []
    batch_files = []
    completed_files = set()

    # open all the files and place the first line into the buffer
    for i, filename in enumerate(os.listdir("batches")):
        batch_file = open(f"batches/{filename}", 'rb')
        batch_files.append(batch_file)
        read_buffers.append(pickle.load(batch_file))
    out_file = open("index2.pickle", 'wb')

    output = dict()
    while len(completed_files) != len(batch_files): # loop through until all files are completed
        target = min([buff[0] for i, buff in enumerate(read_buffers) if i not in completed_files])
        output[target] = dict()
        
        for i, buff in enumerate(read_buffers): # find any matches for the next token
            if i in completed_files:
                continue

            if buff[0] == target: # token match, tack it on and increase that buffer
                for posting in buff[1]:
                    output[target][posting.docid()] = posting.tf() * math.log(document_count/idf)

                try:
                    read_buffers[i] = pickle.load(batch_files[i])
                except EOFError:
                    completed_files.add(i)
        index_length += 1

        if index_length % MERGE_CHUNK_SIZE == 0: # write to out file in chunks
            pickle.dump(output, out_file)
            print(f"Merged {index_length} tokens")
            output = dict()

    pickle.dump(output, out_file)

    # close out the files
    for batch_file in batch_files:
        batch_file.close()
    out_file.close()

    return index_length



if __name__ == "__main__":
    create_indexes("DEV")
    num_tokens = merge_indexes()

    print(f"Number of tokens: {num_tokens}")
    print(f"Number of words: {document_count}")

    # pickle the url map
    with open("urls.pickle", "wb") as f:
        pickle.dump(urls, f)

    # print pickle file size
    print("Pickle file size", os.path.getsize("index2.pickle"))
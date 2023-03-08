import json
import os
import pickle
import math
import time
import itertools
from collections import Counter
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')

document_count = 0  # total count of all documents
urls = {}  # map of document_id to actual url
BATCH_SIZE = 10_000  # number of documents to parse before offloading to disk
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

def tokenize(raw_text):
    """Tokenize text with nltk and use stemming"""
    ps = PorterStemmer()
    tokens = word_tokenize(raw_text)

    # Stem tokens
    tokens = [ps.stem(token) for token in tokens]
    return Counter(tokens)


class Posting:
    def __init__(self, docid: int, tfidf, fields):
        self._docid = docid
        self._tfidf = tfidf # just length for now
        self._fields = fields
    
    def __lt__(self, other):
        if not isinstance(other, Posting):
            return NotImplemented
        return self._docid < other._docid

    def __repr__(self):
        return f"Posting({self._docid}, {self._tfidf}, {self._fields})"


def create_indexes(directory) -> None:
    """Create the indexes"""
    global document_count, urls
    index = {}

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

        if document_count % 100 == 0: # print checkpoint every 100 document
            print("Processed", document_count, "documents")

        if document_count % BATCH_SIZE == 0: # offload batch to disk
            print(f"{document_count} documents processed, offloading to disk.")
            sort_and_write_to_disk(index, f"batches/batch{document_count // BATCH_SIZE}.txt")
            print(f"Batch {document_count // BATCH_SIZE} offloaded.")
            index = {}

    # finished all documents, load any extras in one last batch
    print("All documents processed, offloading final batch to disk.")
    sort_and_write_to_disk(index, f"batches/batch{math.ceil(document_count / BATCH_SIZE)}.txt")
    print(f"Final batch (#{math.ceil(document_count / BATCH_SIZE)}) offloaded.")

def sort_and_write_to_disk(index: dict, filename: str) -> None:
    """Sort the given index and write it out to disk"""
    with open(filename, 'w') as batch:
        to_write = ""
        for doc_id in sorted(index):
            to_write += f"{doc_id} :maps_to: {sorted(index[doc_id])}\n"
        batch.write(to_write)

def merge_indexes() -> int:
    """Merge all temporary indices in the batches/ directory into one index, returning its length."""
    index_length = 0
    read_buffers = []
    batch_files = []
    completed_files = set()

    # open all the files and place the first line into the buffer
    for filename in os.listdir("batches"):
        batch_file = open(f"batches/{filename}", 'r')
        batch_files.append(batch_file)
        read_buffers.append([piece.strip() for piece in next(batch_file).split(" :maps_to: ")])
    out_file = open("index.txt", 'w')

    output = []
    while len(completed_files) != len(batch_files): # loop through until all files are completed
        target = min([buff[0] for i, buff in enumerate(read_buffers) if i not in completed_files])

        matches = []
        for i, temp_line in enumerate(read_buffers): # find any matches for the next token
            if i in completed_files:
                continue

            if temp_line[0] == target: # found match, tack it on and increase that buffer
                matches.append(f"{temp_line[1][1:-1]}")
                try:
                    read_buffers[i] = [piece.strip() for piece in next(batch_files[i]).split(" :maps_to: ")]
                except StopIteration:
                    completed_files.add(i)
        output.append(f"{target} :maps_to: [{', '.join(matches)}]")
        index_length += 1

        if index_length % MERGE_CHUNK_SIZE == 0: # write to out file in chunks
            out_file.write("\n".join(output))
            print(f"Merged {index_length} tokens")
            output = []

    out_file.write("\n".join(output))

    # close out the files
    for batch_file in batch_files:
        batch_file.close()
    out_file.close()

    return index_length



if __name__ == "__main__":
    a = merge_indexes()
    print("num tokens:", a)
    # create_indexes("DEV")
    # num_tokens = merge_indexes()

    # print(f"Number of tokens: {num_tokens}")
    # print(f"Number of words: {document_count}")

    # # # pickle the index
    # # with open("index.pickle", "wb") as f:
    # #     pickle.dump(index, f)
    
    # # pickle the url map
    # with open("urls.pickle", "wb") as f:
    #     pickle.dump(urls, f)

    # # print pickle file size
    # print("Pickle file size", os.path.getsize("index.pickle"))
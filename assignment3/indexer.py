import json
import os
import pickle
import math
import re
import time
import itertools
import shutil
from collections import Counter
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')

document_count = 0  # total count of all documents
urls = {}  # map of document_id to actual url
BATCH_SIZE = 1_000  # number of documents to parse before offloading to disk
MERGE_CHUNK_SIZE = 100_000  # number of lines to read at a time when merging files

def compute_tf_idf(tf, idf):
    global document_count
    return tf * math.log(document_count/idf)

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

def get_important_text_from_html(html):
    """Get the important text from the html"""
    soup = BeautifulSoup(html, "html.parser")
    important_text = defaultdict(dict)
    #html_tags = ['b', 'strong', 'title', 'h1', 'h2', 'h3']
    html_tags = {'b':2, 'strong':2, 'title':5, 'h1':3, 'h2':3, 'h3':3}
    for tag in html_tags.keys():
        for found_text in soup.find_all(tag):
            text_tokens = tokenize(found_text.text.strip())
            for token,count in text_tokens.items():
                important_text[token][tag]=count*html_tags[tag]

    return important_text

def get_anchor_text_from_html(html):
    """Get the anchor text from the html"""
    soup = BeautifulSoup(html, "html.parser")
    anchor_text = []
    for t in soup.find_all('a'):
        anchor_text.append(t.text.strip())
    return anchor_text

def tokenize(raw_text):
    """Tokenize text with nltk and use stemming"""
    ps = PorterStemmer()

    tokens = []
    for token in word_tokenize(raw_text):
        stemmed = ps.stem(token) # stem tokens
        if is_valid_token(stemmed) and len(stemmed) > 1: # only alphanumeric and 2+ char tokens
            tokens.append(token.lower()) # convert to lowercase

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

# extra credit similarity/exact
page_tokens = dict()

def similar(url, tokens):
    if url not in page_tokens:
        token_set = set(tokens) #get unique tokens for url
        for value in page_tokens.values(): #go through all previously scraped pages
            tokens_inter = value.intersection(token_set) #get intersection
            if len(tokens_inter) > 0:
                #check intersection/current tokenlist ratio, if over threshold return True(similar), else continue
                if len(tokens_inter) / len(token_set) > 0.9: 
                    return True
        #add url and unique tokens to list
        page_tokens[url] = token_set
        return False #not similar
    else:
            return True

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
       
        #parse out important tokens
        important_text = get_important_text_from_html(html)

        #parse out anchor tokens
        #anchor_tokens = get_anchor_text_from_html(html)

        # parse out the tokens
        text = get_text_from_html(html)
        tokens = tokenize(text)

        # duplicate page removal - extra credit, works for both exact and similar text
        if not similar(url, tokens.keys()):
            for token, count in tokens.items(): # add each token to the index
                if token not in index:
                    index[token] = []
                if token in important_text:
                    index[token].append(Posting(document_count, count, important_text[token]))
                    important_text.pop(token)
                else:
                    index[token].append(Posting(document_count, count, None))
        
        # print(index)
        #time.sleep(30)
        #adds tokens found in html tags that arent found in the text to the index
        # for token in important_text:
        #     if token not in index:
        #         index[token] = []     
        #     index[token].append(Posting(document_count, 0, important_text[token]))   
        
        if document_count % 100 == 0: # print checkpoint every 100 document
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
        for token in sorted(index):
            pickle.dump((token, sorted(index[token])), batch)

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
    freq = defaultdict(int)
    while len(completed_files) != len(batch_files): # loop through until all files are completed
        target = min([buff[0] for i, buff in enumerate(read_buffers) if i not in completed_files])
        output[target] = dict()
        
        for i, buff in enumerate(read_buffers): # find any matches for the next token
            if i in completed_files:
                continue

            if buff[0] == target: # token match, tack it on and increase that buffer
                for posting in buff[1]:
                    #print(posting)
                    fields_tf = 0 if posting.fields() == None else sum(posting.fields().values())
                    output[target][posting.docid()] = posting.tf()+fields_tf # * math.log(document_count/idf)
                    freq[target]+=1
                try:
                    read_buffers[i] = pickle.load(batch_files[i])
                except EOFError:
                    completed_files.add(i)
        #checking target/freq/output
        # print(f"target: {target}")
        # print(f"freq: {freq}")
        #print(f"output: {output}")
        #time.sleep(5)
        index_length += 1

        if index_length % MERGE_CHUNK_SIZE == 0: # write to out file in chunks
            pickle.dump(output, out_file)
            print(f"Merged {index_length} tokens")
            output = dict()

    for token in output:
        idf = freq[token]
        output[token].update({key: output[token][key] * math.log(document_count/idf) for key in output[token].keys()})

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
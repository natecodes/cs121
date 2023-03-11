import time
import pickle
from nltk.stem import PorterStemmer


def get_from_lookup(index_lookup, token):
    """Checks the index lookup table to find what file has the given token, and returns
    the postings for that token found in the index."""
    for token_range in index_lookup:
        if token > token_range[0] and token < token_range[1]:
            with open(index_lookup[token_range], 'rb') as index_file:
                return pickle.load(index_file).get(token)
    return []


def search_request(request, index_lookup):
    """Takes in a query request and an index lookup, and returns all the results matching
    a boolean AND on all the queries."""
    if not request:
        return []

    # sort tokens by how many documents have that token
    sorted_request = sorted(request, key=lambda x: len(get_from_lookup(index_lookup, x) or []))

    # get the result from the first token
    search_result = get_from_lookup(index_lookup, sorted_request[0])

    if not search_result: # if found nothing, return empty
        return []

    # for every other token, check in the index and take the intersection with running set
    for token in sorted_request[1:]:
        new_results = get_from_lookup(index_lookup, token)
        # intersect new_results and search_result
        search_result = {docId: search_result[docId] + new_results[docId] for docId in search_result if docId in new_results }

    # when returning, sort by tfidf score
    return [result for result in sorted(search_result.items(), key=lambda x:x[1], reverse=True)]


def load_pickle_as_dict(file_path):
    """Continously load and union a pickled dictionary into one dictionary"""
    index = dict()
    with open(file_path, 'rb') as file:
        while True:
            try:
                index |= pickle.load(file)
            except EOFError:
                break
    return index


def create_temp_index():
    return { "a":[("url1",10),("url2", 20),("url3", 5)], "b":[("url2",4)], "c":[("url1",9),("url2",3)], "d": [("url1",1)]}


if __name__ == '__main__':
    print("UCI Search Engine!")
    print("Note: type 'exit' as the query to end program\n")

    # unpickle the lookup and urls
    urls = load_pickle_as_dict('urls.pickle')
    index_lookup = load_pickle_as_dict('index_lookup.pickle')
    ps = PorterStemmer()

    while True:
        # get a query from the user, quit on 'exit'
        request = input('Query: ')
        if(request == "exit"):
            break

        start = time.time()

        # parse out the query and get the top 10 results
        tokens = {ps.stem(token) for token in request.strip().split(" ") if len(ps.stem(token)) > 1}
        results = search_request(tokens, index_lookup)[:10]

        # print out results and time
        if(results == []):
            print("No results found!")
        else:
            print("\n".join([f"... {i}) {urls[docId[0]]}" for i, docId in enumerate(results, start=1)]))
        print(f"Found in ~{int((time.time() - start) * 1000)} milliseconds.\n")

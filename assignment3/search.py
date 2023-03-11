import time
import pickle
from nltk.stem import PorterStemmer


def search_request(request, index):
    if not request:
        return []

    sorted_request = sorted(request, key=lambda x: len(index.get(x) or []))

    if sorted_request[0] not in index:
        return []

    search_result = index[sorted_request[0]]


    for token in sorted_request[1:]:
        new_results = index[token]
        # intersect new_results and search_result
        search_result = {docId: search_result[docId] + new_results[docId] for docId in search_result if docId in new_results }

    return [result[0] for result in sorted(search_result.items(), key=lambda x:x[1], reverse=True)]


def load_pickle_as_dict(file_path):
    index = dict()
    with open(file_path, 'rb') as file:
        index |= pickle.load(file)
    return index
    

def create_temp_index(): 
    return { "a":[("url1",10),("url2", 20),("url3", 5)], "b":[("url2",4)], "c":[("url1",9),("url2",3)], "d": [("url1",1)]}


if __name__ == '__main__':
    print("Loading index...")
    index = load_pickle_as_dict('index2.pickle')
    urls = load_pickle_as_dict('urls.pickle')
    ps = PorterStemmer()
    print("Loaded!\n")
    
    while True:
        request = input('Query: ')
        if(request == "exit"):
            break
        
        start = time.time()
        tokens = [ps.stem(token) for token in request.strip().split(" ")]
        results = search_request(tokens, index)[:5]

        if(results == []):
            print("No results found!")
        else:
            print("\n".join([f"... {i}) {urls[docId]}" for i, docId in enumerate(results, start=1)]))
        print(f"Found in ~{int((time.time() - start) * 1000)} milliseconds.\n")

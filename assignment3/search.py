import time
import pickle
from nltk.stem import PorterStemmer


def search_request(request, index):
    if not request:
        return []

    if index.get(request[0]) == None:
        return []

    search_result = set(index.get(request[0]))
    
    for token in request[1:]:
        if index.get(token) == None:
            return []

        new_results = set(index.get(token))
        new_search_result = set()

        for new_result in new_results: # not at all optimized
            for result in search_result: 
                if new_result[0] == result[0]: # both tokens in the same url, add their count
                    new_search_result.add((new_result[0], new_result[1] + result[1]))
        
        search_result = new_search_result
    
    return [result[0] for result in sorted(search_result, key=lambda x:x[1], reverse=True)]


def get_index():
    with open('index.pickle', 'rb') as file:
        return pickle.load(file)
    

def create_temp_index(): 
    return { "a":[("url1",10),("url2", 20),("url3", 5)], "b":[("url2",4)], "c":[("url1",9),("url2",3)], "d": [("url1",1)]}


if __name__ == '__main__':
    print("Loading index...")
    index = get_index()
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
            print("\n".join([f"... {i}) {result}" for i, result in enumerate(results, start=1)]))
        print(f"Found in ~{int((time.time() - start) * 1000)} milliseconds.\n")

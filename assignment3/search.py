import pickle
import itertools

def search_request(request, index):
    if(index.get(request[0]) == None):
        return []
    search_result = [x[0] for x in index.get(request[0])] #get list of urls
    for i in range(1,len(request)):
        if index.get(request[i]) != None:
            temp = [x[0] for x in index.get(request[i])] #get list of urls
            search_result = set(search_result) & set(temp)
        else:
            return []
    return list(search_result)

def get_index():
    with open('index.pickle', 'rb') as file:
        return pickle.load(file)
    

def create_temp_index(): 
    return { "a":[("url1",10)], "b":[("url2",4)], "c":[("url1",9),("url2",3)], "d": [("url1",1)]}


if __name__ == '__main__':
    # index = get_index()
    index = create_temp_index()
    
    while True:
        request = input('Query: ')
        if(request == "exit"):
            break
        
        tokens = [token for token in request.strip().split(" ") if token != "AND"]
        result = search_request(tokens, index)
        # result = list(itertools.islice(search_request(tokens, index), 5))
        if(result == []):
            print("No results found!")
        else:
            print(result)

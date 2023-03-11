from nltk import PorterStemmer

from flask import Flask, request
from search import load_pickle_as_dict, search_request

app = Flask(__name__)

index_lookup = load_pickle_as_dict('index_lookup.pickle')
urls = load_pickle_as_dict('urls.pickle')
ps = PorterStemmer()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    print(query)
    tokens = [ps.stem(token) for token in query.strip().split(" ")]
    results = search_request(tokens, index_lookup)[:10]
    results = {urls[result[0]]: result[1] for result in results}
    return results

if __name__ == '__main__':
    app.run(host='127.0.0.1', port = 5000)

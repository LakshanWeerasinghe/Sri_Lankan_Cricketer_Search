import json
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')


def read_corpus(filename):
    content = None
    with open(filename) as f:
        content = json.load(f)
    return content


def create_index():
    corpus = read_corpus('corpus/player_corpus_en.json')
    # corpus = json.loads(corpus)

    for document in corpus:
        es.index(index='corpus-en', document=json.loads(document))


if __name__ == '__main__':
    create_index()
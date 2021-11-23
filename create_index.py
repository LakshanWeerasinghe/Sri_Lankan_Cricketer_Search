import os
import json

from elasticsearch import Elasticsearch

from Settings import Settings

es = Elasticsearch(Settings.es_url.value)


def read_corpus(filename):
    content = None
    with open(filename) as f:
        content = json.load(f)
    return content


def create_index():

    corpus = read_corpus('corpus/final-corpus.json')

    for document in corpus:
        es.index(index='sri-lankan-cricketers', document=json.loads(document))


if __name__ == '__main__':
    create_index()

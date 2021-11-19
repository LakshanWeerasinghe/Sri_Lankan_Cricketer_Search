from enum import Enum


class Settings(Enum):

    # Flask
    flask_host = '0.0.0.0'
    flask_port = 5000
    debug = True

    # Elastic Search
    index_name = 'sri-lankan-cricketers'
    es_host = 'localhost'
    es_port = 9000

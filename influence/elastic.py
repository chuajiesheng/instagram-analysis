from elasticsearch import Elasticsearch


class ElasticSearchHelper:
    def __init__(self):
        pass

    def get_es(self):
        host = ['http://10.5.0.61:9200']
        es = Elasticsearch(host, timeout=3000)
        return es

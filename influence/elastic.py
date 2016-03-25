from elasticsearch import Elasticsearch


class ElasticSearchHelper:
    HOST = 'http://localhost:9200'

    def __init__(self):
        pass

    def get_es(self):
        es = Elasticsearch([self.HOST], timeout=3000)
        return es

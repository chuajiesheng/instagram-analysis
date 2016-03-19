import os
import json
from elasticsearch import Elasticsearch


class Relationship:
    json = None

    def __init__(self, json):
        self.json = json

    def cycle_id(self):
        if self.json is None:
            return -1

        return int(self.json['cycle_id'])

    def followers(self):
        if self.json is None:
            return []

        return self.json['followers_id']


class RelationshipHelper:
    FILENAME = 'in/relationship_{}.json'

    def __init__(self):
        pass

    @staticmethod
    def get_relationship(insta_user_id, log=False):
        if log:
            print 'get_relationship of', insta_user_id

        relationship = Relationship(None)
        json = RelationshipHelper.download(insta_user_id)

        dataset = json['hits']['hits']
        for obj in dataset:
            r = Relationship(obj['_source'])
            if r.cycle_id() > relationship.cycle_id():
                relationship = r

        return relationship

    @staticmethod
    def download_from_es(insta_user_id):
        query = {
            "query": {
                "filtered": {
                    "filter": {
                        "term": {
                            "insta_user_id": insta_user_id
                        }
                    }
                }
            },
            "sort": {
                "cycle_id": {
                    "order": "desc",
                    "mode":  "min"
                }
            },
            "from": 0,
            "size": 1
        }
        host = ['http://10.5.0.61:9200']
        es = Elasticsearch(host)

        return es.search(index='instagram', body=query)

    @staticmethod
    def download(insta_user_id):
        # check if json file exist
        filename = RelationshipHelper.FILENAME.format(insta_user_id)
        file_exists = os.path.isfile(filename)

        if not file_exists:
            # download file if not exist
            content = RelationshipHelper.download_from_es(insta_user_id)

            # write to file as cache
            f = open(filename, 'w+')
            f.write(json.dumps(content))

            # return the json
            return content

        content = open(filename, 'r').read()

        data = json.loads(content)
        return data


if __name__ == '__main__':
    INSTA_USER_ID = '1946547496'
    r = RelationshipHelper.get_relationship(INSTA_USER_ID)
    print r.json

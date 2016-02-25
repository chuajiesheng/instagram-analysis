import os
import sys
import json
from elasticsearch import Elasticsearch


class Relationship:
    json = None

    def __init__(self, json):
        self.json = json

    def cycle_id(self):
        return int(self.json['cycle_id'])


class RelationshipHelper:
    FILENAME = 'in/relationship_{}.json'

    def __init__(self):
        pass

    @staticmethod
    def get_relationship(insta_user_id):
        relationship = None

        json = RelationshipHelper.download(insta_user_id)
        dataset = json['hits']['hits']
        for obj in dataset:
            r = Relationship(obj['_source'])
            if relationship is None:
                relationship = r
            elif r.cycle_id() > relationship.cycle_id():
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
                    "mode": "min"
                }
            }
        }
        host = ['http://localhost:9200']
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
    INSTA_USER_ID = '269959784'
    r = RelationshipHelper.get_relationship(INSTA_USER_ID)
    print r.json

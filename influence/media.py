from elasticsearch import Elasticsearch

es = None


class Media:
    json = None

    def __init__(self, json):
        self.json = json['_source']

    def id(self):
        return self.json['id']

class MediaHelper:
    def __init__(self):
        pass

    @staticmethod
    def get_media(media_id):
        json = MediaHelper.download(media_id)
        dataset = json['hits']['hits']
        for obj in dataset:
            media = Media(obj)

            if media.id() == media_id:
                return media


    @staticmethod
    def download(media_id):
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "type": {"value": "media"}
                        },
                        {
                            "term": {
                                "id": {"value": media_id}
                            }
                        }
                    ]
                }
            }
        }
        return es.search(index='instagram', body=query)


if __name__ == '__main__':
    MEDIA_ID = '1108626510904721584_35720927'

    host = ['http://localhost:9200']
    es = Elasticsearch(host)

    print MediaHelper.get_media(MEDIA_ID).id()

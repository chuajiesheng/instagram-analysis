import elastic as e
import string

es = None


class Media:
    json = None

    def __init__(self, json):
        self.json = json

    def id(self):
        return self.json['id']

    def created_time(self):
        return int(self.json['created_time'])

    def caption(self):
        return self.json['caption']

    def link(self):
        return self.json['link']

    def tags(self):
        return '|'.join([self.clean_string(s) for s in self.json['tags']])

    def no_of_tags(self):
        return len(self.json['tags'])

    def caption_id(self):
        return self.caption()['id']

    def user(self):
        return self.json['user']

    def username(self):
        return self.user()['username']

    def user_id(self):
        return self.user()['id']

    def clean_string(self, str):
        if str is None:
            return ''

        printable = set(string.printable)
        return filter(lambda s: s in printable, str)

class MediaHelper:
    def __init__(self):
        pass

    @staticmethod
    def get_media(media_id, log=False):
        if log:
            print 'downloading media', media_id

        json = MediaHelper.download(media_id)
        dataset = json['hits']['hits']
        for obj in dataset:
            media = Media(obj['_source'])

            if media.id() == media_id:
                return media

        return None

    @staticmethod
    def download(media_id):
        es = e.ElasticSearchHelper().get_es()

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

    print MediaHelper.get_media(MEDIA_ID).caption_id()

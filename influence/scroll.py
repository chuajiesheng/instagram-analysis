import elastic as e
import comment_tree as ct
import requests
import json
import code


class Scroll:
    done = 0
    sid = None

    def __init__(self):
        self.done = 0

    def start(self):
        es = e.ElasticSearchHelper().get_es()

        page = es.search(
            index='instagram',
            doc_type='media',
            scroll='30m',
            search_type='scan',
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "type": "image"
                                }
                            }
                        ],
                        "filter": [
                            {
                                "range": {
                                    "comments.count": {
                                        "lte": 150
                                    }
                                }
                            }
                        ]
                    }
                },
                "sort": [
                    "_doc"
                ],
                "size": 5

            })
        self.sid = page['_scroll_id']
        scroll_size = page['hits']['total']
        # code.interact(local=locals())

        # Start scrolling
        while scroll_size > 0:
            print "scrolling..."
            page = es.scroll(scroll_id=self.sid, scroll='2m')
            # Update the scroll ID
            self.sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            results = page['hits']['hits']
            scroll_size = len(results)
            print "scroll size: " + str(scroll_size)

            medias = [result['_source']['id'] for result in results]
            ct.CommentTree.generate_all(medias)

    def end_session(self):
        payload = {'scroll_id': [self.sid]}
        url = e.ElasticSearchHelper.HOST + '/_search/scroll'
        response = requests.delete(url, data=json.dumps(payload))
        return response.status_code == requests.codes.ok


if __name__ == '__main__':
    s = Scroll()
    s.start()
    s.end_session()

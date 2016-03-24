import elastic as e
import comment_tree as ct


class Scroll:
    done = 0

    def __init__(self):
        self.done = 0

    def start(self):
        es = e.ElasticSearchHelper().get_es()

        page = es.search(
            index='instagram',
            doc_type='media',
            scroll='300m',
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
                "size": 5000000

            })
        sid = page['_scroll_id']
        scroll_size = page['hits']['total']

        # Start scrolling
        while (scroll_size > 0):
            print "Scrolling..."
            page = es.scroll(scroll_id=sid, scroll='2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            scroll_size = len(page['hits']['hits'])
            print "scroll size: " + str(scroll_size)
            # Do something with the obtained page


if __name__ == '__main__':
    s = Scroll()
    s.start()

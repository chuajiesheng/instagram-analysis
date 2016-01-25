from elasticsearch import Elasticsearch
import sys
import json

es = None


def put(index_name, doc_type, id, doc):
    res = es.index(index=index_name, doc_type=doc_type, id=id, body=doc)
    if not res['created']:
        print(index_name + '/' + doc_type + '/' + str(id), res['created'])
    else:
        sys.stdout.write('.')
        sys.stdout.flush()


def get(index_name, doc_type):
    res = es.get(index=index_name, doc_type=doc_type, id=1)
    print(res['_source'])


def refresh(index_name):
    es.indices.refresh(index=index_name)


def search(index_name, query):
    res = es.search(index=index_name, body=query)

    print("Got %d Hits:" % res['hits']['total'])
    for hit in res['hits']['hits']:
        print("[%(timestamp)s] %(place)s - %(temperature)s by %(device)s" % hit["_source"])

if __name__ == '__main__':
    address = 'http://localhost:9200'
    index_name = 'instagram'
    doc_type = ''

    file = ''

    if len(sys.argv) > 2:
        doc_type = sys.argv[1]
        print 'Importing into', address + '/' + index_name + '/' + doc_type

        file = sys.argv[2]
        print 'Reading file', file
    else:
        print 'No import file found, exiting.'
        exit(1)

    with_id = 1
    if len(sys.argv) > 3:
        with_id = int(sys.argv[3])

    es = Elasticsearch([address])
    fp = open(file)
    lines = 0
    for i, line in enumerate(fp):
        with_id = with_id == 1
        try:
            parsed_json = json.loads(line)
        except ValueError:
            print 'Load', id, 'failed'

        if with_id:
            put(index_name, doc_type, i, line)
        else:
            put(index_name, doc_type, None, line)

        lines += 0

    fp.close()
    print lines, 'added.'



from elasticsearch import Elasticsearch
import sys
import json
import glob
import time

es = None


def put(index_name, doc_type, id, doc, tries=0):
    res = None
    failed = False

    try:
        res = es.index(index=index_name, doc_type=doc_type, id=id, body=doc)
    except Exception as e:
        print str(e)
        failed = True

    if failed or (not res['created']):
        print 'res[created]', str(res)
        print 'Error', index_name + '/' + doc_type + '/' + str(id)

        if tries > 5:
            error_file = open('error.json', 'w+')
            error_file.write(doc + '\n')
            error_file.close()
            print 'Error output'
            return 0
        else:
            sleep(tries)
            indexed = put(index_name, doc_type, id, doc, (tries + 1))
            print 'Error cleared'
            return indexed
    else:
        sys.stdout.write('.')
        sys.stdout.flush()
        return 1


def sleep(tries):
    sleep_time = 2 ** tries

    if sleep_time > 120:
        sleep_time = 120

    print 'Sleeping for', sleep_time
    sys.stdout.flush()

    time.sleep(sleep_time)


if __name__ == '__main__':
    address = 'http://localhost:9200'
    index_name = 'instagram'
    doc_type = sys.argv[1]
    print 'Index', address + '/' + index_name + '/' + doc_type

    es = Elasticsearch([address])

    total_lines_added = 0

    for filename in glob.glob('in/*.json'):
        print 'Reading', filename
        fp = open(filename)
        file_lines_added = 0

        for i, line in enumerate(fp):
            try:
                parsed_json = json.loads(line)
            except ValueError:
                print 'Parse failed', filename, i

            indexed = put(index_name, doc_type, None, line)
            file_lines_added += indexed

        print file_lines_added, 'added from', filename
        total_lines_added += file_lines_added
        fp.close()

    print total_lines_added, 'added.'



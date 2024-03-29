from elasticsearch import Elasticsearch
import sys
import json
import getopt
import time

es = None


def put(index_name, doc_type, id, doc, tries=0):
    res = None
    failed = False

    try:
        res = es.index(index=index_name, doc_type=doc_type, id=id, body=doc)
    except Exception:
        failed = True

    if failed or (not res['created']):
        print 'Error:', index_name + '/' + doc_type + '/' + str(id)
        sleep(tries)
        put(index_name, doc_type, id, doc, (tries + 1))
        print 'Error cleared'

    sys.stdout.write('.')
    sys.stdout.flush()


def sleep(tries):
    sleep_time = 2 ** tries

    if sleep_time > 120:
        sleep_time = 120

    print 'Sleeping for', sleep_time
    sys.stdout.flush()

    time.sleep(sleep_time)


def print_help():
    # print help
    print 'import_json.py -f <input_file>'
    print ''
    print '-h', 'Print this help file'
    print '-n', 'Do not use index in index call'
    print '-d doc_type', 'The doc_type for the index'
    print '-f file', 'Import this file'
    print '-o', 'Start reading file at this line'
    print '-s', 'ID for index call start with this value'
    sys.exit()


if __name__ == '__main__':
    address = 'http://localhost:9200'
    index_name = 'instagram'
    doc_type = ''

    verbose = False
    file = ''
    with_id = True
    file_offset = 0
    id_offset = 0

    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, 'hvnd:f:o:s:', ['help', 'verbose', 'no-index', 'doc=', 'file=', 'offset=', 'start='])
    except getopt.GetoptError:
        print 'import_json.py -f <input_file>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
        elif opt in ('-v', '--verbose'):
            print 'Verbose mode'
            verbose = True
        elif opt in ('-n', '--no-index'):
            print 'Do not use id in the index call'
            with_id = False
        elif opt in ('-d', '--doc'):
            doc_type = arg
            print 'Document', doc_type
        elif opt in ('-f', '--file'):
            file = arg
            print 'Reading file', file
        elif opt in ('-o', '--offset'):
            file_offset = int(arg)
            print 'Reading file starting from line', file_offset
        elif opt in ('-s', '--start'):
            id_offset = int(arg)
            print 'Index starting from id', id_offset

    if doc_type is None or len(doc_type) == 0:
        print 'Document type is a required parameter.'
        exit(1)

    if file is None or len(file) == 0:
        print 'File is a required parameter.'
        exit(2)

    es = Elasticsearch([address])
    fp = open(file)
    lines_added = 0
    for i, line in enumerate(fp):
        if i < file_offset:
            continue

        id = None
        if with_id:
            id = id_offset + i

        if verbose:
            print 'Putting %s/%s/%s\n%s' % (index_name, doc_type, id, line)

        try:
            parsed_json = json.loads(line)
        except ValueError:
            print 'Load', i, 'failed'

        put(index_name, doc_type, id, line)
        lines_added += 1

    fp.close()
    print lines_added, 'added.'



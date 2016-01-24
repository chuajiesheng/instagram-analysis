from elasticsearch import Elasticsearch
import sys
import json

es = None


if __name__ == '__main__':
    file = ''

    if len(sys.argv) > 1:
        file = sys.argv[1]
        print 'Reading file', file
    else:
        print 'No import file found, exiting.'
        exit(1)

    lines = 0;
    fp = open(file)
    for i, line in enumerate(fp):
        try:
            parsed_json = json.loads(line)
        except ValueError:
            print 'Load', i, 'failed'

        lines += 1

    fp.close()
    print lines, 'valid.'



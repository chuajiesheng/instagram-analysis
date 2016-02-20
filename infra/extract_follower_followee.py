import sys
import json


def read_line(doc, output):
    json_object = json.loads(doc)

    identifier = ''
    if 'id' in json_object:
        identifier = json_object['id']
    elif 'twitter_id_str' in json_object:
        identifier = json_object['twitter_id_str']
    else:
        print json_object

    followers = 0
    following = 0
    media = 0
    if 'counts' in json_object:
        followers = json_object['counts']['followed_by']
        following = json_object['counts']['follows']
        media = json_object['counts']['media']

    output_line = '\"%s\",\"%s\",%s,%s,%s\n' % (identifier,
                                        json_object['username'],
                                        followers,
                                        following,
                                        media)
    output.write(output_line)


def main():
    input_file = sys.argv[1]

    print '\nReading', input_file
    fp = open(input_file)
    output_fp = open('counts.csv', 'w+')

    output_fp.write('\"id\", \"username\", \"followers\", \"following\", \"media\"\n')
    for i, line in enumerate(fp):
        read_line(line, output_fp)

    fp.close()
    output_fp.close()

if __name__ == '__main__':
    main()


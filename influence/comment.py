import urllib
import json

ACCESS_TOKEN = '3067414468.b59fbe4.bfd922cb49fb401e9c2c08ba537f1b4b'
INSTAGRAM_DOWNLOAD_URL = 'https://api.instagram.com/v1/media/{}/comments?access_token=%s' % ACCESS_TOKEN
DOWNLOAD_URL = 'http://iconosquare.com/controller_nl.php?action=nlGetMethod&method=mediaComments&value={}'


class Comment:
    json = None

    def __init__(self, json):
        self.json = json

    def id(self):
        return self.json['id']

    def created_time(self):
        return int(self.json['created_time'])

    def text(self):
        return self.json['text']

    def user(self):
        return self.json['from']

    def username(self):
        return self.user()['username']

    def user_profile_picture(self):
        return self.user()['profile_picture']

    def user_id(self):
        return self.user()['id']

    def user_full_name(self):
        return self.user()['full_name']

    def __eq__(self, other):
        return type(self) == type(other) and self.id() == other.id()


class CommentHelper:
    def __init__(self):
        pass

    @staticmethod
    def get_comment(media_id):
        comments = []

        json = CommentHelper.download(media_id)

        if json is None:
            return []

        if 'data' not in json.keys():
            print json

        dataset = json['data']
        for obj in dataset:
            comments.append(Comment(obj))

        return comments

    @staticmethod
    def download(media_id):
        download_url = DOWNLOAD_URL.format(media_id)
        response = urllib.urlopen(download_url)
        result = response.read()

        if result == '' or result == '400':
            return None

        try:
            data = json.loads(result)
        except ValueError, e:
            print media_id, e, 'for', result
            return None

        if 'meta' in data.keys() and 'code' in data['meta'].keys() and data['meta']['code'] == 400:
            return None

        return data


if __name__ == '__main__':
    MEDIA_ID = '1108626510904721584_35720927'
    comments = CommentHelper.get_comment(MEDIA_ID)
    print len(comments)
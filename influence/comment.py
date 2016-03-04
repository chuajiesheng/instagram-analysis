import urllib, json

DOWNLOAD_URL = 'http://iconosquare.com/controller_nl.php?action=nlGetMethod&method=mediaComments&value={}'


class Comment:
    json = None

    def __init__(self, json):
        self.json = json

    def id(self):
        return self.json['id']

    def created_time(self):
        return self.json['created_time']

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
        dataset = json['data']
        for obj in dataset:
            comments.append(Comment(obj))

        return comments

    @staticmethod
    def download(media_id):
        download_url = DOWNLOAD_URL.format(media_id)
        response = urllib.urlopen(download_url)
        data = json.loads(response.read())
        return data


if __name__ == '__main__':
    MEDIA_ID = '1108626510904721584_35720927'
    comments = CommentHelper.get_comment(MEDIA_ID)
    print len(comments)
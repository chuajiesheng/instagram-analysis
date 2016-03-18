import urllib, json

DOWNLOAD_URL = 'http://iconosquare.com/rqig.php?e=/users/{}&a=ico2&t=198845160.d949468.60c75ba61c524f4c91719a2f10ea19d1'


class User:
    json = None

    def __init__(self, json):
        self.json = json

    def id(self):
        return self.json['id']

    def username(self):
        return self.json['username']


class UserHelper:
    def __init__(self):
        pass

    @staticmethod
    def get_user(user_id):
        comments = []

        json = UserHelper.download(user_id)
        data = json['data']
        return User(data)

    @staticmethod
    def download(media_id):
        download_url = DOWNLOAD_URL.format(media_id)
        response = urllib.urlopen(download_url)
        data = json.loads(response.read())
        return data


if __name__ == '__main__':
    USER_ID = '529718025'
    user = UserHelper.get_user(USER_ID)
    print user.username()
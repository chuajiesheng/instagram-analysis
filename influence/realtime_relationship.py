import json
import urllib

ACCESS_TOKEN = '198845160.b59fbe4.d5c35ad8c01543fcac377219fffb805e'
URL = 'https://api.instagram.com/v1/users/{}/followed-by?access_token={}'


class RealtimeRelationshipHelper:
    def __init__(self):
        pass

    @staticmethod
    def download_all(insta_user_id, log=False):
        followers = []
        next_url = URL.format(insta_user_id, ACCESS_TOKEN)

        while next_url is not None:
            next_url, followed_by = RealtimeRelationshipHelper.download(next_url)
            followers.extend(followed_by)

            if log:
                print 'next_url', next_url
                print 'followed_by', len(followed_by)

        print insta_user_id, 'have', len(followers), 'followers'

        return followers

    @staticmethod
    def download(url):
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        code = response.getcode()
        if code != 200:
            return None, []

        pagination = data['pagination']
        next_url = pagination['next_url'] if (pagination is not None and 'next_url' in pagination) else None
        followed_by = [user['id'] for user in data['data']]
        return next_url, followed_by


if __name__ == '__main__':
    INSTA_USER_ID = '4641204'
    RealtimeRelationshipHelper.download_all(INSTA_USER_ID, True)

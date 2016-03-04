import networkx as nx
import relationship as rs
import media as me
import comment as co
import realtime_relationship as rr
from elasticsearch import Elasticsearch


MEDIA_ID = '1107620890619006408_256997418' # https://www.instagram.com/p/9fD1TjJc3I/
FILENAME = 'run/comment_network_{}.graphml'
comments = []
nodes = dict()


def get_relationship(source_node):
    followers = rs.RelationshipHelper.get_relationship(source_node).followers()

    if len(followers) == 0:
        followers = rr.RealtimeRelationshipHelper.download_all(source_node)
        print 'obtained', len(followers), 'relationship real-time'

    return followers


def add_comment(graph, source_node, source_node_level):
    print source_node, 'at level', source_node_level
    if source_node_level > 5:
        return

    followers = get_relationship(source_node)

    if len(followers) == 0:
        error_file = open('missing_relationship.txt', 'a')
        error_file.write(source_node + '\n')
        error_file.close()
        print source_node, 'empty'
        return

    followers_set = set(followers)
    comment_user_set = set([comment.user_id() for comment in comments])
    intersection = followers_set.intersection(comment_user_set)
    print 'found', len(intersection), 'for', source_node

    for user in intersection:
        graph.add_node(user)

        comments_by_user = filter(lambda c: c.user_id() == user, comments)
        for comment in comments_by_user:
            graph.add_edge(source_node, user, comment_id=comment.id())
            comments.remove(comment)

    print 'left', len(comments), 'comments'

    i = 0
    for user in intersection:
        i += 1
        print 'level', source_node_level, 'at', i, 'of', len(intersection)
        add_comment(graph, user, source_node_level + 1)


if __name__ == '__main__':
    host = ['http://localhost:9200']
    es = Elasticsearch(host)
    media = me.MediaHelper.get_media(MEDIA_ID)
    comments = co.CommentHelper.get_comment(MEDIA_ID)

    G = nx.Graph()
    G.add_node(media.user_id(), username=media.username())

    add_comment(G, media.user_id(), 0)

    filename = FILENAME.format(MEDIA_ID)
    nx.write_graphml(G, filename)

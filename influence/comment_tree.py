import networkx as nx
import relationship as rs
import media as me
import comment as co
from elasticsearch import Elasticsearch


MEDIA_ID = '1107620890619006408_256997418' # https://www.instagram.com/p/9fD1TjJc3I/
comments = []
nodes = dict()


def add_comment(graph, source_node, source_node_level):
    print source_node, 'at level', source_node_level
    if source_node_level > 5:
        return

    r = rs.RelationshipHelper.get_relationship(source_node)

    if len(r.followers()) == 0:
        error_file = open('missing_relationship.txt', 'a')
        error_file.write(source_node + '\n')
        error_file.close()
        print source_node, 'empty'
        return

    followers_set = set(r.followers())
    comment_user_set = set([comment.user_id() for comment in comments])
    intersection = followers_set.intersection(comment_user_set)
    print 'found', len(intersection), 'for', source_node

    for user in intersection:
        graph.add_node(user)

        comments_by_user = (comment for comment in comments if comment.user_id() == user)
        for comment in comments_by_user:
            graph.add_edge(source_node, user, comment_id=comment.id())
            comments.remove(comment)

    i = 0
    for user in intersection:
        i += 1
        print 'level', source_node_level, 'at', i, 'of', len(intersection)
        add_comment(graph, user, source_node_level + 1)

    print 'left', len(comments), 'comments'


if __name__ == '__main__':
    host = ['http://localhost:9200']
    es = Elasticsearch(host)
    media = me.MediaHelper.get_media(MEDIA_ID)
    comments = co.CommentHelper.get_comment(MEDIA_ID)

    G = nx.Graph()
    G.add_node(media.user_id(), username=media.username())

    add_comment(G, media.user_id(), 0)

    nx.write_graphml(G, "comment_network.graphml")

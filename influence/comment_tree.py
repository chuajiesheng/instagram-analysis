import networkx as nx
import relationship as rs
import media as me
import comment as co
import realtime_relationship as rr
from elasticsearch import Elasticsearch
import matplotlib.pyplot as plt
import code


MEDIA_ID = '1101457419536463341_1507143100' # https://www.instagram.com/p/9fD1TjJc3I/
FILENAME = 'run/comment_network_{}.graphml'
IMAGE_FILENAME = 'run/comment_network_{}.png'
MISSING_RELATIONSHIP = 'run/missing_relationship.txt'
JSON_SCRIPT_FILE = 'run/comment_network_{}.js'
JSON_OBJECT_TEMPLATE = "{source: \"%s\", target: \"%s\", type: \"%s\"},"
comments = []
nodes = dict()


def get_relationship(source_node):
    followers = rs.RelationshipHelper.get_relationship(source_node).followers()

    if len(followers) == 0:
        followers = rr.RealtimeRelationshipHelper.download_all(source_node)

    return followers


def find_intersected_followers(followers):
    followers_set = set(followers)
    comment_user_set = set([comment.user_id() for comment in comments])
    intersection = followers_set.intersection(comment_user_set)
    return intersection


def get_latest_incoming_edge(graph, source_node, comment):
    lower_limit = 0
    upper_limit = comment.created_time()

    edges = graph.in_edges(source_node, data=True)

    if len(edges) > 0:
        print 'given', source_node, 'found', edges

    for edge in edges:
        created_time = int(edge[2]['created_time'])
        if lower_limit < created_time < upper_limit:
            lower_limit = created_time

    return lower_limit



def add_edges(graph, intersection, source_node):
    for user in intersection:
        comments_by_user = filter(lambda c: c.user_id() == user, comments)
        for comment in comments_by_user:
            created_time = comment.created_time()
            latest_influence_comment = get_latest_incoming_edge(graph, source_node, comment)
            time_diff = created_time - latest_influence_comment

            if time_diff < 0:
                print 'comment', comment.id(), 'created on', created_time, 'but previous comment created', latest_influence_comment

            graph.add_edge(source_node, user, comment_id=comment.id(), created_time=created_time, time_diff=time_diff)
            comments.remove(comment)


def add_comment(graph, source_node, source_node_level):
    if source_node_level > 5:
        return

    followers = get_relationship(source_node)

    if len(followers) == 0:
        error_file = open(MISSING_RELATIONSHIP, 'a')
        error_file.write(source_node + '\n')
        error_file.close()
        return

    intersection = find_intersected_followers(followers)
    add_edges(graph, intersection, source_node)
    map(lambda c: add_comment(graph, c, source_node_level + 1), intersection)


def output_script_file(graph):
    script_file = open(JSON_SCRIPT_FILE.format(MEDIA_ID), 'w')
    script_file.write('var links = [')

    for edge in graph.edges():
        # code.interact(local=locals())
        edge_type = 'default'
        if edge[2]['time_diff'] != edge[2]['created_time']:
            edge_type = 'influence'

        script_file.write(JSON_OBJECT_TEMPLATE % (edge[0], edge[1], edge_type))

    script_file.write('];')
    script_file.close()


if __name__ == '__main__':
    host = ['http://localhost:9200']
    es = Elasticsearch(host)
    media = me.MediaHelper.get_media(MEDIA_ID)
    comments = co.CommentHelper.get_comment(MEDIA_ID)

    G = nx.DiGraph()
    G.add_node(media.user_id(), username=media.username(), link=media.link())

    add_comment(G, media.user_id(), 0)

    filename = FILENAME.format(MEDIA_ID)
    nx.write_graphml(G, filename)

    nx.draw(G)
    plt.show(block=False)
    plt.savefig(IMAGE_FILENAME.format(MEDIA_ID), format="PNG")

    output_script_file(G)

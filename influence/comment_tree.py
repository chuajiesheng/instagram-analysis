import networkx as nx
import relationship as rs
import media as me
import comment as co
import realtime_relationship as rr
from elasticsearch import Elasticsearch
import matplotlib.pyplot as plt
import math
import code
from datetime import datetime


MEDIA_IDS = ['1101457419536463341_1507143100'] # https://www.instagram.com/p/9fD1TjJc3I/
FILENAME = 'run/comment_network_{}.graphml'
IMAGE_FILENAME = 'run/comment_network_{}.png'
MISSING_RELATIONSHIP = 'run/missing_relationship.txt'
JSON_SCRIPT_FILE = 'run/comment_network_{}.js'
JSON_OBJECT_TEMPLATE = "{source: \"%s\", target: \"%s\", influence: \"%s\", type: \"%s\"},"
comments = []


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
            time_diff = datetime.utcfromtimestamp(float(created_time)) - datetime.utcfromtimestamp(float(latest_influence_comment))
            time_diff_in_hours = math.ceil(float(time_diff.seconds) / 60 / 60)
            influence = 1 / time_diff_in_hours

            if time_diff.seconds < 0:
                print 'comment', comment.id(), 'created on', created_time, 'but previous comment created', latest_influence_comment

            print 'adding edge', source_node, user
            graph.add_node(user, username=comment.username(), total_influence=0.0)
            graph.add_edge(source_node, user,
                           comment_id=comment.id(), comment=comment.text(),
                           created_time=created_time, time_diff=time_diff.seconds, influence=influence)
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


def output_script_file(graph, media_id):
    script_file = open(JSON_SCRIPT_FILE.format(media_id), 'w')
    script_file.write('var links = [')

    for edge in graph.edges(data=True):
        source_node = edge[0]
        source_node_name = graph.node[source_node]['username']

        node = edge[1]
        node_name = graph.node[node]['username']

        edge_type = 'default'
        if edge[2]['influence'] > 0:
            edge_type = 'influence'

        script_file.write(JSON_OBJECT_TEMPLATE %
                          (source_node_name, node_name, graph.node[node]['total_influence'], edge_type))

    script_file.write('];')
    script_file.close()


def calculate_total_influence(graph, root_node, source_node):
    total_influence = 0.0
    for node in graph[source_node].keys():
        edge = graph[source_node][node]
        total_influence += edge['influence']
        # code.interact(local=locals())
        if node != root_node:
            total_influence += calculate_total_influence(graph, root_node, node)

    print 'total_influence', source_node, total_influence
    graph[source_node]['total_influence'] = total_influence
    return total_influence

if __name__ == '__main__':
    host = ['http://localhost:9200']
    es = Elasticsearch(host)

    for media_id in MEDIA_IDS:
        print 'running', media_id
        comments = []

        media = me.MediaHelper.get_media(media_id)
        comments = co.CommentHelper.get_comment(media_id)

        G = nx.DiGraph()
        G.add_node(media.user_id(), username=media.username(), link=media.link(), total_influence=0.0)

        add_comment(G, media.user_id(), 0)
        calculate_total_influence(G, media.user_id(), media.user_id())

        output_script_file(G, media_id)

        filename = FILENAME.format(media_id)
        nx.write_graphml(G, filename)

        nx.draw(G)
        plt.show(block=False)
        plt.savefig(IMAGE_FILENAME.format(media_id), format="PNG")


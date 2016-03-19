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


MEDIA_IDS = ['1121729201701872441_2697007']
FILENAME = 'run/comment_network_{}.graphml'
IMAGE_FILENAME = 'run/comment_network_{}.png'
MISSING_RELATIONSHIP = 'run/missing_relationship.txt'
JSON_SCRIPT_FILE = 'run/comment_network_{}.js'
JSON_OBJECT_TEMPLATE = "{source: \"%s\", target: \"%s\", source_total_influence: \"%s\", target_total_influence: \"%s\", type: \"%s\"},"
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
            if user not in graph.node:
                graph.add_node(user, username=comment.username())

            graph.add_edge(source_node, user,
                           comment_id=comment.id(), comment=comment.text(),
                           created_time=created_time, time_diff=time_diff.seconds,
                           influence=influence, weight=influence)
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


def output_script_file(graph, root_node, media_id):
    script_file = open(JSON_SCRIPT_FILE.format(media_id), 'w')
    script_file.write('var links = [')

    for node in graph.node.keys():
        # code.interact(local=locals())
        node_name = graph.node[node]['username']
        node_total_influence = graph.node[node]['total_influence']

        keys = graph.edge[node].keys()
        for key in keys:
            if key in graph.node:
                edge = graph.edge[node][key]

                other_node = graph.node[key]
                other_node_name = other_node['username']
                other_node_total_influence = other_node['total_influence']

                comment = edge['comment']
                created_time = edge['created_time']
                influence = edge['influence']

                edge_type = 'default'

                if node != root_node and influence > 0:
                    edge_type = 'influence'

                script_file.write(JSON_OBJECT_TEMPLATE %
                                  (node_name, other_node_name, node_total_influence, other_node_total_influence, edge_type))

    script_file.write('];')
    script_file.close()


def calculate_total_influence(graph, root_node, source_node):
    total_influence = 0.0
    for node in graph[source_node].keys():
        edge = graph[source_node][node]
        total_influence += edge['influence']
        if node != root_node:
            total_influence += calculate_total_influence(graph, root_node, node)

    print 'total_influence', source_node, total_influence
    graph.node[source_node]['total_influence'] = str(total_influence)
    graph.node[source_node]['weight'] = str(total_influence)
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
        G.add_node(media.user_id(), username=media.username(), link=media.link())

        add_comment(G, media.user_id(), 0)
        # code.interact(local=locals())

        calculate_total_influence(G, media.user_id(), media.user_id())
        output_script_file(G, media.user_id(), media_id)

        nx.draw(G)
        plt.show(block=False)
        plt.savefig(IMAGE_FILENAME.format(media_id), format="PNG")

        filename = FILENAME.format(media_id)
        nx.write_graphml(G, filename)




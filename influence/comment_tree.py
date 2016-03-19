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
import csv


MEDIA_IDS = ['1120521602937694152_511289136',
             '1107226302945107697_10615198',
             '1138177160224569759_204847429',
             '1154333559965647101_302326055',
             '1135218645765676768_231949310',
             '1129684818227258761_181896432',
             '1101210696952364281_293188374',
             '1158464186162135032_293188374',
             '1099013123541875812_293188374',
             '1118095516856794899_293188374',
             '1130975450563828497_23745725',
             '1149798294806377561_5589652',
             '1130467813934001652_39220794',
             '1133786935846007255_192231307',
             '1135569371711887552_573593285',
             '1101232673898673213_5589652',
             '1127380535685420183_11743588',
             '1124251969314884707_1139660770',
             '1129038924486187274_195426445',
             '1113730407457105505_9730520',
             '1133302489363153363_35720927',
             '1119954715539983584_511234658',
             '1138198007249693806_22612874',
             '1152990067611828713_35720927',
             '1103373993652386505_20015893',
             '1108817316691091284_1111047854',
             '1103399328056354240_413908336',
             '1120299625762451657_2576211',
             '1106503423643624908_9730520',
             '1158167954094302866_9730520',
             '1129981839188968970_242810016',
             '1136619715197596101_1385810955',
             '1114845661055692097_1470371802',
             '1144150486577771416_1385810955',
             '1102521797801079264_1385810955',
             '1141098632581544738_6308389',
             '1135994281632145319_610235966',
             '1099983138533472736_6308389',
             '1109306662461840450_10615198',
             '1145538922235099839_6308389',
             '1144647402843439311_35720927',
             '1162229019753480448_35720927',
             '1107134807559400857_39220794',
             '1140616432104270869_39220794',
             '1158113280204646858_463044265']

FILENAME = 'run/comment_network_{}.graphml'
IMAGE_FILENAME = 'run/comment_network_{}.png'
MISSING_RELATIONSHIP = 'run/missing_relationship.txt'
JSON_SCRIPT_FILE = 'run/comment_network_{}.js'
CSV_FILE = 'run/comment_network_{}.csv'
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


def get_latest_incoming_edge(graph, source_node, comment, log=False):
    lower_limit = 0
    upper_limit = comment.created_time()

    edges = graph.in_edges(source_node, data=True)

    if log and len(edges) > 0:
        print 'given', source_node, 'found', edges

    for edge in edges:
        created_time = int(edge[2]['created_time'])
        if lower_limit < created_time < upper_limit:
            lower_limit = created_time

    return lower_limit


def add_edges(graph, intersection, source_node, log=False):
    for user in intersection:
        comments_by_user = filter(lambda c: c.user_id() == user, comments)
        for comment in comments_by_user:
            created_time = comment.created_time()
            latest_influence_comment = get_latest_incoming_edge(graph, source_node, comment)
            time_diff = datetime.utcfromtimestamp(float(created_time)) - datetime.utcfromtimestamp(float(latest_influence_comment))
            time_diff_in_hours = math.ceil(float(time_diff.seconds) / 60 / 60)
            influence = 1 / time_diff_in_hours

            if log and time_diff.seconds < 0:
                print 'comment', comment.id(), 'created on', created_time, 'but previous comment created', latest_influence_comment

            if log:
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


def calculate_total_influence(graph, root_node, source_node, log=False):
    total_influence = 0.0
    for node in graph[source_node].keys():
        edge = graph[source_node][node]
        total_influence += edge['influence']
        if node != root_node:
            total_influence += calculate_total_influence(graph, root_node, node)


    graph.node[source_node]['total_influence'] = str(total_influence)
    graph.node[source_node]['weight'] = str(total_influence)

    if root_node == source_node:
        print 'total_influence', source_node, total_influence

    return total_influence


def output_csv_file(graph, media_id):
    with open(CSV_FILE.format(media_id), 'w') as csvfile:
        fieldnames = ['media_id', 'comment_id', 'comment', 'created_time', 'comment_author_id', 'comment_author_name', 'following_user', 'following_user_id', 'time_diff', 'influence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for node in graph.node.keys():
            node_name = graph.node[node]['username']

            keys = graph.edge[node].keys()
            for key in keys:
                if key in graph.node:
                    edge = graph.edge[node][key]

                    other_node = graph.node[key]
                    other_node_name = other_node['username']

                    comment_id = edge['comment_id']
                    comment = edge['comment']
                    created_time = edge['created_time']
                    time_diff = edge['time_diff']
                    influence = edge['influence']

                    writer.writerow({
                        'media_id': media_id,
                        'comment_id': str(comment_id),
                        'comment': comment.encode('ascii', 'ignore'),
                        'created_time': created_time,
                        'comment_author_id': key,
                        'comment_author_name': other_node_name,
                        'following_user': node_name,
                        'following_user_id': node_name,
                        'time_diff': str(time_diff),
                        'influence': influence
                    })


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
        output_csv_file(G, media_id)

        nx.draw(G)
        plt.show(block=False)
        plt.savefig(IMAGE_FILENAME.format(media_id), format="PNG")

        filename = FILENAME.format(media_id)
        nx.write_graphml(G, filename)




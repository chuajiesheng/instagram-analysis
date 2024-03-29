import networkx as nx
import relationship as rs


INIT_INSTA_USER_ID = '1438863821'
MISSING_RELATIONSHIP = 'run/missing_relationship.txt'
nodes = dict()


def add_child(graph, source_node, source_node_level):
    print source_node, 'at level', source_node_level
    if source_node_level > 2:
        return

    r = rs.RelationshipHelper.get_relationship(source_node)
    i = 0

    if len(r.followers()) == 0:
        error_file = open(MISSING_RELATIONSHIP, 'a')
        error_file.write(source_node + '\n')
        error_file.close()
        print source_node, 'empty'

    for follower in r.followers():
        if follower in nodes.keys():
            continue

        nodes[follower] = source_node_level + 1
        graph.add_node(follower)
        graph.add_edge(source_node, follower)

        i += 1
        if i % 10000 == 0:
            print 'at', str(i), 'of', len(r.followers())

    for follower in r.followers():
        add_child(graph, follower, source_node_level + 1)


if __name__ == '__main__':
    G = nx.Graph()
    G.add_node(INIT_INSTA_USER_ID, username='thejianhaotan')

    add_child(G, INIT_INSTA_USER_ID, 0)

    nx.write_graphml(G, "3-level_network.graphml")

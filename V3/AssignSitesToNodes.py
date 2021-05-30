import networkx as nx
import osmnx as ox
from shapely import wkt
from shapely.geometry.linestring import LineString
from copy import deepcopy
import numpy as np


def generate_nodes_list(graph):
    return sorted(list(graph.nodes.data()), key=lambda x: float(x[1]['UnitsWithinHalfMile']))


def check_for_uncovered_units(graph):
    return bool(sum(float(edge[2]['weight']) for edge in list(graph.edges.data()) if 'weight' in edge[2]))


def calculate_node_weights(node_list, G):
    print("ah", node_list)
    for node in node_list:  # Node list will be a simple list of nodes representing the top n nodes by UnitsWithinHalfMile
        print("basa")
        ego_graph = nx.ego_graph(G, node, radius=805, undirected=True,
                                 distance='length')  # meters in a half-mile, rounded to the nearest meter
        print("tiki")
        edge_weights_list = [int(float(edge[2]['weight'])) for edge in list(ego_graph.edges.data()) if
                             'weight' in edge[2]]
        edge_weights_sum = np.nansum(edge_weights_list)
        G.nodes[node]['UnitsWithinHalfMile'] = edge_weights_sum
    return G

def recalculate_node_weights(node_list, G):
    """Finds nodes in G that were connected to nodes in ego"""

if __name__ == '__main__':
    print("Loading newly created graphml, now with 'UnitsWithinHalfMile' as an available attribute.")
    g = nx.read_graphml(
        r'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\graphFiles\nyc_graph_3_unitsPerNode.graphml')
    print("Adjusting graph attributes for plotting using osmnx.")
    nyc_graph = nx.read_graphml(
        r'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\graphFiles\nyc_graph_1.graphml')
    nyc_graph.to_undirected()
    nyc_graph.remove_edges_from(list(nyc_graph.edges()))
    nyc_graph.remove_nodes_from(list(nyc_graph.nodes()))
    G = deepcopy(nyc_graph)
    nyc_graph.add_nodes_from(list(g.nodes(data=True)))
    nyc_graph.add_edges_from(list(g.edges.data(keys=True)))

    for u, v, k, data in nyc_graph.edges(data=True, keys=True):
        w = int(data['AdjUnitsRes']) if 'AdjUnitsRes' in data else 1.0
        if G.has_edge(u, v):
            G[u][v][0]['weight'] += w
            G[u][v][0]['geometry'] = wkt.loads(data['geometry'])
            G[u][v][0]['length'] = data['length']

        else:
            G.add_edge(u, v, weight=w)
            G[u][v][0]['geometry'] = wkt.loads(data['geometry'])
            G[u][v][0]['length'] = data['length']

    for node in nyc_graph.nodes(data=True):
        # print(" Fixing node:", node)
        G.nodes[node[0]]['geometry'] = wkt.loads(node[1]['geometry'])
        G.nodes[node[0]]['x'] = G.nodes[node[0]]['geometry'].x
        G.nodes[node[0]]['y'] = G.nodes[node[0]]['geometry'].y
        G.nodes[node[0]]['UnitsWithinHalfMile'] = node[1]['UnitsWithinHalfMile']

    print("Now generating a heatmap showing residential units within "
          "a half-mile's walking distance of every intersection in Manhattan.")
    nyc_graph = G
    nodes_list = generate_nodes_list(nyc_graph)
    print(nodes_list)
    uncovered_units = check_for_uncovered_units(nyc_graph)
    print(uncovered_units)
    site_nodes = []
    loop_count = 0
    ox.plot_graph(nyc_graph, node_size=0, show=True, save=True,
                  filepath=rf'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\imageFiles\assignDropOffsToNodes\manhattan\mn_frame_{str(loop_count)}.png',
                  close=True)
    print(nyc_graph.edges(data=True))

    while uncovered_units:
        loop_count += 1
        most_populous_node = nodes_list[-1][0]
        print(f"Loop {loop_count}. Most populous node is:", most_populous_node)
        # print(nyc_graph.edges(data=True))
        site_nodes.append(most_populous_node)
        print("generating ego")
        ego_graph = nx.ego_graph(nyc_graph, most_populous_node, radius=805, undirected=True,
                                 distance='length')  # meters in a half-mile, rounded to the nearest meter
        ego_nodes = list(ego_graph.nodes())
        print("Ego nodes for removal:", ego_nodes)
        nyc_graph.remove_nodes_from(ego_nodes)

        nodes_list = generate_nodes_list(nyc_graph)
        print(type(nodes_list))
        nyc_graph = calculate_node_weights([node[0] for node in nodes_list[:10]], nyc_graph)
        uncovered_units = check_for_uncovered_units(nyc_graph)
        try:
            ox.plot_graph(ego_graph, node_size=0, show=False, save=True,
                          filepath=rf'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\imageFiles\assignDropOffsToNodes\local\local_frame_{str(loop_count)}.png',
                          close=True)
            ox.plot_graph(nyc_graph, node_size=0, show=False, save=True,
                          filepath=rf'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\imageFiles\assignDropOffsToNodes\manhattan\mn_frame_{str(loop_count)}.png',
                          close=True)

        except:
            print(f'ERROR: exception on node {most_populous_node}, loop {loop_count}.')
            pass

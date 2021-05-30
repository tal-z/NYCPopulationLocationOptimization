from igraph import *
import ast
import numpy as np
import networkx as nx
import osmnx as ox
from copy import deepcopy
from shapely import wkt

g = Graph.Load(
    r'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\graphFiles\nyc_graph_2_unitsPerEdge.graphml',
    format='graphml')
for e in g.es:
    e['length'] = int(round(float(e['length'])))


def generate_ego_graph(vtx, graph):
    """Takes a vertex and default igraph object,
    and returns a tuple with vertex and ego graph object. E.g. (v, eg)"""
    distances = graph.shortest_paths(source=vtx, target=graph.vs,
                                     weights='length', mode='all')[0]
    vert_distances_dict = {}
    for vert, dist in zip(graph.vs, distances):
        if dist <= 805:
            vert_distances_dict[vert.index] = dist
    if list(vert_distances_dict.keys()):
        ego_graph = graph.induced_subgraph(list(vert_distances_dict.keys()))
        return ego_graph
    else:
        return None


def sum_edge_weights(ego_graph, weight='AdjUnitsRes'):
    """Takes an igraph object, and returns a sum of a given attribute's values."""
    edge_weights_list = [ast.literal_eval(weight) for weight in list(ego_graph.es[weight])]
    edge_weights_sum = np.nansum(edge_weights_list)
    return edge_weights_sum


def calculate_node_weight(vtx):
    ego_graph = generate_ego_graph(vtx, g)
    ew_sum = sum_edge_weights(ego_graph)
    g.vs[vtx]['UnitsWithinHalfMile'] = ew_sum
    print("  Node", vtx)


if __name__ == '__main__':

    print(f"Calculating number of residential units within a half-mile's walking distance of {len(g.vs())} nodes.")
    for vertex in range(len(g.vs())):
        calculate_node_weight(vertex)
    print("Saving new graph with node weights to file, so that we don't have to do this again.")
    g.save(r'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\graphFiles\nyc_graph_3_unitsPerNode.graphml', format='graphml')

    print("Loading newly created graphml, now with 'UnitsWithinHalfMile' as an available attribute.")
    g = nx.read_graphml(r'C:\Users\PC\PycharmProjects\NYCPopulationLocationOptimization\V3\graphFiles\nyc_graph_3_unitsPerNode.graphml')
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
        else:
            G.add_edge(u, v, weight=w)
            G[u][v][0]['geometry'] = wkt.loads(data['geometry'])

    for node in nyc_graph.nodes(data=True):
        print(" Fixing node:", node)
        G.nodes[node[0]]['geometry'] = wkt.loads(node[1]['geometry'])
        G.nodes[node[0]]['x'] = G.nodes[node[0]]['geometry'].x
        G.nodes[node[0]]['y'] = G.nodes[node[0]]['geometry'].y
        G.nodes[node[0]]['UnitsWithinHalfMile'] = node[1]['UnitsWithinHalfMile']

    print("Now generating a heatmap showing residential units within "
          "a half-mile's walking distance of every intersection in Manhattan.")
    nyc_graph = G
    nc = ox.plot.get_node_colors_by_attr(nyc_graph, 'UnitsWithinHalfMile', cmap='hot_r', start=0, stop=.75)
    ox.plot_graph(nyc_graph, node_size=1, node_color=nc, save=True,
                  filepath='imageFiles/ManhattanIntersectionHeatmap.png', dpi=800)
    print("Done!")

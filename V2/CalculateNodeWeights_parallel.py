import numpy as np
import networkx as nx
import osmnx as ox
from multiprocessing import Process, Queue, Pool, cpu_count

ox.config(log_console=True, use_cache=True)
ox.__version__


def add_node_weights(idx_node_graph):
    idx, node, G = idx_node_graph
    print(idx)
    ego_graph = nx.ego_graph(G, node, radius=805, undirected=True, distance='length')  # roughly 805 meters/half-mile
    edge_weights_list = ([int(float(edge[2]['AdjUnitsRes']))
                          for edge in list(ego_graph.edges.data())
                          if 'AdjUnitsRes' in edge[2]])
    edge_weights_sum = np.nansum(edge_weights_list)
    G.nodes[node]['UnitsWithinHalfMile'] = edge_weights_sum


if __name__ == '__main__':
    nyc_graph = ox.load_graphml('nyc_graph_2_allocateUnitsToEdges.graphml')
    nodes = list(nyc_graph.nodes)
    indexed_nodes = [(idx, node, nyc_graph) for idx, node in zip(range(len(nodes)), nodes)]
    pool = Pool(max(cpu_count()//2, 1))
    pool.map(func=add_node_weights, iterable=indexed_nodes)
    ox.save_graphml(nyc_graph, 'nyc_graph_3_sumEdgeUnitsPerNode.graphml')

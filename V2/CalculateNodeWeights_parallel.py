import numpy as np
import networkx as nx
import osmnx as ox
from multiprocessing import  Process, Queue, Pool, cpu_count

ox.config(log_console=True, use_cache=True)
ox.__version__

"""
def add_node_weights(nodes, queue, G=nyc_graph):
#def add_node_weights(nodes, G=nyc_graph):
    count = 0
    for n in nodes:
        count+=1
        print(count)
        ego_graph = nx.ego_graph(G, n, radius=805, undirected=True, distance='length') # meters in a half-mile, rounded to the nearest meter
        edge_weights_list = [int(float(edge[2]['AdjUnitsRes'])) for edge in list(ego_graph.edges.data()) if 'AdjUnitsRes' in edge[2]]
        edge_weights_sum = np.nansum(edge_weights_list)
        G.nodes[n]['UnitsWithinHalfMile'] = edge_weights_sum
"""


def add_node_weights(idx_node_graph):
    idx, node, G = idx_node_graph
    print(idx)
    ego_graph = nx.ego_graph(G, node, radius=805, undirected=True, distance='length') # meters in a half-mile, rounded to the nearest meter
    edge_weights_list = [int(float(edge[2]['AdjUnitsRes'])) for edge in list(ego_graph.edges.data()) if 'AdjUnitsRes' in edge[2]]
    edge_weights_sum = np.nansum(edge_weights_list)
    G.nodes[node]['UnitsWithinHalfMile'] = edge_weights_sum


if __name__ == '__main__':
    nyc_graph = ox.load_graphml('nyc_graph_2_allocateUnitsToEdges.graphml')
    nodes = list(nyc_graph.nodes)
    indexed_nodes = [(idx,node,nyc_graph) for idx,node in zip(range(len(nodes)),nodes)]
    pool = Pool(cpu_count())
    pool.map(func=add_node_weights, iterable=indexed_nodes)
    ox.save_graphml(nyc_graph, 'nyc_graph_3_sumEdgeUnitsPerNode.graphml')



"""

if __name__ == '__main__':
    nodes = list(nyc_graph.nodes)
    queue = Queue()
    node_weights_process = Process(target=add_node_weights, args=(nodes, queue))
    node_weights_process.start()
    node_weights_process.join()
    while not queue.empty():
        print(queue.get())
    ox.save_graphml(nyc_graph, 'nyc_graph_3_sumEdgeUnitsPerNode.graphml')

"""

"""
# 2. Calculate the number of households reachable within .5 miles
# of each node, and assign that aggregated sum as a node weight.
print(len(list(nyc_graph.nodes)))
node_count = 0
for node in list(nyc_graph.nodes):
    print(node)
    node_count += 1
    ego_graph = nx.ego_graph(nyc_graph, node, radius=805, undirected=True, distance='length') # meters in a half-mile, rounded to the nearest meter
    print(list(ego_graph.edges.data()))
    edge_weights_list = [int(float(edge[2]['AdjUnitsRes'])) for edge in list(ego_graph.edges.data()) if 'AdjUnitsRes' in edge[2]]
    print(edge_weights_list)
    edge_weights_sum = np.nansum(edge_weights_list)
    print(edge_weights_sum)
    nyc_graph.nodes[node]['UnitsWithinHalfMile'] = edge_weights_sum
    print(node_count, node, nyc_graph.nodes[node]['UnitsWithinHalfMile'])


print(list(nyc_graph.nodes(data=True)))
ox.save_graphml(nyc_graph, 'nyc_graph_3_sumEdgeUnitsPerNode.graphml')
"""
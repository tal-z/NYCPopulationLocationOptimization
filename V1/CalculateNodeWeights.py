import numpy as np
import networkx as nx
import osmnx as ox

ox.config(log_console=True, use_cache=True)
ox.__version__




# 1. Read graph from gexf file, which already has households assigned to edges as edge weights
nyc_graph = ox.load_graphml('graphFiles/graphml/mn_step1_allocateUnitsToEdges_20210418.graphml')

# 2. Calculate the number of households reachable within .5 miles
# of each node, and assign that aggregated sum as a node weight.
print(len(list(nyc_graph.nodes)))
node_count = 0
for node in list(nyc_graph.nodes):
    print(node)
    node_count += 1
    ego_graph = nx.ego_graph(nyc_graph, node, radius=805, undirected=False, distance='length') # meters in a half-mile, rounded to the nearest meter
    print(list(ego_graph.edges.data()))
    edge_weights_list = [int(float(edge[2]['UnitsRes'])) for edge in list(ego_graph.edges.data()) if 'UnitsRes' in edge[2]]
    print(edge_weights_list)
    edge_weights_sum = np.nansum(edge_weights_list)
    print(edge_weights_sum)
    nyc_graph.nodes[node]['UnitsWithinHalfMile'] = edge_weights_sum
    print(node_count, node, nyc_graph.nodes[node]['UnitsWithinHalfMile'])

ox.save_graphml(nyc_graph, 'graphFiles/graphml/mn_step2_sumEdgeUnitsPerNode_20210418.graphml')

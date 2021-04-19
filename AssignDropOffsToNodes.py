import numpy as np
import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt


"""
Assignment Strategy
1. For each node, calculate the weight of all edges within d distance.
    - Take the ego graph of the node at .5 miles 
    - Add up the weight of all edges within the ego graph
    - Assign that weight to the node
    - Store the heaviest ego-graph visited on this trip in a variable
    - Store the heaviest node in a list of drop-off locations
2. Remove the ego graph from the original graph.
3. Repeat starting at step 1 on the new, smaller graph. Continue onward until no weighted edges remain.
"""

nyc_graph = ox.load_graphml('graphFiles/graphml/mn_step2_sumEdgeUnitsPerNode_20210418.graphml')

def generate_nodes_list(G):
    return sorted(list(G.nodes.data()), key=lambda x: float(x[1]['UnitsWithinHalfMile']))
nodes_list = generate_nodes_list(nyc_graph)
print(nodes_list)

# Note that uncovered units is not an accurate count of the total remaining units,
# as units may be (and likely are) allocated to multiple nodes.
# This is why I cast it as a boolean.
def check_for_uncovered_units(nodes_list):
    return bool(sum(float(item[1]['UnitsWithinHalfMile']) for item in nodes_list))
uncovered_units = check_for_uncovered_units(nodes_list)
print(uncovered_units)

def calculate_node_weights(G):
    for node in list(G.nodes):
        ego_graph = nx.ego_graph(G, node, radius=805, undirected=False, distance='length')  # meters in a half-mile, rounded to the nearest meter
        edge_weights_list = [int(float(edge[2]['UnitsRes'])) for edge in list(ego_graph.edges.data()) if
                             'UnitsRes' in edge[2]]
        edge_weights_sum = np.nansum(edge_weights_list)
        G.nodes[node]['UnitsWithinHalfMile'] = edge_weights_sum
    return G


dropoff_nodes = []
#fig, ax = plt.subplots()
loop_count = 0
while uncovered_units:
    loop_count += 1
    most_populous_node = nodes_list[-1][0]
    print(nodes_list[-1])
    dropoff_nodes.append(most_populous_node)
    ego_graph = nx.ego_graph(nyc_graph, most_populous_node, radius=805, undirected=True, distance='length') # meters in a half-mile, rounded to the nearest meter
    ego_nodes = list(ego_graph.nodes)
    ego_edges = list(ego_graph.edges)
    nyc_graph.remove_nodes_from(ego_nodes)
    nyc_graph.remove_edges_from(ego_edges)
    nyc_graph = calculate_node_weights(nyc_graph)
    nodes_list = generate_nodes_list(nyc_graph)
    uncovered_units = check_for_uncovered_units(nodes_list)
    try:
        ox.plot_graph(nyc_graph, show=False, save=True, filepath=rf'animationFrames/frame_{str(loop_count)}.png')
    except:
        pass


print(dropoff_nodes)
print(len(dropoff_nodes))


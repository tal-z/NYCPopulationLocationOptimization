# Welcome to the Manhattan Residential Population Location Optimization repo!

This repo holds modules used for answering questions about 
optimizing service locations for Manhattan's residential population, and some resources that I created along the way. 
For example, [this map](https://raw.githubusercontent.com/tal-z/NYCPopulationLocationOptimization/master/V3/imageFiles/ManhattanIntersectionHeatmap.png) (located in the /imageFiles directory) displays color-coded nodes that correspond to the residential population located within .5 miles walking distance of each intersection in Manhattan.

#### Example questions:
1) What is the minimum number of sites needed in order to place a site within .5 miles walking distance of every Manhattan resident?
2) Which Manhattan street corner is within d walking distance of the greatest number of residents?
3) How many service locations are needed in order to allocate x locations for every y residents within a given area?

#### Description of Modules:

###### AllocateUnitsToEdges.py
This module pulls all the data needed for this analysis, 
and sets up our data model for us, which is a network graph. 
The model consists of nodes and edges, 
where every edge represents a walkable street in NYC,
and every node represents an intersection in NYC. 
Edges also have weight attributes, which correspond to their length 
and number of residential units that fall along that edge. 
The outputs of this script are:
  - nyc_graph_1.graphml
  - nyc_graph_2.graphml
  - BldgsNodesEdges_DataModel.png


###### CalculateUnitsNearNodes.py
This module calculates the number of units within a half-mile's 
walking distance of each node in the data model.
This module leverages the Python iGraph library to 
quickly analyze thousands of relationships, generating so-called "ego-graphs."
Ego-graphs are sub-graphs, which contain all the edges and nodes reachable within d 
distance of a given node, where d is an attribute of each edge in the main graph.


###### AssignDropOffsToNodes.py
In Progress! It will attempt to optimize the assignment of sites to nodes, 
given a defined priority. Potential methods may include: 
  - Maximize coverage, Minimize number of sites
  - Optimize service area for a given number of sites 
    (such that sites fill, and don't overflow, capacity)
  - Equalize distribution of sites to populations within districts

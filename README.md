## Structure
#### Modules:
1. AllocateHouseholdsToEdges. Establishes an allocation of NYC households nearest to each edge in a graph of NYC's walkable street/sidewalk network, by interpolating NYC MapPLUTO data with a network graph object derived from Open Street Map data.
2. CalculateNodeWeights. Calculates the weight of all edges within d distance of each node, and assigns the aggregated weights to each node.
3. AllocateDropOffsToCDs. Established the number of drop-offs to be placed per community district, based on population. Can allocate based on a # drop-offs per population or by total # drop-offs
4. DrawBuildingsAndNodes. Produces a high res .pdf of manhattan building footprints and intersection nodes overlaid on MN borough boundaries.
5. AssignDropOffsToNodes. Will determine which nodes are assigned as drop-offs.

## Strategy
####Graph Set-up:
- Edges represent walkable streets
- Nodes represent intersections
- Edge weights represent the number of households along that street.
  - Note that each household is allocated to exactly one edge

####Iterative Placement Method:  
1. For each node, calculate the weight of all edges within d distance.
    - Take the ego graph of the node at .5 miles 
    - Add up the weight of all edges within the ego graph
    - Assign that weight to the node
    - Store the heaviest ego-graph visited on this trip in a variable
    - Store the heaviest node in a list of drop-off locations
2. Remove the ego graph from the original graph.
3. Repeat starting at step 1 on the new, smaller graph. Continue onward until no weighted edges remain.

####Single-run Placement Method:
1. For each node, calculate the weight of all edges within d distance.
    - Take the ego graph of the node at .5 miles 
    - Add up the weight of all edges within the ego graph
    - Assign that weight to the node
2. Determine how many drop-offs to place in each district, by allocating one per 50,000 residents. store those values to an allocation dict.
3. Initialize an empty dict of drop-off nodes per district. Ex: {'101':[], '102':[],...}
4. For each district:
    1. Get a list of nodes that fall within that district.
    2. Sort the list of nodes (highest to lowest) based on population within .5 miles
    3. Check and store the number of nodes already assigned to that district. (take the list length...should be zero to start.)
    4. While there are fewer than n drop-offs placed (where n is the number of drop-offs allocated to the district)
        - For each node in the list of nodes:
            1. Check if it is within 1 mile of any previously-placed node.
            2. If not within 1 mile of another previously-placed node, add that node to the dict of drop-off nodes, and remove it from the list of available nodes.
            3. Re-check and store the number of nodes already assigned to that district.
        - If allocated drop-offs remain unplaced after visiting all nodes in the district, reduce the required distance from other placed nodes, and re-iterate through the list of nodes. Do this recursively until the allocation is met. 
 
## Resources
- ESRI tool for building queries against MapPLUTO data: https://hub.arcgis.com/datasets/1564ace0b4f44318ac39920737f9bd07_0/geoservice?geometry=-74.911%2C40.523%2C-73.044%2C40.888
- Paper by Jeff Boeing on OSMnx: https://www.sciencedirect.com/science/article/pii/S0198971516303970
- web-hosted population stats by community board: https://edm-publishing.nyc3.digitaloceanspaces.com/db-community-profiles/latest/output/cd_demo_age_gender.csv
- NYC Boundaries Map: https://boundaries.beta.nyc/
import os
import requests

import scipy
from sodapy import Socrata
import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx as ox
import numpy as np

ox.config(log_console=True, use_cache=True)
ox.__version__

pd.set_option('display.max_columns', 500)


# 1. Compose multi-directional graph out of New York City's walkable streets.
## Currently filtered for Manhattan only
"""
nyc_boroughs_withwater = gpd.read_file('https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Borough_Boundary_Water_Included/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson').head(1)
borough_graphs = [ox.graph_from_polygon(geom, network_type='walk', simplify=False) for geom in nyc_boroughs_withwater['geometry']]
nyc_graph = nx.compose_all(borough_graphs)
nyc_graph = nx.to_undirected(nyc_graph)
nyc_graph = ox.save_graphml(nyc_graph, "nyc_graph_1.graphml")
"""
nyc_graph = ox.load_graphml("nyc_graph_1.graphml")
# 2. Get building data from NYC Open Data
## Currently filtered for Manhattan onlu (based on BBL first digit)
client = Socrata("data.cityofnewyork.us",
                 'odQdEcIxnATZPym3KySwgWw27',
                 username=os.getenv('username'),
                 password=os.getenv('password'))
results = client.get("viz9-mrjz",
                     content_type='geojson',
                     where=f"mpluto_bbl like '1%'", # is in Manhattan
                     limit=1100000)
building_footprints_gdf = gpd.GeoDataFrame.from_features(results).set_crs(epsg=4326, inplace=True)

print(building_footprints_gdf.columns)
print(building_footprints_gdf.shape)

# 3. Calculate the centroid of each building footprint.
#    We will use the centroid of the footprint as a proxy location
#    for allocating the building's unitsres to an edge.
#    Perhaps a better method would allocate buildings to edges
#    based on the location of their front door.
#    This refinement can be made at a later time.
building_footprints_gdf['centroids'] = building_footprints_gdf['geometry'].centroid
building_footprints_gdf['centroids'] = building_footprints_gdf['centroids'].to_crs('EPSG:4326')


# 4. Get Manhattan MapPluto data into a DataFrame.
manhattan_mpluto_response = requests.get("https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=Borough%20%3D%20%27MN%27&outFields=Block,Lot,CD,ZipCode,FireComp,PolicePrct,SanitSub,Address,OwnerName,NumBldgs,UnitsRes,LotFront,BldgFront,BBL,CT2010,CB2010,SchoolDist,Council,Sanitboro,SanitDistrict,OwnerType,BoroCode,Borough&outSR=4326&f=json")
manhattan_mpluto_data = manhattan_mpluto_response.json()

manhattan_mpluto_df = pd.DataFrame(manhattan_mpluto_data['features'])
manhattan_mpluto_df = pd.DataFrame(list(manhattan_mpluto_df['attributes']))
manhattan_mpluto_df.columns = ['Block', 'Lot', 'CD', 'ZipCode', 'FireComp', 'PolicePrct', 'SanitSub',
       'Address', 'OwnerName', 'MplutoNumBldgs', 'MplutoUnitsRes', 'LotFront', 'BldgFront', 'mpluto_bbl',
       'CT2010', 'CB2010', 'SchoolDist', 'Council', 'Sanitboro',
       'SanitDistrict', 'OwnerType', 'BoroCode', 'Borough']

print(manhattan_mpluto_df['MplutoUnitsRes'].sum())
print(manhattan_mpluto_df.columns)
# 5. Join MapPluto data with building footprint data.
#    Note: consider using MapPluto data for footprints too...
building_footprints_gdf['mpluto_bbl'] = building_footprints_gdf['mpluto_bbl'].astype(int)
manhattan_mpluto_df['mpluto_bbl'] = manhattan_mpluto_df['mpluto_bbl'].astype(int)
building_footprints_gdf = building_footprints_gdf.merge(manhattan_mpluto_df, on='mpluto_bbl')
building_footprints_gdf = building_footprints_gdf[building_footprints_gdf['ZipCode'] != 10044.0] # strip out Roosevelt Island buildings
building_footprints_gdf['AdjUnitsRes'] = building_footprints_gdf['MplutoUnitsRes'].fillna(0) / building_footprints_gdf['MplutoNumBldgs'].replace(0,1).fillna(1)
building_footprints_gdf['AdjUnitsRes'] = building_footprints_gdf['AdjUnitsRes'].round().astype(int)

print(building_footprints_gdf.sort_values('AdjUnitsRes'))
print(building_footprints_gdf[building_footprints_gdf['Address'] == '240 1 AVENUE'])
print(building_footprints_gdf['AdjUnitsRes'].sum())


# 6. Allocate buildings to their nearest edges,
#    based on closest proximity of a building's centroid
#    to surrounding edges, measured in euclidean distance.
building_edges = ox.get_nearest_edges(nyc_graph,
                                      [coor.x for coor in building_footprints_gdf['centroids']],
                                      [coor.y for coor in building_footprints_gdf['centroids']],
                                      method='balltree')
building_edges = [(item[0],item[1],item[2]) for item in building_edges]
building_footprints_gdf['allocated_edge'] = building_edges
print(building_footprints_gdf.sort_values('AdjUnitsRes'))
print(building_footprints_gdf[building_footprints_gdf['Address'] == '240 1 AVENUE'])
print(building_footprints_gdf['AdjUnitsRes'].sum())


# 7. calculate the number of residents per edge
edges_residents_df = building_footprints_gdf[['allocated_edge','AdjUnitsRes']].groupby(['allocated_edge']).sum()
edges_residents_df.sort_values(by='AdjUnitsRes', inplace=True)
print(edges_residents_df)

# 8. add residents as an attribute to edges in nyc_graph
nyc_nodes_gdf, nyc_edges_gdf = ox.graph_to_gdfs(nyc_graph)

nyc_edges_gdf['allocated_edge'] = nyc_edges_gdf.index
nyc_edges_gdf = nyc_edges_gdf.merge(edges_residents_df, on='allocated_edge', how='left')
nyc_edges_gdf['AdjUnitsRes'] = nyc_edges_gdf['AdjUnitsRes'].fillna(0).astype(np.uint8)
print(nyc_edges_gdf)


# 8.5 re-compose graph from GDFs
nyc_edges_gdf['u'] = nyc_edges_gdf['allocated_edge'].apply(lambda x: x[0])
nyc_edges_gdf['v'] = nyc_edges_gdf['allocated_edge'].apply(lambda x: x[1])
nyc_edges_gdf['key'] = nyc_edges_gdf['allocated_edge'].apply(lambda x: x[2])
nyc_edges_gdf = nyc_edges_gdf[['u', 'v', 'key', 'osmid', 'name', 'highway',
                               'oneway', 'length', 'geometry', 'allocated_edge', 'AdjUnitsRes']]
nyc_edges_gdf = nyc_edges_gdf.set_index(['u', 'v', 'key'])
assert nyc_nodes_gdf.index.is_unique and nyc_edges_gdf.index.is_unique
graph_attrs = {'crs': 'epsg:4326', 'simplified': False}
nyc_graph = ox.graph_from_gdfs(nyc_nodes_gdf, nyc_edges_gdf, graph_attrs)

# 9. Save graph to GraphML file.
ox.save_graphml(nyc_graph, 'nyc_graph_2_allocateUnitsToEdges.graphml')

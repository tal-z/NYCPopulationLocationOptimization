import os
from datetime import datetime
import requests

from sodapy import Socrata
import pandas as pd
import geopandas as gpd
import osmnx as ox
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rc('xtick', labelsize=8)
mpl.rc('ytick', labelsize=8)


nyc_graph = ox.load_graphml('graphFiles/graphml/mn_step2_sumEdgeUnitsPerNode_20210418.graphml')

nyc_gdf = gpd.read_file(gpd.datasets.get_path('nybb')).to_crs("EPSG:4326")
manhattan_gdf = nyc_gdf[nyc_gdf['BoroCode']==1]

client = Socrata("data.cityofnewyork.us",
                 'odQdEcIxnATZPym3KySwgWw27',
                 username=os.getenv('username'),
                 password=os.getenv('password'))
results = client.get("4txx-zupp",
                     content_type='geojson',
                     where=f"mpluto_bbl like '1%'", # is in Manhattan
                     limit=1100000)
building_footprints_gdf = gpd.GeoDataFrame.from_features(results).set_crs(epsg=4326, inplace=True)

manhattan_mpluto_response = requests.get("https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=Borough%20%3D%20%27MN%27&outFields=Block,Lot,CD,ZipCode,FireComp,PolicePrct,SanitSub,Address,OwnerName,UnitsRes,LotFront,BldgFront,BBL,CT2010,CB2010,SchoolDist,Council,Sanitboro,SanitDistrict,OwnerType,BoroCode,Borough&outSR=4326&f=json")
manhattan_mpluto_data = manhattan_mpluto_response.json()
manhattan_mpluto_df = pd.DataFrame(manhattan_mpluto_data['features'])
manhattan_mpluto_df = pd.DataFrame(list(manhattan_mpluto_df['attributes']))
manhattan_mpluto_df.columns = ['Block', 'Lot', 'CD', 'ZipCode', 'FireComp', 'PolicePrct', 'SanitSub',
       'Address', 'OwnerName', 'UnitsRes', 'LotFront', 'BldgFront', 'mpluto_bbl',
       'CT2010', 'CB2010', 'SchoolDist', 'Council', 'Sanitboro',
       'SanitDistrict', 'OwnerType', 'BoroCode', 'Borough']

# 5. Join MapPluto data with building footprint data.
#    Note: consider using MapPluto data for footprints too...
building_footprints_gdf['mpluto_bbl'] = building_footprints_gdf['mpluto_bbl'].astype(int)
manhattan_mpluto_df['mpluto_bbl'] = manhattan_mpluto_df['mpluto_bbl'].astype(int)
building_footprints_gdf = building_footprints_gdf.merge(manhattan_mpluto_df, on='mpluto_bbl')
building_footprints_gdf = building_footprints_gdf[building_footprints_gdf['ZipCode'] != 10044.0] # strip out Roosevelt Island buildings



gdf_nodes = ox.graph_to_gdfs(nyc_graph, edges=False)
gdf_nodes['UnitsWithinHalfMile'] = gdf_nodes['UnitsWithinHalfMile'].astype(float)
gdf_nodes['UnitsWithinHalfMile'] = gdf_nodes['UnitsWithinHalfMile'] * (100/gdf_nodes['UnitsWithinHalfMile'].max())


fig, ax = plt.subplots(figsize=(8,8),dpi=1200)
base = manhattan_gdf.plot(ax=ax, color='lightgray', edgecolor='gray')
building_footprints_gdf.plot(ax=base, zorder=5)
nodes = ax.scatter(x=gdf_nodes['x'], y=gdf_nodes['y'], color='green', s=.1, edgecolors='none', zorder=10)
plt.savefig(f'MnBldgFootPrintsAndNodes_{datetime.now()}.pdf', bbox_inches="tight")



import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
ox.config(log_console=True, use_cache=True)
from bs4 import BeautifulSoup
import requests

# We want to display a map of the streets in NYC
"""
nyc_graph = ox.graph_from_place('NYC')
nyc_graph = nx.to_undirected(nyc_graph)
ox.save_graphml(nyc_graph, "graphFiles/nyc_graph_1.graphml")

"""



"""ENTER BEAUTIFULSOUP"""

base_url = "https://www.gutenberg.org/browse/authors/"
#alphabet = "abcdefghijklmnopqrstuvwxyz"
alphabet = [chr(i + 97) for i in range(26)]
author_names = {}
sess = requests.session()
for char in alphabet:
    response = sess.get(f"{base_url}/{char}")
    soup = BeautifulSoup(response.text, "html")
    for tag in soup.findAll("h2"):
        text = ""
        for child in tag.children:
            text = child.text.split(",")
            break

        if len(text) > 1:
            name = text[1].strip() + " " + text[0].strip()
        else:
            name = text[0]
        print(name)
        author_names[name] = 1

print(author_names)

nyc_graph = ox.load_graphml("graphFiles/nyc_graph_1.graphml")
fig, ax = ox.plot_graph(nyc_graph,
                        bgcolor='k',
                        edge_linewidth=3,
                        node_size=0,
                        show=False,
                        close=False)
print("Doing the loop!!!!")

for _, edge in ox.graph_to_gsdf(nyc_graph, nodes=False).fillna('').iterrows():
    c = edge['geometry'].centroid
    text = str(edge['name'])
    if text in author_names:
        print(text)
        ax.annotate(text, (c.x, c.y), c='w')

plt.show()



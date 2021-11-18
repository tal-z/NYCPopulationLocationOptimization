import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
ox.config(log_console=True, use_cache=True)
from bs4 import BeautifulSoup
import requests


"""ENTER BEAUTIFULSOUP"""

base_url = "https://www.gutenberg.org/browse/authors/"
#alphabet = "abcdefghijklmnopqrstuvwxyz"
alphabet = [chr(i + 97) for i in range(26)]
author_names = []
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
        author_names.appen(name)
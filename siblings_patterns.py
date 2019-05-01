import numpy as np
import pandas as pd
import os
import networkx as nx
from difflib import SequenceMatcher

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

def get_cluster_qn_count(cluster_data, node_data, num_clusters=200):
	qn_count_map = {}
	for cluster in range(num_clusters):
		nodes = list(cluster_data[cluster_data.clusters_200 == cluster]['nodes'])
		cl_data = node_data[nodes].T
		cl_data = cl_data.loc[:, (cl_data != 0).any(axis=0)]
		qn_count_map[cluster] = (cl_data.sum(axis=1)/cl_data.shape[1]).sum()/cl_data.shape[0]
	return qn_count_map

def remove_subsets(arr):
	arr2 = arr[:]
	for m in arr:
		for n in arr:
			if set(m).issubset(set(n)) and m != n:
				arr2.remove(m)
				break
	return arr2


def get_siblings(master_graph, cluster_data, cluster_index, threshold = 0.7):
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster_index]['nodes'])
	master_siblings = []
	for i in range(len(nodes)):
		node1_neigbours = set(master_graph.neighbors(nodes[i])).intersection(nodes)
		node1_neig_len = len(node1_neigbours)
		node1_siblings = []
		for j in range(i+1, len(nodes)):
			node2_neigbours = set(master_graph.neighbors(nodes[j])).intersection(nodes)
			node2_neig_len = len(node2_neigbours)

			if nodes[i] in node2_neigbours:
				continue
			else:
				if node2_neig_len > 0 and node1_neig_len > 0:
					if node2_neig_len > node1_neig_len:
						if len(node2_neigbours.intersection(node1_neigbours))/ float(node2_neig_len) >= threshold:
							node1_siblings.append(nodes[j])
					else:
						if len(node2_neigbours.intersection(node1_neigbours))/ float(node1_neig_len) >= threshold:
							node1_siblings.append(nodes[j])
		if node1_siblings:
			node1_siblings.append(nodes[i])
			master_siblings.append(node1_siblings)
	return remove_subsets(master_siblings)



def get_rename_nodes(master_graph, cluster_data, cluster_index, threshold = 0.6):
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster_index]['nodes'])
	master_siblings = []
	for i in range(len(nodes)):
		node1_neigbours = set(master_graph.neighbors(nodes[i])).intersection(nodes)
		node1_neig_len = len(node1_neigbours)
		node1_siblings = []
		for j in range(i+1, len(nodes)):
			node2_neigbours = set(master_graph.neighbors(nodes[j])).intersection(nodes)
			node2_neig_len = len(node2_neigbours)

			if nodes[i] in node2_neigbours:
				continue
			else:
				if node2_neig_len > 0 and node1_neig_len > 0:
					sim_ratio = similar(nodes[i], nodes[j])
					if node2_neig_len > node1_neig_len:
						if (len(node2_neigbours.intersection(node1_neigbours))/ float(node2_neig_len)) * sim_ratio >= threshold:
							node1_siblings.append(nodes[j])
					else:
						if (len(node2_neigbours.intersection(node1_neigbours))/ float(node1_neig_len)) * sim_ratio >= threshold:
							node1_siblings.append(nodes[j])
		if node1_siblings:
			node1_siblings.append(nodes[i])
			master_siblings.append(node1_siblings)
	return remove_subsets(master_siblings)


cluster_data = pd.read_csv('/home/hduser/iit_data/node_clusters/master_clusters_200.csv')
node_data = pd.read_csv('/home/hduser/iit_data/node_clusters/node_data_wo_index.csv')

# read master graph for neighbour lookup
G = nx.read_weighted_edgelist('/home/hduser/iit_data/node_clusters/master_graph.txt')

# ignore the clusters which have very less number of questions
small_cluster_threshold = 1
cluster_qn_count_map = get_cluster_qn_count(cluster_data, node_data)
clusters_subset = [k for k, v in cluster_qn_count_map.items() if v > small_cluster_threshold]

count = 0
for cluster in clusters_subset:
	print('######################################################')
	print('Cluster : {}'.format(cluster))
	siblings = get_siblings(G, cluster_data, cluster)
	if siblings:
		print(siblings)
		count = count + len(siblings)
	print('######################################################')

print(count)
for cluster in clusters_subset:
	print('######################################################')
	print('Cluster : {}'.format(cluster))
	siblings = get_rename_nodes(G, cluster_data, cluster)
	if siblings:
		print(siblings)
	print('######################################################')




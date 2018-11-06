import numpy as np
import pandas as pd
from sklearn.externals import joblib
from os.path import join
from os import listdir


master_chains = []
years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
#years = [2010, 2011]

def add(pair):
	found_indices = []
	for index, graph in enumerate(master_chains):
		for key in graph.keys():
			if key in list(pair.items())[0][1]:
				found_indices.append(index)

	if not found_indices:
		master_chains.append(pair)
	else:
		merge_chains(found_indices, pair)


def merge_chains(indices, pair):
	graphs = []
	for index in indices:
		graphs.append(master_chains[index])

	new_master = master_chains.copy()
	for index in indices:
		master_chains.remove(new_master[index])

	graphs.append(pair)
	new_graph = {}
	for graph in graphs:
		for k, v in graph.items():
			new_graph[k] = v
	master_chains.append(new_graph)

def merge_pairs(file):
	# only merge case is handled
	merge_map = {}
	with open(file , 'r') as fp:
		for pair_str in fp.readlines():
			pair = [x.strip() for x in pair_str.split(',')]
			if pair[1] in merge_map:
				merge_map[pair[1]].append(pair[0])
			else:
				merge_map[pair[1]] = [pair[0]]

	return [{key: merge_map[key]} for key in merge_map.keys()] 


def create_temporal_chains(root_folder):
	for year in years :
		filename = 'WL-{0}-{1}-best-match.txt'.format(year, year+1)
		merged_pairs = merge_pairs(join(root_folder, filename))
		if master_chains:
			for pair in merged_pairs:
				add(pair)
		else:
			[master_chains.append(pair) for pair in merged_pairs]

def create_vis_data(graph):
	node_count = 0
	node_map = {}
	nodes = []
	edges = []
	for key, value in graph.items():
		if key not in node_map:
			node_count = node_count + 1
			node_map[key]	= node_count
			nodes.append({'id' : node_map[key], 'label' : key, 'shape' : 'ellipse'})

		for x in value:
			if x not in node_map:
				node_count = node_count + 1
				node_map[x]	= node_count
				nodes.append({'id' : node_map[x], 'label' : x, 'shape' : 'ellipse'})
			edges.append({'from' : node_map[x], 'to' : node_map[key], 'arrows': 'to', 'width' : 3, 'length' :200})

	return (nodes, edges)
				

if __name__ == '__main__':
	root_folder = '/home/hduser/iit_data/ask_ubuntu/models/graph_similarity_matrices'
	create_temporal_chains(root_folder)
	print('##############################################')
	for chain in master_chains:
		print('**********************************')
		nodes ,edges = create_vis_data(chain)
		print('nodes : {0}'.format(nodes))
		print('edges : {0}'.format(edges))

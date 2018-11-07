# https://github.com/almende/vis
import numpy as np
import os
from os import listdir


master_chains = []
years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
community_data_folder = '/home/vparambath/workpad/iith/year_wise_communities'
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
		merged_pairs = merge_pairs(os.path.join(root_folder, filename))
		if master_chains:
			for pair in merged_pairs:
				add(pair)
		else:
			[master_chains.append(pair) for pair in merged_pairs]

def get_tags(community_name):
	year = community_name.split('_')[0]
	community = community_name.split('_')[1]
	file_path = '{0}/{1}/community_tags/{2}_tags.txt'.format(community_data_folder, year, community)
	with open(file_path, 'r') as fp:
		tags = fp.read()
	return tags.replace('\n', '<br>')


def apply_vis_js_template(nodes, edges):
	return "var nodes = [{0}];\nvar edges = [{1}];".format(','.join(nodes), ','.join(edges))
	
def create_vis_data(graph):
	node_count = 0
	node_map = {}
	nodes = []
	edges = []
	for key, value in graph.items():
		if key not in node_map:
			node_count = node_count + 1
			node_map[key] = node_count
			nodes.append("{{id : {0},  label: '{1}', title : '{2}', shape : 'ellipse'}}".format(node_map[key], key, get_tags(key)))

		for x in value:
			if x not in node_map:
				node_count = node_count + 1
				node_map[x]	= node_count
				nodes.append("{{id : {0}, label : '{1}', title : '{2}', shape : 'ellipse'}}".format(node_map[x], x, get_tags(x)))
			edges.append("{{from : {0}, to : {1}, arrows: 'to', width : 3, length :200}}".format(node_map[x], node_map[key]))

	return apply_vis_js_template(nodes, edges)
				

if __name__ == '__main__':
	root_folder = '/home/vparambath/workpad/iith/models/graph_similarity_matrices'
	vis_folder = '/home/vparambath/workpad/iith/models/visualization'
	vis_template = 'vis_template.html'

	create_temporal_chains(root_folder)

	with open(vis_template, 'r') as fp:
		template_data = fp.read()

	counter = 0
	for chain in master_chains:
		vis_data = create_vis_data(chain)
		file_name = '{0}_chain.html'.format(counter)
		with open(os.path.join(vis_folder, file_name), 'w') as fp:
			fp.write(template_data.format(file_name.split('.')[0], vis_data))
		counter += 1
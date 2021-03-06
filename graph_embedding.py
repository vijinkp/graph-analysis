import networkx as nx
import numpy as np
from node2vec import Node2Vec
import pandas as pd
import os


def get_networkx_graph(graph_path, nodetype=str):
	return nx.read_edgelist(graph_path, nodetype=nodetype, data=(('weight',float),), create_using=nx.DiGraph())

def get_graph_embedding_model(graph, dimensions=64, walk_length=30, num_walks=200, workers=1, window=10, min_count=1, batch_words=4):
	if graph is not None:
		node2vec = Node2Vec(graph, dimensions=dimensions, walk_length=walk_length, num_walks=num_walks, workers=workers)
		model = node2vec.fit(window=window, min_count=min_count, batch_words=batch_words)
		return model

def get_node_similarity_matrix(model):
	return np.array([model.wv.similarity(node,node1) for node in model.wv.index2word for node1 in model.wv.index2word]).reshape(len(model.wv.index2word), -1)

def get_valid_nodes(model, nodes):
	return set(model.wv.index2word).intersection(nodes)


def get_yearwise_node_similarity_matrix(model, year1_nodes, year2_nodes):
	data = []
	for y1_node in year1_nodes:
		arr = []
		for y2_node in year2_nodes:
			arr.append(model.wv.similarity(y1_node, y2_node))
		data.append(arr)
	return np.array(data)

def add_graphs(file_paths, out_path):
	graph_lookup = {}
	graph_labels = {}
	for year, file in file_paths.items():
		labels = set()
		with open(file, 'r') as fp:
			lines = fp.readlines()
		for line in lines:
			line_arr = line.rsplit(' ', 1)
			labels.add(line.split(' ')[0])
			labels.add(line.split(' ')[1])
			if line_arr[0] in graph_lookup:
				graph_lookup[line_arr[0]] = graph_lookup[line_arr[0]] + float(line_arr[1])
			else:
				graph_lookup[line_arr[0]] = float(line_arr[1])
		graph_labels[year] = labels
	with open(out_path, 'w') as fp:
		for key, value in graph_lookup.items():
			fp.write('{0} {1}\n'.format(key, value))
	return graph_labels

if __name__ == '__main__':

	years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
	input_data_path = '/home/hduser/iit_data/ask_ubuntu_new/year_wise_named_graphs'
	output_path = '/home/hduser/iit_data/ask_ubuntu_new/node_resolution'
	high_thresholds = (0.8,1.0) 

	for t1, t2 in list(zip(years[0::1],years[1::1])):
		file_paths = {t1 : os.path.join(input_data_path, '{}.txt'.format(t1)), t2 : os.path.join(input_data_path, '{}.txt'.format(t2))}

		out_path = os.path.join(output_path, 'add_{0}_{1}.ncol'.format(t1,t2))
		result_path = os.path.join(output_path, 'node_sim_{0}_{1}.csv'.format(t1,t2))
		result_path1 = os.path.join(output_path, 'yr_node_sim_{0}_{1}.csv'.format(t1,t2))
		high_threshold_path = os.path.join(output_path, 'yr_node_ht_sim_{0}_{1}.csv'.format(t1,t2))
		
		sim_score_grps = list(zip(np.arange(0,1.1,0.1)[0::1], np.arange(0,1.1,0.1)[1::1]))

		graph_label_map = add_graphs(file_paths, out_path)
		graph = get_networkx_graph(out_path)
		model = get_graph_embedding_model(graph)
		nodes = model.wv.index2word

		# Only year1 nodes are compared aganist year2 nodes
		t1_nodes = get_valid_nodes(model,graph_label_map[t1])
		t2_nodes = get_valid_nodes(model,graph_label_map[t2])

		# nodes which are not present in t1
		t2_updated_nodes = list(t2_nodes.difference(t1_nodes))
		t1_nodes = list(t1_nodes)

		print('Number of nodes in t1 : {}'.format(len(t1_nodes)))
		print('Number of nodes in t2 : {}'.format(len(list(t2_nodes))))
		print('Number of new nodes in t2 : {}'.format(len(t2_updated_nodes)))

		node_yr_similarity_matrix = get_yearwise_node_similarity_matrix(model, t1_nodes, t2_updated_nodes)
		year_sim_data = []
		ht_yr_sim_data = []
		for i in range(node_yr_similarity_matrix.shape[0]):
			node_data = []
			node = t1_nodes[i]
			node_sim_arr = node_yr_similarity_matrix[i]
			node_data.append(node)
			# High thresholds to another file
			ht_str = ':'.join(list(np.array(t2_updated_nodes)[list(np.where((node_sim_arr >= high_thresholds[0]) & (node_sim_arr < high_thresholds[1]))[0])]))
			if ht_str != '' :
				ht_yr_sim_data.append([node, ht_str])

			for lb, ub in sim_score_grps:
				sim_node_str = ':'.join(list(np.array(t2_updated_nodes)[list(np.where((node_sim_arr >= lb) & (node_sim_arr < ub))[0])]))
				node_data.append(sim_node_str)
			year_sim_data.append(node_data)

		dataframe = pd.DataFrame(year_sim_data, columns=['nodes'] + [str(x) for x in sim_score_grps])
		dataframe.to_csv(result_path1, index=False)

		ht_df = pd.DataFrame(ht_yr_sim_data, columns=['nodes', 'similar_nodes'])
		ht_df.to_csv(high_threshold_path, index=False)

		# full nodes comparison
		node_similarity_matrix = get_node_similarity_matrix(model)
		data = []
		for i in range(node_similarity_matrix.shape[0]):
			node_data = []
			node = nodes[i]
			node_sim_arr = node_similarity_matrix[i]
			node_data.append(node)
			for lb, ub in sim_score_grps:
				sim_node_str = ':'.join(list(np.array(nodes)[list(np.where((node_sim_arr >= lb) & (node_sim_arr < ub))[0])]))
				node_data.append(sim_node_str)
			data.append(node_data)

		dataframe = pd.DataFrame(data, columns=['nodes'] + [str(x) for x in sim_score_grps])
		dataframe.to_csv(result_path, index=False)
import networkx as nx
import numpy as np
from node2vec import Node2Vec
import pandas as pd


def get_networkx_graph(graph_path, nodetype=str):
	return nx.read_edgelist(graph_path, nodetype=nodetype, data=(('weight',float),), create_using=nx.DiGraph())

def get_graph_embedding_model(graph, dimensions=64, walk_length=30, num_walks=200, workers=1, window=10, min_count=1, batch_words=4):
	if graph is not None:
		node2vec = Node2Vec(graph, dimensions=dimensions, walk_length=walk_length, num_walks=num_walks, workers=workers)
		model = node2vec.fit(window=window, min_count=min_count, batch_words=batch_words)
		return model

def get_node_similarity_matrix(model):
	return np.array([model.wv.similarity(node,node1) for node in model.wv.index2word for node1 in model.wv.index2word]).reshape(len(model.wv.index2word), -1)

def add_graphs(file_paths, out_path):
	graph_lookup = {}
	for file in file_paths:
		with open(file, 'r') as fp:
			lines = fp.readlines()
		for line in lines:
			line_arr = line.rsplit(' ', 1)
			if line_arr[0] in graph_lookup:
				graph_lookup[line_arr[0]] = graph_lookup[line_arr[0]] + float(line_arr[1])
			else:
				graph_lookup[line_arr[0]] = float(line_arr[1])
	with open(out_path, 'w') as fp:
		for key, value in graph_lookup.items():
			fp.write('{0} {1}\n'.format(key, value))

if __name__ == '__main__':

	file_paths = ['/home/hduser/iit_data/tmp/2010_0.ncol', '/home/hduser/iit_data/tmp/2011_0.ncol']
	out_path = '/home/hduser/iit_data/tmp/add.ncol'
	result_path = '/home/hduser/iit_data/tmp/results.csv'
	sim_score_grps = list(zip(np.arange(0,1.1,0.1)[0::1], np.arange(0,1.1,0.1)[1::1]))

	add_graphs(file_paths, out_path)
	graph = get_networkx_graph(out_path)
	model = get_graph_embedding_model(graph)
	nodes = model.wv.index2word
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








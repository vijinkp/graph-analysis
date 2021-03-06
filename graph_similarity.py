import numpy as np
import graphkernels.kernels as gk
from os import listdir
from igraph import *
from sklearn.externals import joblib
import os
import itertools

def get_igraph(file, master_map):
	graph = Graph.Read_Pajek(file)
	graph.vs['label'] = [master_map[name] for name in graph.vs['id']]
	graph.es['label'] = graph.es['weight']
	return graph

def get_graphs(year, folder_path, master_map):
	return ([get_igraph(os.path.join(folder_path,file), master_map) for file in listdir(folder_path) if '.net' in file] , ['{0}_{1}'.format(year, file.split('.')[0]) for file in listdir(folder_path) if '.net' in file])

def create_kernel_csv(kernel, row_labels, col_labels, file_path):
	str_kernel = np.char.mod('%d', kernel)
	csv_str = ',' + ','.join(col_labels)+ '\n'+ '\n'.join([row_labels[index]+ ',' + ','.join(x) for index, x in enumerate(str_kernel)])
	with open(file_path, 'w') as fp:
		fp.write(csv_str)


if __name__ == '__main__':
	root_folder = '/home/hduser/iit_data/ask_ubuntu_new/year_wise_communities'
	master_map_path = '/home/hduser/iit_data/ask_ubuntu_new/models/master_index.pkl'
	outpath = '/home/hduser/iit_data/ask_ubuntu_new/models/graph_similarity_matrices'

	os.makedirs(outpath)

	master_map = joblib.load(master_map_path)
	
	years = [int(yr) for yr in listdir(root_folder)] 
	years.sort()
	year_tup = list(zip(years[0:], years[1:]))

	for yr1, yr2 in year_tup:
		yr1_graphs , yr1_labels = get_graphs(yr1, os.path.join(root_folder, str(yr1), 'communities_pajek'), master_map)
		yr2_graphs , yr2_labels = get_graphs(yr2, os.path.join(root_folder, str(yr2), 'communities_pajek'), master_map)

		graph_list = []
		graph_list.extend(yr1_graphs)
		graph_list.extend(yr2_graphs)

		K_WL = gk.CalculateWLKernel(graph_list, par = 3)
		K_WL_subset = K_WL[:len(yr1_graphs), len(yr1_graphs):]
		joblib.dump(K_WL_subset, '{0}/WL-{1}-{2}.pkl'.format(outpath, yr1, yr2), compress = 1)
		create_kernel_csv(K_WL_subset, yr1_labels, yr2_labels, '{0}/WL-{1}-{2}.csv'.format(outpath, yr1, yr2))

		# multiplying penalising coeff to block small communities getting merged with very large communities. 
		row_len , col_len = K_WL_subset.shape
		yr1_graph_sizes = [g.vcount() for g in yr1_graphs]
		yr2_graph_sizes = [g.vcount() for g in yr2_graphs]

		#penalize_coeff = np.array([x/float(y) for x,y in list(itertools.product(yr1_graph_sizes,yr2_graph_sizes))]).reshape(row_len, col_len)
		# 1/abs(x-y)+1
		penalize_coeff = np.array([1/float((np.abs(x-y)+1)) for x,y in list(itertools.product(yr1_graph_sizes,yr2_graph_sizes))]).reshape(row_len, col_len)
		sim_matrix = np.multiply(K_WL_subset, penalize_coeff)

		# only merge and one to one matching is possible, split is not possible
		# split can be defined by setting a threshold which will help to identify if a community is matched with more than one on next time interval
		#best_match = np.argmax(K_WL_subset, axis=1)
		best_match = np.argmax(sim_matrix, axis=1)
		with open('{0}/WL-{1}-{2}-best-match.txt'.format(outpath, yr1, yr2), 'w')as fp:
			for index, x in enumerate(best_match):
				if sim_matrix[index][x] >= 0.25 and K_WL_subset[index][x] > 1:
					fp.write('{0}, {1}, {2}\n'.format(yr1_labels[index],yr2_labels[int(x)], sim_matrix[index][x]))
				# if K_WL_subset[index][x] > 1:
				# 	fp.write('{0}, {1}, {2}\n'.format(yr1_labels[index],yr2_labels[int(x)], K_WL_subset[index][x]))
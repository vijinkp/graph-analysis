import numpy as np
import graphkernels.kernels as gk
from os import listdir
from igraph import *
from sklearn.externals import joblib
import os

def get_igraph(file, master_map):
	graph = Graph.Read_Pajek(file)
	graph.vs['label'] = [master_map[name] for name in graph.vs['id']]
	graph.es['label'] = graph.es['weight']
	return graph

def get_graphs(year, folder_path, master_map):
	return ([get_igraph(os.path.join(folder_path,file), master_map) for file in listdir(folder_path) if '.net' in file] , ['{0}_{1}'.format(year, file.split('.')[0]) for file in listdir(folder_path) if '.net' in file])

def create_kernel_csv(kernel, row_labels, col_labels, file_path):
	str_kernel = np.char.mod('%d', kernel)
	csv_str = ',' + ','.join(col_labels)+ '\n'+ '\n'.join([row_label[index]+ ',' + ','.join(x) for index, x in enumerate(kernel)])
	with open(file_path, 'w') as fp:
		fp.write(csv_str)


if __name__ == '__main__':
	root_folder = '/home/hduser/iit_data/ask_ubuntu/year_wise_communities'
	master_map_path = '/home/hduser/iit_data/ask_ubuntu/models/master_index.pkl'
	outpath = '/home/hduser/iit_data/ask_ubuntu/models/graph_similarity_matrices'

	os.makedirs(outpath)

	master_map = joblib.load(master_map_path)
	
	years = [int(yr) for yr in listdir(root_folder)] 
	years.sort()
	year_tup = list(zip(years[0:], years[1:]))

	for yr1, yr2 in year_tup:
		print(yr1, yr2)
		yr1_graphs , yr1_labels = get_graphs(yr1, os.path.join(root_folder, str(yr1), 'communities_pajek'), master_map)
		yr2_graphs , yr2_labels = get_graphs(yr2, os.path.join(root_folder, str(yr2), 'communities_pajek'), master_map)

		graph_list = []
		graph_list.extend(yr1_graphs)
		graph_list.extend(yr2_graphs)

		K_WL = gk.CalculateWLKernel(graph_list, par = 3)
		K_WL_subset = K_WL[:len(yr1_graphs), len(yr1_graphs):]
		joblib.dump(K_WL_subset, '{0}/WL-{1}-{2}.pkl'.format(outpath, yr1, yr2), compress = 1)
		create_kernel_csv(K_WL_subset, yr1_labels, yr2_labels, '{0}/WL-{1}-{2}.csv'.format(outpath, yr1, yr2))

		# only merge and one to one matching is possible, split is not possible
		# split can be defined by setting a threshold which will help to identify if a community is matched with more than one on next time interval
		best_match = np.argmax(K_WL_subset, axis=1)
		print(len(yr1_graphs), len(yr2_graphs))
		print(best_match)
		with open('{0}/WL-{1}-{2}-best-match.txt'.format(outpath, yr1, yr2), 'w')as fp:
			for index, x in enumerate(best_match):
				fp.write('{0}, {1}\n'.format(yr1_labels[index],yr2_labels[int(x)]))
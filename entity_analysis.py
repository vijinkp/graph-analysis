import numpy as np
import pandas as pd
from scipy.spatial import distance_matrix
from sklearn.preprocessing import scale
from scipy.stats import linregress
from matplotlib import pyplot as plt
import os

def normalize(a):
	return np.interp(a, (a.min(), a.max()), (-1, +1))

def plot_diff(x, node, path):
	x_norm = normalize(x)
	x = list(range(1,x_norm.shape[0]+1))
	y = list(x_norm)
	plt.figure(figsize=(12,8))
	plt.plot(x,y)
	plt.title(node)
	plt.xlabel('monthly interval')
	plt.ylabel('norm question count')
	plt.tight_layout()
	plt.savefig(os.path.join(path, '{}.png'.format(node)))
	plt.clf()
	plt.close()

def plot_pair(x1, x2, path, node):
	x = list(range(1,x1.shape[0]+1))
	y1 = list(x1)
	y2 = list(x2)
	plt.figure(figsize=(12,8))
	plt.plot(x,y1)
	plt.plot(x,y2)
	plt.title(node)
	plt.xlabel('monthly interval')
	plt.ylabel('question count')
	plt.tight_layout()
	plt.savefig(os.path.join(path, '{}.png'.format(node)))
	plt.clf()
	plt.close()

def get_cluster_qn_count(cluster_data, node_data, num_clusters=200):
	qn_count_map = {}
	for cluster in range(num_clusters):
		nodes = list(cluster_data[cluster_data.clusters_200 == cluster]['nodes'])
		cl_data = node_data[nodes].T
		cl_data = cl_data.loc[:, (cl_data != 0).any(axis=0)]
		qn_count_map[cluster] = (cl_data.sum(axis=1)/cl_data.shape[1]).sum()/cl_data.shape[0]
	return qn_count_map

root_folder = '/home/hduser/iit_data/node_clusters/tmp'
cluster_data = pd.read_csv('/home/hduser/iit_data/node_clusters/master_clusters_200.csv')
node_data = pd.read_csv('/home/hduser/iit_data/node_clusters/node_data_wo_index.csv')

small_cluster_threshold = 1
cluster_qn_count_map = get_cluster_qn_count(cluster_data, node_data)
clusters_subset = [k for k, v in cluster_qn_count_map.items() if v > small_cluster_threshold]

def identify_entity_change(norm_array, threshold = 1.2):
	count = 0
	sign_shift_count = 0
	shift_len = norm_array.shape[0]

	if np.where(norm_array == 1)[0].shape[0] >= 1 and np.where(norm_array == -1)[0].shape[0] >= 1 :
		if np.where(norm_array == 1)[0][0]  < np.where(norm_array == -1)[0][0]:
			if np.where(norm_array[:np.where(norm_array == 1)[0][0]] < 0)[0].shape[0] == 0 and np.where(norm_array[np.where(norm_array == -1)[0][0]:] > 0.5)[0].shape[0] == 0:
				shift_len = np.where(norm_array == -1)[0][0] - np.where(norm_array == 1)[0][0]

	# for first, second in zip(norm_array, norm_array[1:]):
	# 	if (first - second) >= threshold:
	# 		count = count + 1

	if shift_len < 10:
		print(shift_len)
		return True
	else:
		return False


possible_entity_change = []
for cluster in clusters_subset:
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster]['nodes'])
	entity_cluster = node_data[nodes]
	#os.makedirs(os.path.join(root_folder, str(cluster)))
	#os.makedirs(os.path.join(root_folder, str(cluster), 'pair_plots'))
	#os.makedirs(os.path.join(root_folder, str(cluster), 'diff_plots'))
	analysis_data = {}
	for node1 in nodes:
		for node2 in nodes:
			if node1 != node2:
				analysis_data[node1 + '-' +node2] = entity_cluster[node1] - entity_cluster[node2]
				if max(entity_cluster[node1]) - min(entity_cluster[node1]) > 10 and max(entity_cluster[node2]) - min(entity_cluster[node2]) > 10:
					if identify_entity_change(normalize(entity_cluster[node1] - entity_cluster[node2])):
						possible_entity_change.append(node1 + '-' +node2)
						print('Cluster : {0}, pair : {1}'.format(cluster, node1 + '-' +node2))
				#plot_diff(entity_cluster[node1] - entity_cluster[node2], node1 + '-' +node2, os.path.join(root_folder, str(cluster), 'diff_plots'))
				#plot_pair(entity_cluster[node1], entity_cluster[node2], os.path.join(root_folder, str(cluster), 'pair_plots'), node1 + '-' +node2)
#print(possible_entity_change)
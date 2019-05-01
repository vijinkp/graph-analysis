import numpy as np
import pandas as pd
from scipy.spatial import distance_matrix
from sklearn.preprocessing import scale
from scipy.stats import linregress
from matplotlib import pyplot as plt
import os
import networkx as nx


def get_scaled_dist_matrix(cluster_data, node_data, cluster_index):
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster_index]['nodes'])
	cl_data = node_data[nodes].T
	cl_dist = pd.DataFrame(distance_matrix(cl_data.values, cl_data.values), index=cl_data.index, columns=cl_data.index)
	cl_dist_scale = pd.DataFrame(scale(cl_dist), index=cl_data.index, columns=cl_data.index)
	cl_dist_scale['dis_sum'] = cl_dist_scale.sum(axis=1)/cl_dist_scale.shape[0]
	return cl_dist_scale

def identify_max_nodes(cluster_data, node_data, cluster_index):
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster_index]['nodes'])
	cl_data = node_data[nodes].T
	cl_data = cl_data.loc[:, (cl_data != 0).any(axis=0)]
	max_count = cl_data.idxmax().value_counts().to_dict()
	max_count.update((x, y/cl_data.shape[1]) for x, y in max_count.items())
	return max_count

def get_parent_score(max_lookup, row):
	if row['nodes'].strip() in max_lookup:
		return max_lookup[row['nodes'].strip()] * row['dis_sum'] 
	else:
		return 0

def get_cluster_qn_count(cluster_data, node_data, num_clusters=200):
	qn_count_map = {}
	for cluster in range(num_clusters):
		nodes = list(cluster_data[cluster_data.clusters_200 == cluster]['nodes'])
		cl_data = node_data[nodes].T
		cl_data = cl_data.loc[:, (cl_data != 0).any(axis=0)]
		qn_count_map[cluster] = (cl_data.sum(axis=1)/cl_data.shape[1]).sum()/cl_data.shape[0]
	return qn_count_map

def check_parent_leader(cluster_data, master_graph, cluster_index, node_list, threshold = 0.9):
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster_index]['nodes'])
	output = {}
	for pos_node in node_list:
		edges = len(set(master_graph.neighbors(pos_node)).intersection(nodes))
		if edges / float(len(nodes)-1) > threshold:
			output[pos_node] = 'parent'
		else:
			output[pos_node] = 'leader'
	return output


def get_slope(row, path):
	x = list(range(1,row.shape[0]+1))
	y = list(row)
	node = row.name
	slope, intercept, r_value, p_value, std_err = linregress(x, y)
	
	y_first = y[:int(len(y)/2)]
	x_first = list(range(1, len(y_first)+1))
	slope_first, intercept_first, r_value_first, p_value, std_err = linregress(x_first, y_first)

	y_second = y[int(len(y)/2):]
	x_second = list(range(1, len(y_second)+1))
	slope_second, intercept_second, r_value_second, p_value, std_err = linregress(x_second, y_second)

	plot_slope(x, y, slope, intercept, r_value, path, node, slope_first, intercept_first, r_value_first, slope_second, intercept_second, r_value_second)
	return slope, intercept, r_value

def plot_slope(x, y, slope, intercept, r_value, path, node, slope_first, intercept_first, r_value_first, slope_second, intercept_second, r_value_second):
	plt.figure(figsize=(12,8))
	plt.plot(x,y)
	line_x = np.arange(min(x), max(x))
	line_y = slope*line_x + intercept
	plt.plot(line_x, line_y, label='Full :$%.2fx + %.2f$, $R^2=%.2f$' % (slope, intercept, r_value**2))

	line_y_first = slope_first*line_x + intercept_first
	plt.plot(line_x, line_y_first, label='First Half : $%.2fx + %.2f$, $R^2=%.2f$' % (slope_first, intercept_first, r_value_first**2))

	line_y_second = slope_second*line_x + intercept_second
	plt.plot(line_x, line_y_second, label='Second Half : $%.2fx + %.2f$, $R^2=%.2f$' % (slope_second, intercept_second, intercept_second**2))

	plt.legend(loc='best')
	plt.title(node)
	plt.xlabel('monthly interval')
	plt.ylabel('question count')
	plt.tight_layout()
	plt.savefig(os.path.join(path, '{}.png'.format(node)))
	plt.clf()
	plt.close()

def get_cluster_trends(cluster_data, node_slope_lookup, cluster_index, uptrends_threshold = 0.5, downtrends_threshold = -0.5):
	nodes = list(cluster_data[cluster_data.clusters_200 == cluster_index]['nodes'])
	up_trends = []
	down_trends = []
	for node in nodes:
		if node_slope_lookup[node] >= uptrends_threshold:
			up_trends.append(node)
		elif node_slope_lookup[node] <= downtrends_threshold:
			down_trends.append(node)
	return {'up' : up_trends, 'down' : down_trends}

# max_threshold = 10
# norm_dist_threshold = 0.5
parent_threshold = 0.5
cluster_data = pd.read_csv('/home/hduser/iit_data/node_clusters/master_clusters_200.csv')
node_data = pd.read_csv('/home/hduser/iit_data/node_clusters/node_data_wo_index.csv')

# read master graph for neighbour lookup
G = nx.read_weighted_edgelist('/home/hduser/iit_data/node_clusters/master_graph.txt')

# ignore the clusters which have very less number of questions
small_cluster_threshold = 1
cluster_qn_count_map = get_cluster_qn_count(cluster_data, node_data)
clusters_subset = [k for k, v in cluster_qn_count_map.items() if v > small_cluster_threshold]

# Identify possible parent/leaders in clusters
possible_parent_clusters = {}
for cluster in clusters_subset:
	data = get_scaled_dist_matrix(cluster_data, node_data, cluster)
	# normalised distance based method
	# high_dist_nodes = set(data[data.dis_sum > norm_dist_threshold].index)
	# max_count = identify_max_nodes(cluster_data, node_data, cluster)
	# max_nodes = set(max_count[max_count > max_threshold].index)
	# if high_dist_nodes and  max_nodes:
	# 	possible_parent_clusters[cluster] = max_nodes.intersection(high_dist_nodes)

	# normalised distance * normalized sum of max count
	subset = data[['dis_sum']].rename_axis('nodes').reset_index()
	max_count_map = identify_max_nodes(cluster_data, node_data, cluster)
	subset['parent_score'] = subset.apply(lambda row : get_parent_score(max_count_map, row), axis=1)
	parent_nodes = list(subset[subset.parent_score > parent_threshold].nodes)
	if parent_nodes:
		possible_parent_clusters[cluster] = parent_nodes

possible_parent_csv = []
for key in possible_parent_clusters.keys():
	possible_parent_csv.append(str(key) + '\t' + ','.join(possible_parent_clusters[key]))

with open('/home/hduser/iit_data/node_clusters/possible_parents.csv', 'w') as fp:
	fp.write('\n'.join(possible_parent_csv))

# Classify parent and leader
for cluster in possible_parent_clusters.keys():
	print(cluster, check_parent_leader(cluster_data, G, cluster, possible_parent_clusters[cluster]))


# Identify significant node trends within the clusters
# nd = node_data.T
# nd['slope'],  nd['intercept'], nd['R2'] = zip(*nd.apply(lambda row : get_slope(row, node_slope_folder), axis=1))
# nd = nd.rename_axis('node').reset_index()
# nd.to_csv('node_slope.csv', index=False)
# node_slope_lookup = nd[['node', 'slope']].set_index('node').to_dict()

# clusters_node_trends = {}
# for cluster in clusters_subset:
# 	clusters_node_trends[cluster] = get_cluster_trends(cluster_data, node_slope_lookup, cluster)
# print(clusters_node_trends)



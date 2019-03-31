import numpy as np 
import pandas as pd 
from matplotlib import pyplot as plt 
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


def create_plots(nodes, node_data, output_path):
	node_data[list(nodes)].plot(kind='area', stacked=False, figsize=(12,8))
	plt.savefig(output_path)

sns.set()
data = pd.read_csv('/home/hduser/iit_data/tmp/master_graph_embeddings.csv')
cols = list(data.columns)
cols.remove('nodes')

X = data[cols]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

k_arr = [25, 50, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1500]

max_score = -1
best_cluster = None 
score_map = {}
for k in k_arr:
	ward = AgglomerativeClustering(n_clusters=k, linkage='ward').fit(X_scaled)
	label = ward.labels_
	silhouette_avg = silhouette_score(X_scaled, label)
	score_map[k] = silhouette_avg

	if silhouette_avg > max_score:
		max_score = silhouette_avg
		best_cluster = k

print('Optimum number of clusters : {0} , silhouette_score : {1}'.format(best_cluster, max_score))

plt.plot(score_map.keys(), score_map.values())
plt.show()

# Optimum number of clusters : 800 , silhouette_score : 0.2826148696476016
ward = AgglomerativeClustering(n_clusters=800, linkage='ward').fit(X_scaled)
label = ward.labels_
data['clusters'] = label
data[['nodes','clusters']].to_csv('/home/hduser/iit_data/tmp/master_clusters.csv', index=False)

# adhoc code for plotting nodes' temporal trends
plot_root_folder = '/home/hduser/iit_data/tmp/clusters_200'
cluster_data = pd.read_csv('/home/hduser/iit_data/tmp/master_clusters_200.csv')
node_data = pd.read_csv('/home/hduser/iit_data/tmp/node_data_wo_index.csv')
no_clusters = 200
for x in range(200):
	create_plots(list(cluster_data[cluster_data.clusters_200 == x]['nodes']), node_data, os.path.join(plot_root_folder, '{}.png'.format(x))) 






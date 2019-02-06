# http://igraph.org/python/doc/igraph.clustering.VertexClustering-class.html
# http://igraph.org/python/doc/igraph.Graph-class.html#community_infomap

from igraph import *
from sklearn.externals import joblib
from os import listdir
import os

def create_communities(input_file, output_folder, master_map):
	if os.stat(input_file).st_size != 0:
		
		graph = Graph.Read_Pajek(input_file)

		# Create communities with infomap
		communities = graph.community_infomap()

		# Save community object
		joblib.dump(communities, os.path.join(output_folder, 'communities.pkl'), compress = 1)

		# Save cluster subgraphs
		for index, subgraph in enumerate(communities.subgraphs()):
			subgraph.write_pajek(os.path.join(output_folder, 'communities_pajek', '{0}.net'.format(index)))
			

			subgraph.vs['name'] = subgraph.vs['id']
			subgraph.write_ncol(os.path.join(output_folder, 'communities_ncol', '{0}.ncol'.format(index)))

			subgraph.vs['label'] = [master_map[name] for name in subgraph.vs['id']]
			subgraph.es['label'] = subgraph.es['weight']
			subgraph.write_graphml(os.path.join(output_folder, 'communities_graphml', '{0}.graphml'.format(index)))

			with open(os.path.join(output_folder, 'community_tags', '{0}_tags.txt'.format(index)), 'w') as fp:
				fp.write('\n'.join(subgraph.vs['id']))

if __name__ == '__main__':
	input_folder = '/home/hduser/iit_data/ask_ubuntu_new/year_wise_graphs_pajek'
	output_folder = '/home/hduser/iit_data/ask_ubuntu_new/year_wise_communities'
	master_map_path = '/home/hduser/iit_data/ask_ubuntu_new/models/master_index.pkl'
	master_map = joblib.load(master_map_path)

	for file in listdir(input_folder):
		print(file)
		file_name = file.split('.')[0]
		os.makedirs(os.path.join(output_folder, file_name))
		os.makedirs(os.path.join(output_folder, file_name, 'communities_ncol'))
		os.makedirs(os.path.join(output_folder, file_name, 'communities_pajek'))
		os.makedirs(os.path.join(output_folder, file_name, 'communities_graphml'))
		os.makedirs(os.path.join(output_folder, file_name, 'community_tags'))

		create_communities(os.path.join(input_folder, file), os.path.join(output_folder, file_name), master_map)






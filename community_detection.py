# http://igraph.org/python/doc/igraph.clustering.VertexClustering-class.html
# http://igraph.org/python/doc/igraph.Graph-class.html#community_infomap

from igraph import *
from sklearn.externals import joblib
from os import listdir
import os

def create_communities(input_file, output_folder):
	if os.stat(input_file).st_size != 0:
		
		# Read graph in pajek format
		graph = Graph.Read_Pajek(input_file)

		# Create communities with infomap
		communities = graph.community_infomap()

		# Save community object
		joblib.dump(communities, os.path.join(output_folder, 'communities.pkl'), compress = 1)

		# Save cluster subgraphs
		for index, subgraph in enumerate(communities.subgraphs()):
			subgraph.write_pajek(os.path.join(output_folder, 'communities', '{0}.net'.format(index)))
			with open(os.path.join(output_folder, 'community_tags', '{0}_tags.txt'.format(index)), 'w') as fp:
				fp.write('\n'.join(subgraph.vs['id']))

if __name__ == '__main__':
	input_folder = '/home/hduser/iit_data/ask_ubuntu/year_wise_graphs_pajek'
	output_folder = '/home/hduser/iit_data/ask_ubuntu/year_wise_communities'

	for file in listdir(input_folder):
		print(file)
		file_name = file.split('.')[0]
		os.makedirs(os.path.join(output_folder, file_name))
		os.makedirs(os.path.join(output_folder, file_name, 'communities'))
		os.makedirs(os.path.join(output_folder, file_name, 'community_tags'))

		create_communities(os.path.join(input_folder, file), os.path.join(output_folder, file_name))






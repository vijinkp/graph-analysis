from igraph import *
from os import listdir
from os.path import isfile, join
import os
from sklearn.externals import joblib

def convert_to_pajek(input_file, output_file):
	graph = Graph.Read_Ncol(input_file, directed=True, names=True)
	graph.vs['id'] = graph.vs['name']
	graph.write_pajek(output_file)


def convert_to_graphml(input_file, output_file, master_map):
	graph = Graph.Read_Ncol(input_file, directed=True, names=True)
	graph.vs['id'] = graph.vs['name']
	graph.vs['label'] = [master_map[name] for name in graph.vs['name']]
	graph.es['label'] = graph.es['weight']
	graph.write_graphml(output_file)


if __name__ == '__main__':
	input_path = '/home/hduser/iit_data/ask_ubuntu/year_wise_named_graphs'
	output_pajek_path = '/home/hduser/iit_data/ask_ubuntu/year_wise_graphs_pajek'
	output_graphml_path = '/home/hduser/iit_data/ask_ubuntu/year_wise_graphs_graphml'
	master_map_path = '/home/hduser/iit_data/ask_ubuntu/models/master_index.pkl'
	master_map = joblib.load(master_map_path)

	os.makedirs(output_pajek_path)
	os.makedirs(output_graphml_path)

	for file in listdir(input_path):
		file_name = file.split('.')[0]
		if os.stat(join(input_path, file)).st_size != 0:
			print(file_name)
			convert_to_pajek(join(input_path, file), join(output_pajek_path, '{0}.net'.format(file_name)))
			convert_to_graphml(join(input_path, file), join(output_graphml_path, '{0}.graphml'.format(file_name)), master_map)
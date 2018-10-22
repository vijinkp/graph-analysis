from igraph import *
from os import listdir
from os.path import isfile, join
import os

#def plot_graph(input_file, ):

def convert_to_pajek(input_file, output_file):
	graph = Graph.Read_Ncol(input_file, directed=True, names=True)
	graph.vs['id'] = graph.vs['name']
	graph.write_pajek(output_file)

if __name__ == '__main__':
	input_path = '/home/hduser/iit_data/ask_ubuntu/year_wise_named_graphs'
	output_path = '/home/hduser/iit_data/ask_ubuntu/year_wise_graphs_pajek'

	os.makedirs(output_path)

	for file in listdir(input_path):
		file_name = file.split('.')[0]
		if os.stat(join(input_path, file)).st_size != 0:
			print(file_name)
			convert_to_pajek(join(input_path, file), join(output_path, '{0}.net'.format(file_name)))
import os
from matplotlib import pyplot as plt 
import seaborn as sns
import pandas as pd 
import numpy as np
from graph_embedding import get_networkx_graph, get_graph_embedding_model

def tagcount(row):
    year_key = str(row['CreationYear']) + "{0:0=2d}".format(row['CreationMonth'])
    tags = row.CleanedTags.split(',')
    for tag in tags:
        if tag in tag_year_map:
            if year_key in tag_year_map[tag]:
                tag_year_map[tag][year_key] = tag_year_map[tag][year_key] + 1
            else:
                tag_year_map[tag][year_key] = 1
        else:
            tag_year_map[tag] = {year_key : 1}

def create_master_graph(input_folder, out_path):
	graph_lookup = {}
	for file in os.listdir(input_folder):
		with open(os.path.join(input_folder, file), 'r') as fp:
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

def create_plots(nodes, node_data, output_path):
	node_data[list(nodes)].plot(kind='area', stacked=False, figsize=(12,8))
	plt.savefig(output_path)

def create_node_clusters(input_folder, output_file, node_data, plot_folder = None):
	files = os.listdir(input_folder)
	files.sort()

	master_list = []
	for file in files:
		with open(os.path.join(input_folder, file), 'r', encoding="utf8", errors='ignore') as fp:
			lines = fp.readlines()

		for index,line in enumerate(lines):
			line = line.strip()
			# ignore header
			if index == 0:
				continue
			line_arr = []
			line_arr.append(line.split(',')[0])
			line_arr.extend(line.split(',')[1].split(':'))

			# Add first element to master_list
			if index == 1:
				master_list.append(set(line_arr))
			else:
				match_list = []
				for index, lst in enumerate(master_list):
					if len([item for item in line_arr if item in lst]) > 0:
						match_list.append(index)

				if len(match_list) > 0:
					# join all matched items to a single list
					join_set = set()
					for index in match_list:
						join_set = join_set.union(master_list[index])
					join_set = join_set.union(set(line_arr))

					# delete matched items
					for index in sorted(match_list, reverse=True):
						del master_list[index]

					# insert joined set back to master list for further processing
					master_list.append(join_set)

				else:
					master_list.append(set(line_arr))
	with open(output_file, 'w') as fp:
		count = 0
		for ls in master_list:
			create_plots(ls, node_data,os.path.join(plot_folder, '{}.png'.format(count)))
			fp.write(','.join(ls) + '\n')
			count += 1

if __name__ == '__main__':
	#sns.set_palette(sns.color_palette("gist_rainbow", n_colors=35))
	sns.set()

	root_folder = '/home/hduser/iit_data/node_clusters'
	yr_graph_data_path = '/home/hduser/iit_data/ask_ubuntu_new/year_wise_named_graphs'
	master_graph_path = os.path.join(root_folder, 'master_graph.txt')
	qn_data_path = '/home/hduser/iit_data/ask_ubuntu_new/question_posts.csv'
	input_folder = os.path.join(root_folder, 'yr_node_sim')
	output_file = os.path.join(root_folder, 'node_clusters.csv')
	plot_folder = os.path.join(root_folder, 'plots_style')

	# monthly count of questions tagged
	tag_year_map = {}
	qn_data = pd.read_csv(qn_data_path)
	x = qn_data.apply(tagcount, axis=1)
	data = pd.DataFrame.from_dict(tag_year_map)
	data.fillna(0, inplace=True)
	data.to_csv(os.path.join(root_folder, 'node_data_wo_index.csv'), index=False)
	data.to_csv(os.path.join(root_folder, 'node_data.csv'))

	# node_data = pd.read_csv(os.path.join(root_folder, 'node_data_wo_index.csv'))
	# create_node_clusters(input_folder, output_file, node_data, plot_folder)

	create_master_graph(yr_graph_data_path, master_graph_path)
	graph = get_networkx_graph(master_graph_path)
	model = get_graph_embedding_model(graph)
	model.save(os.path.join(root_folder, 'model_full_data.bin'))
	embedding_data = pd.DataFrame(model.wv.vectors)
	embedding_data['nodes'] = model.wv.index2word
	embedding_data.to_csv(os.path.join(root_folder, 'master_graph_embeddings.csv'), index=False)




	
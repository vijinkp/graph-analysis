import numpy as np
from orangecontrib.associate.fpgrowth import *  
from sklearn.externals import joblib
from os import listdir
from os.path import isfile, join
import os

master_index = {}

def create_graph(input_file, output_file, output_named_file, min_transactions = 2, confidence = 0.02 ):
	print('Creating graph for : {0}'.format(input_file))
	with open(input_file, 'r') as fp:
		lines = fp.read()

	items = [line.replace('\"' , '').split(',') for line in lines.split('\n')]
	for item in set([element for item in items for element in item]):
		if item not in master_index:
			if not master_index.values():
				master_index[item] = 1
			else:
				master_index[item] = max(master_index.values()) + 1

	int_items = [[master_index[x] for x in item] for item in items]

	itemsets = frequent_itemsets(int_items, min_transactions)
	itemsets = dict(itemsets)

	count_map = {list(key)[0]: value for key, value  in itemsets.items() if len(key) == 1}

	rules = list(association_rules(itemsets, confidence))
	pair_rules = [rule for rule in rules if len(list(rule[0])) == 1 and len(list(rule[1])) == 1]

	with open(output_file, 'w') as fp1:
		for rule in pair_rules:
			fp1.write('{0} {1} {2}\n'.format(list(rule[0])[0],list(rule[1])[0],rule[2]/float(count_map[list(rule[0])[0]])))

	master_index_rev = dict((v,k) for k,v in master_index.items())
	with open(output_named_file, 'w') as fp1:
		for rule in pair_rules:
			fp1.write('{0} {1} {2}\n'.format(master_index_rev[list(rule[0])[0]],master_index_rev[list(rule[1])[0]],rule[2]/float(count_map[list(rule[0])[0]])))

	print('Finished creating graph..')

if __name__ == '__main__':

	root_folder = '/home/hduser/iit_data/ask_ubuntu/'

	os.makedirs(os.path.join(root_folder, 'year_wise_graphs'))
	os.makedirs(os.path.join(root_folder, 'year_wise_named_graphs'))
	os.makedirs(os.path.join(root_folder, 'models'))

	input_folder = os.path.join(root_folder, 'year_wise')
	output_folder = os.path.join(root_folder, 'year_wise_graphs')
	output_name_folder = os.path.join(root_folder, 'year_wise_named_graphs')
	model_folder = os.path.join(root_folder, 'models')
	
	for file in listdir(input_folder):
		create_graph(join(input_folder, file), join(output_folder, file), join(output_name_folder, file))
	joblib.dump(master_index, join(model_folder, 'master_index.pkl'), compress=1)
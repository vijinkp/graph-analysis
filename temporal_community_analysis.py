from os import listdir
from os.path import isfile, join
import os
import operator

# https://www.hackerearth.com/blog/machine-learning/practical-guide-to-clustering-algorithms-evaluation-in-r/

# distance based measures
def rand_index(c1, c2):
	if c1 and c2 :
		return (len(c1|c2) + len(c1-c2 | c2-c1)) / float(len(c1-c2 | c2-c1) + len(c1|c2) + len(c1-c2) + len(c2-c1))
	else:
		return 0

def jaccard_index(c1, c2):
	if c1 and c2:
		return len(c1&c2)/ float(len(c1|c2))

def process_file(file_path):
	lines = None
	with open(file_path, 'r')as fp:
		lines = set([x.strip() for x in fp.readlines()])
	return lines

def best_match(stats):
	return max(stats.items(), key=operator.itemgetter(1))

if __name__ == '__main__':
	temporal_path1 = '/home/hduser/iit_data/ask_ubuntu/year_wise_communities/2010/community_tags'
	temporal_path2 = '/home/hduser/iit_data/ask_ubuntu/year_wise_communities/2011/community_tags'

	path1_files = listdir(temporal_path1)
	path2_files = listdir(temporal_path2)

	matching_dict = {}
	for file1 in path1_files:
		matching_dict[file1.split('_')[0]] = {file2.split('_')[0] : jaccard_index(process_file(join(temporal_path1, file1)), process_file(join(temporal_path2, file2))) for file2 in path2_files}

	for key in matching_dict.keys():
		print('{0} - {1} : {2}'.format(key, best_match(matching_dict[key])[0], best_match(matching_dict[key])[1]))

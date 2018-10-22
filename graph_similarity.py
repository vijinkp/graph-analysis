import numpy as np
import graphkernels.kernels as gk
from os import listdir
from os.path import join
from igraph import *

def get_graphs(year, folder_path):
	return ([Graph.Read_Pajek(join(folder_path,file)) for file in listdir(folder_path) if '.net' in file] , ['{0}_{1}'.format(year, file.split('.')[0]) for file in listdir(folder_path) if '.net' in file])

if __name__ == '__main__':
	root_folder = '/home/hduser/iit_data/ask_ubuntu/year_wise_communities'
	
	years = [int(yr) for yr in listdir(root_folder)] 
	years.sort()
	year_tup = list(zip(years[0:], years[1:]))

	for yr1, yr2 in year_tup:
		yr1_graphs , yr1_labels = get_graphs(yr1, join(root_folder, str(yr1), 'communities'))
		yr2_graphs , yr2_labels = get_graphs(yr2, join(root_folder, str(yr2), 'communities'))

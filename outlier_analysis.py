import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt


def plot_dist_data(data):
	plt.figure(figsize=(12,8))
	sns.distplot(data)
	plt.savefig('/home/hduser/iit_data/ask_ubuntu_mc/models/qn_count_slope.jpg')

def get_outlier_intervals(data, no_sds = 2, plot = True):
	chains = data.chain.unique()
	dist_data = []
	for chain in chains:
		chain_data = data[data.chain == chain].sort_values('year')
		qn_data = list(chain_data.no_questions)
		diff_data = [(x-qn_data[i-1])/float(qn_data[i-1] + 1) for i,x in enumerate(qn_data) ][1:]
		dist_data.extend(diff_data)

	if plot:
		plot_dist_data(dist_data)

	dist_data = np.array(dist_data)
	mean = np.mean(dist_data, axis=0)
	sd = np.std(dist_data, axis=0)
	return (mean - no_sds * sd, mean + no_sds * sd)


def identify_outlier_chains(data, interval):
	chains = data.chain.unique()
	outlier_chains = []
	for chain in chains:
		chain_data = data[data.chain == chain].sort_values('year')
		qn_data = list(chain_data.no_questions)
		diff_data = [(x-qn_data[i-1])/float(qn_data[i-1]+1) for i,x in enumerate(qn_data) ][1:]
		if len([x for x in diff_data if x < interval[0] or x > interval[1]]) > 0:
			outlier_chains.append(chain)
	return outlier_chains

if __name__ == '__main__':
	data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu_mc/models/temporal_data.csv')
	outlier_interval = get_outlier_intervals(data)
	print('Outlier : [{0}, {1}]'.format(outlier_interval[0], outlier_interval[1]))
	outlier_chains = identify_outlier_chains(data, outlier_interval)
	print(outlier_chains)

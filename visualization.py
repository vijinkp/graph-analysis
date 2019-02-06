from os import listdir
import os

def apply_vis_js_template(nodes, edges):
	return "var nodes = [{0}];\nvar edges = [{1}];".format(','.join(nodes), ','.join(edges))

def create_vis_data(pajek_data):
	vertex_data = False
	edge_data = False

	nodes = []
	edges = []
	for line in pajek_data.split('\n'):
		if '*Vertices' in line:
			vertex_data = True
			continue
		if '*Arcs' in line:
			edge_data = True
			vertex_data = False
			continue

		if vertex_data:
			if len(line.split(' ')) == 2:
				nodes.append("{{id : {0},  label: '{1}', title : '{2}', shape : 'circle'}}".format(line.split(' ')[0], 
					line.split(' ')[1].strip().replace('\"','')[:6], line.split(' ')[1].strip().replace('\"','')))

		if edge_data:
			if len(line.split(' ')) == 3:
				edges.append("{{from : {0}, to : {1}, arrows: 'to', width : 3, length :200, label: '{2}', font: {{align: 'top'}}}}"
					.format(line.split(' ')[0].strip(), 
					line.split(' ')[1].strip(), round(float(line.split(' ')[2].strip()),5)))

	return apply_vis_js_template(nodes, edges)


vis_template = 'community_template.html'
with open(vis_template, 'r') as fp:
	template_data = fp.read()

root_directory = '/home/hduser/iit_data/ask_ubuntu_new/year_wise_communities'
output_directory = '/home/hduser/iit_data/ask_ubuntu_new/community_vis'
os.makedirs(output_directory)

years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

for year in years:
	print('Processing year : {}'.format(year))
	output_path = os.path.join(output_directory, year)
	os.makedirs(output_path)
	
	folder_path = os.path.join(root_directory, year, 'communities_pajek')
	for file in listdir(folder_path):
		file_name = file.split('.')[0]
		with open(os.path.join(folder_path, file)) as fp:
			community_graph = fp.read()

		with open(os.path.join(output_path, file_name+'.html'), 'w') as fp:
			fp.write(template_data.format(file_name, create_vis_data(community_graph)))
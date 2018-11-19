import pandas as pd
import numpy as np
from os import listdir
import os
import xml.etree.ElementTree
import dateutil.parser

community_data_folder = '/home/hduser/iit_data/ask_ubuntu/models/temporal_chains'
community_tags_folder = '/home/hduser/iit_data/ask_ubuntu/year_wise_communities'

def process_post_data(input_file, date_cols):
	root = xml.etree.ElementTree.parse(input_file).getroot()
	post_list = []
	for post in root.getchildren():
		post_list.append(post.attrib)

	post_data = pd.DataFrame.from_dict(post_list)
	for col in post_data.columns:
		post_data[col] = post_data[col].apply(lambda x : str(x).replace('\n', '').strip())

	for col in date_cols:
		post_data[col] = post_data[col].apply(lambda x : dateutil.parser.parse(x))

	post_data.Id = post_data.Id.astype('float')
	post_data.AcceptedAnswerId = post_data.AcceptedAnswerId.astype('float')
	return post_data


def common_member(a, b): 
    a_set = set(a)
    b_set = set(b)
    if len(a_set.intersection(b_set)) > 0: 
        return(True)
    return(False)

def get_question_data(year, tag_id, data):
	file_path = os.path.join(community_tags_folder, year, 'community_tags', '{0}_tags.txt'.format(tag_id))
	tags = None
	with open(file_path , 'r') as fp:
		tags = fp.read().split('\n')

	year_data = data[data['creation_year'] == year]
	return year_data[year_data.tag_arr.apply(lambda x : common_member(x, tags))][['id','accepted_answer_id']] 






















if __name__ == '__main__':

	input_schema = ['id', 'post_type_id', 'accepted_answer_id', 'creation_date', 'score', 'view_count', 'body','owner_user_id','lasteditor_user_id',
	'lasteditor_display_name','lastedit_date','lastactivity_date' ,'title' ,'tags' ,'answer_count' ,'comment_count' ,'favorite_count' ,'community_owned_date' ]

	user_data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu/users.csv', sep='\u0001', engine='python')

	data =  process_post_data('/home/hduser/iit_data/ask_ubuntu/Posts.xml', ['CreationDate'])

	# Cleaned tag set and year
	data['creation_year'] = data.CreationDate.apply(lambda x : str(x.year))
	data['cleaned_tags'] = data.Tags.apply(lambda x : str(x).replace("><", ",").replace(">", "").replace("<", "").strip())

	# Quality questions
	# score = upvotes - downvotes
	qn_data = data[data.PostTypeId == '1']
	qn_data.Score = qn_data.Score.astype('float')
	quality_qn = qn_data[np.logical_and(qn_data.Score > 0, qn_data.AcceptedAnswerId != 0)]
	quality_qn['tag_arr'] = quality_qn.cleaned_tags.apply(lambda x : x.split(','))

	for file in listdir(community_data_folder):
		with open(os.path.join(community_data_folder, file), 'r') as fp:

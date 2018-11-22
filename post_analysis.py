import pandas as pd
import numpy as np
from os import listdir
import os
import xml.etree.ElementTree
import dateutil.parser
import warnings

warnings.filterwarnings('ignore')

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

def get_tags(year, community_ids):
	tag_list = []
	for community_id in community_ids:
		file_path = os.path.join(community_tags_folder, year, 'community_tags', '{0}_tags.txt'.format(community_id))
		tags = None
		with open(file_path , 'r') as fp:
			tag_list.extend(fp.read().split('\n'))
	return list(set(tag_list))


def get_question_data(year, tags, data):
	year_data = data[data['creation_year'] == year]
	return year_data[year_data.tag_arr.apply(lambda x : common_member(x, tags))][['Id','AcceptedAnswerId']] 

if __name__ == '__main__':

	# input_schema = ['AcceptedAnswerId', 'AnswerCount', 'Body', 'ClosedDate', 'CommentCount', 'CommunityOwnedDate', 'CreationDate', 'FavoriteCount', 'Id', 'LastActivityDate', 'LastEditDate', 'LastEditorDisplayName', 'LastEditorUserId', 'OwnerDisplayName', 'OwnerUserId', 'ParentId','PostTypeId', 'Score', 'Tags', 'Title', 'ViewCount']

 	global_sep = ','
 	user_data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu/users.csv', sep='\u0001', engine='python')
 	data =  process_post_data('/home/hduser/iit_data/ask_ubuntu/Posts.xml', ['CreationDate'])

 	# Cleaned tag set and year
 	data['creation_year'] = data.CreationDate.apply(lambda x : str(x.year))
 	data['cleaned_tags'] = data.Tags.apply(lambda x : str(x).replace("><", ",").replace(">", "").replace("<", "").strip())

 	# Quality questions
 	# score = upvotes - downvotes
 	qn_data = data[data.PostTypeId == '1']
 	qn_data.Score = qn_data.Score.astype('float')
 	quality_qn = qn_data[np.logical_and(qn_data.Score > 0, np.logical_not(qn_data.AcceptedAnswerId.isna()))]
 	quality_qn['tag_arr'] = quality_qn.cleaned_tags.apply(lambda x : x.split(','))

 	# answer data
 	answer_data = data[data.ParentId != 'nan']

 	temporal_data = []
 	for file in listdir(community_data_folder):
 		print('Processing chain : {0}'.format(file))
 		with open(os.path.join(community_data_folder, file), 'r') as fp:
 			lines = [(x.strip().split('_')[0],x.strip().split('_')[1])  for x in fp.readlines()]
 		
 		year_dict = dict()
 		[year_dict[t[0]].append(t[1]) if t[0] in list(year_dict.keys()) else year_dict.update({t[0]: [t[1]]}) for t in lines]

 		for year, community_ids in year_dict.items():
 			tags = get_tags(year, community_ids)

 			# get questions for corresponding tags
 			qn_ans_data = get_question_data(year, tags, quality_qn[quality_qn.creation_year == year])

 			# find users
 			join_data = qn_ans_data.join(answer_data.set_index('Id', inplace=False), on='AcceptedAnswerId', rsuffix='_ans', how='left')
 			unique_users = list(join_data.OwnerUserId.unique())
 			user_size = len(unique_users)
 			qn_size = qn_ans_data.shape[0]

 			# user based profiles
 			# Sum of reputation scores of users
 			reputation_score = user_data[user_data.Id.isin(unique_users)].Reputation.sum()

 			# Number of answers provided by users on that year
 			answer_year_data = answer_data[answer_data.creation_year == year]
 			user_answer_count = answer_year_data[answer_year_data.OwnerUserId.isin(unique_users)].shape[0]
 			temporal_data.append(global_sep.join([file, year, ':'.join(tags), str(user_size), str(qn_size), str(reputation_score), str(user_answer_count)]))
 	
 	schema = ['chain', 'year', 'tags', 'no_users', 'no_questions', 'sum_reputation', 'user_answer_count']
 	with open('/home/hduser/iit_data/ask_ubuntu/models/temporal_data.csv', 'w') as fp:
 		fp.write(','.join(schema) +'\n'+('\n'.join(temporal_data)))







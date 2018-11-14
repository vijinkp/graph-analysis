import pandas as pd
import numpy as np
from os import listdir

























if __name__ == '__main__':

	community_data_folder = '/home/hduser/iit_data/ask_ubuntu/models/temporal_chains'

	input_schema = ['id', 'post_type_id', 'accepted_answer_id', 'creation_date', 'score', 'view_count', 'body','owner_user_id','lasteditor_user_id',
	'lasteditor_display_name','lastedit_date','lastactivity_date' ,'title' ,'tags' ,'answer_count' ,'comment_count' ,'favorite_count' ,'community_owned_date' ]

	data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu/posts.csv', header=None, sep='\u0001', names=input_schema, 
		parse_dates=['creation_date', 'lastedit_date', 'lastactivity_date', 'community_owned_date'])

	# Cleaned tag set and year
	data['creation_year'] = data.creation_date.apply(lambda x : x[0:4])
	data['cleaned_tags'] = data.tags.apply(lambda x : str(x).replace("><", ",").replace(">", "").replace("<", "").strip())

	# Quality questions
	# score = upvotes - downvotes
	qn_data = data[data.post_type_id == 1]
	qn_data.score = qn_data.score.astype('float')
	quality_qn = qn_data[np.logical_and(qn_data.score > 0, qn_data.accepted_answer_id != 0)]




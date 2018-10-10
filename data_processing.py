import pandas as pd
import numpy as np
import os


input_schema = ['id', 'post_type_id', 'accepted_answer_id', 'creation_date', 'score', 'view_count', 'body','owner_user_id','lasteditor_user_id','lasteditor_display_name','lastedit_date','lastactivity_date' ,'title' ,'tags' ,'answer_count' ,'comment_count' ,'favorite_count' ,'community_owned_date' ]

data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu/posts.csv', header=None, sep='\u0001', names=input_schema, parse_dates=['creation_date', 'lastedit_date', 'lastactivity_date', 'community_owned_date'])

# Cleaned tag set and year
data['creation_year'] = data.creation_date.apply(lambda x : x[0:4])
data['cleaned_tags'] = data.tags.apply(lambda x : str(x).replace("><", ",").replace(">", "").replace("<", "").strip())

# Question posts
question_posts =  data[data.post_type_id == 1]
question_posts.to_csv('/home/hduser/iit_data/ask_ubuntu/question_posts.csv', index=False)	

os.makedirs('/home/hduser/iit_data/ask_ubuntu/year_wise')
[question_posts[question_posts.creation_year == year][['cleaned_tags']].to_csv('/home/hduser/iit_data/ask_ubuntu/year_wise/{0}.txt'.format(year), index=False, quotechar="\"", header=False) for year in question_posts.creation_year.unique()]

os.makedirs('/home/hduser/iit_data/ask_ubuntu/year_wise_question_data')
[question_posts[question_posts.creation_year == year].to_csv('/home/hduser/iit_data/ask_ubuntu/year_wise_question_data/{0}.csv'.format(year), index=False, sep='\u0001') for year in question_posts.creation_year.unique()]

os.makedirs('/home/hduser/iit_data/ask_ubuntu/year_wise_data')
[data[data.creation_year == year].to_csv('/home/hduser/iit_data/ask_ubuntu/year_wise_data/{0}.csv'.format(year), index=False, sep='\u0001') for year in question_posts.creation_year.unique()]
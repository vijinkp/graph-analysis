import pandas as pd
import numpy as np
import os


input_schema = ['id', 'post_type_id', 'accepted_answer_id', 'creation_date', 'score', 'view_count', 'body','owner_user_id','lasteditor_user_id','lasteditor_display_name','lastedit_date','lastactivity_date' ,'title' ,'tags' ,'answer_count' ,'comment_count' ,'favorite_count' ,'community_owned_date' ]

data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu/posts.csv', header=None, sep='\u0001', names=input_schema, parse_dates=['creation_date', 'lastedit_date', 'lastactivity_date', 'community_owned_date'])

# Question posts
question_posts =  data[data.post_type_id == 1]
question_posts['creation_year'] = question_posts.creation_date.apply(lambda x : x[0:4])

# Cleaned tag set and year
question_posts['cleaned_tags'] = question_posts.tags.apply(lambda x : x.replace("><", ",").replace(">", "").replace("<", "").strip())
question_posts.to_csv('/home/hduser/iit_data/ask_ubuntu/question_posts.csv', index=False)	

os.makedirs('/home/hduser/iit_data/ask_ubuntu/year_wise')

[question_posts[question_posts.creation_year == year][['cleaned_tags']].to_csv('/home/hduser/iit_data/ask_ubuntu/year_wise/{0}.txt'.format(year), index=False, quotechar="\"", header=False) for year in question_posts.creation_year.unique()]

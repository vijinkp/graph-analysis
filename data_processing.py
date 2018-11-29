import pandas as pd
import numpy as np
import os
from sklearn.externals import joblib

data = pd.read_csv('/home/hduser/iit_data/ask_ubuntu/posts-clean.csv', sep='\u0001')

# Cleaned tag set and year
data['CreationYear'] = data.CreationDate.str.slice(start=0,stop=4)
data['CleanedTags'] = data.Tags.apply(lambda x : str(x).replace("><", ",").replace(">", "").replace("<", "").strip())

# Master list of tags
# tag_set = set([z for y in [x.split(',') for x in data.cleaned_tags.tolist() if x != 'nan'] for z in y])
# master_map = {tag : index for index, tag in enumerate(tag_set)}
# joblib.dump(master_map, '/home/hduser/iit_data/ask_ubuntu/master_tag_map.pkl', compress=1)

# Question posts
question_posts =  data[data.PostTypeId == 1]
question_posts.to_csv('/home/hduser/iit_data/ask_ubuntu_mc/question_posts.csv', index=False)
joblib.dump(question_posts.groupby(by='CreationYear').count().Id.to_dict(), '/home/hduser/iit_data/ask_ubuntu_mc/year_qn_count.pkl', compress=1)	

os.makedirs('/home/hduser/iit_data/ask_ubuntu_mc/year_wise')
[question_posts[question_posts.CreationYear == year][['CleanedTags']].to_csv('/home/hduser/iit_data/ask_ubuntu_mc/year_wise/{0}.txt'.format(year), index=False, quotechar="\"", header=False) for year in question_posts.CreationYear.unique()]

os.makedirs('/home/hduser/iit_data/ask_ubuntu_mc/year_wise_question_data')
[question_posts[question_posts.CreationYear == year].to_csv('/home/hduser/iit_data/ask_ubuntu_mc/year_wise_question_data/{0}.csv'.format(year), index=False, sep='\u0001') for year in question_posts.CreationYear.unique()]

os.makedirs('/home/hduser/iit_data/ask_ubuntu_mc/year_wise_data')
[data[data.CreationYear == year].to_csv('/home/hduser/iit_data/ask_ubuntu_mc/year_wise_data/{0}.csv'.format(year), index=False, sep='\u0001') for year in question_posts.CreationYear.unique()]
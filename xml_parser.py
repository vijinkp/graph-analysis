import xml.etree.ElementTree
import pandas as pd
import dateutil.parser


def process_user_data(input_file, output_file):
	root = xml.etree.ElementTree.parse(input_file).getroot()
	user_list = []
	for user in root.getchildren():
		user_list.append(user.attrib)

	user_data = pd.DataFrame.from_dict(user_list)
	for col in user_data.columns:
		user_data[col] = user_data[col].apply(lambda x : str(x).replace('\n', '').strip())

	user_data.Id = user_data.Id.astype('float')
	user_data.Reputation = user_data.Reputation.astype('float')

	user_data.to_csv(output_file, sep='\u0001', index=False)


def process_post_data(input_file, output_file, date_cols):
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
	post_data.to_csv(output_file, sep='\u0001', index=False)


if __name__ == '__main__':
	# date_cols = ['CreationDate', 'LastEditDate', 'LastActivityDate', 'CommunityOwnedDate']
	# TO DO: Resolve error parsing on NAN values.
	date_cols = ['CreationDate']
	process_post_data('/home/hduser/iit_data/ask_ubuntu/Posts.xml', '/home/hduser/iit_data/ask_ubuntu/posts-clean.csv', date_cols)
	process_user_data('/home/hduser/iit_data/ask_ubuntu/Users.xml', '/home/hduser/iit_data/ask_ubuntu/users.csv')

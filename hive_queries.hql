create database askubuntu_raw;
create table posts (xmlstring string);
create table users (xmlstring string);

INSERT OVERWRITE LOCAL DIRECTORY '/home/hduser/iit_data/ask_ubuntu/posts'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\u0001'
STORED AS TEXTFILE
SELECT 
xpath_int(xmlstring,'//row/@Id') as id,
xpath_int(xmlstring,'//row/@PostTypeId') as post_type_id,
xpath_int(xmlstring,'//row/@AcceptedAnswerId') as accepted_answer_id,
from_unixtime(unix_timestamp(regexp_replace(xpath_string(xmlstring,'//row/@CreationDate'), 'T',' '))) as creation_date,
xpath_int(xmlstring,'//row/@Score') as score,
xpath_int(xmlstring,'//row/@ViewCount') as view_count,
regexp_replace(xpath_string(xmlstring,'//row/@Body'),"\n","") as body,
xpath_int(xmlstring,'//row/@OwnerUserId') as owner_user_id,
xpath_int(xmlstring,'//row/@LastEditorUserId') as lasteditor_user_id,
regexp_replace(xpath_string(xmlstring,'//row/@LastEditorDisplayName'),"\n","") as lasteditor_display_name,
from_unixtime(unix_timestamp(regexp_replace(xpath_string(xmlstring,'//row/@LastEditDate'), 'T',' '))) as lastedit_date,
from_unixtime(unix_timestamp(regexp_replace(xpath_string(xmlstring,'//row/@LastActivityDate'), 'T',' '))) as lastactivity_date,
regexp_replace(xpath_string(xmlstring,'//row/@Title'),"\n","") as title,
regexp_replace(xpath_string(xmlstring,'//row/@Tags'),"\n","") as tags,
xpath_int(xmlstring,'//row/@AnswerCount') as answer_count,
xpath_int(xmlstring,'//row/@CommentCount') as comment_count,
xpath_int(xmlstring,'//row/@FavoriteCount') as favorite_count,
from_unixtime(unix_timestamp(regexp_replace(xpath_string(xmlstring,'//row/@CommunityOwnedDate'), 'T',' '))) as community_owned_date
FROM posts
WHERE xmlstring NOT LIKE '%<?xml version=%' AND xmlstring  NOT LIKE '%posts>';


INSERT OVERWRITE LOCAL DIRECTORY '/home/hduser/iit_data/ask_ubuntu/users'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\u0001'
STORED AS TEXTFILE
SELECT 
xpath_int(xmlstring,'//row/@Id') as id,
xpath_int(xmlstring,'//row/@Reputation') as reputation,
from_unixtime(unix_timestamp(regexp_replace(xpath_string(xmlstring,'//row/@CreationDate'), 'T',' '))) as creation_date,
regexp_replace(xpath_string(xmlstring,'//row/@DisplayName'),"\n","") as display_name,
from_unixtime(unix_timestamp(regexp_replace(xpath_string(xmlstring,'//row/@LastAccessDate'), 'T',' '))) as lastaccess_date,
regexp_replace(xpath_string(xmlstring,'//row/@WebsiteUrl'),"\n","") as website_url,
regexp_replace(xpath_string(xmlstring,'//row/@Location'),"\n","") as location,
regexp_replace(xpath_string(xmlstring,'//row/@AboutMe'),"\n","") as about_me,
xpath_int(xmlstring,'//row/@Views') as views,
xpath_int(xmlstring,'//row/@UpVotes') as upvotes,
xpath_int(xmlstring,'//row/@DownVotes') as downvotes,
regexp_replace(xpath_string(xmlstring,'//row/@ProfileImageUrl'), "\n", "") as profile_image_url,
xpath_int(xmlstring,'//row/@AccountId') as account_id
FROM users
WHERE xmlstring NOT LIKE '%<?xml version=%' AND xmlstring  NOT LIKE '%users>';
from pymongo import MongoClient
import pandas as pd
import mysql.connector
import time

my_connect = mysql.connector.connect(
  host="localhost",
  user="db",
  passwd="newzer@",
  database="cms_major"
)

sample = pd.read_sql("select resource_id, html_body from `raw-articles` limit 3", my_connect)

rids = list(sample['resource_id'])
rids = [x.hex() for x in rids]
htmls = list(sample['html_body'])

client = MongoClient()
mydb = client['mydatabase']

data = mydb.data
# start = time.time()
# for i in range(len(rids)):
#     dump_stuff = {
#         '_id': rids[i],
#         'html_body': htmls[i]
#     }
#     data.insert_one(dump_stuff)
# print("Duration (s) for 1M inserts ==> ", time.time()-start)

start = time.time()
data.insert_many([{'_id': rids[i], 'html_body': htmls[i]} for i in range(len(rids))])
print("Duration (s) for 1M inserts ==> ", time.time()-start)

# data.find_one({'resource_id':'11eb3df24777cc3ea4052cf05d046cab'})['html_body']

'''
data.estimated_document_count()
'''

'''
ids = ['11eb3df24775b994b8e12cf05d046cab', '11eb3df24773d660afbb2cf05d046cab']
for x in data.find({"_id": {"$in": ids}}):
    print(x['html_body'])
'''

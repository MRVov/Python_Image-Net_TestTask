# -*- coding: utf-8 -*-

import requests
import pymongo
import os
from pymongo import MongoClient
import shutil

category_percent={
	"train": 20,
	"test": 80,
}

p_db=[
	{
		"name": "cat",
		"name_rus": "кошка",
		"id":"n02062017",
	},
	
	{
		"name": "dog",
		"name_rus": "собака",
		"id":"n02103406",
	},
	
]

storage_path="/opt/tmp/data/"

#Init DB
client = MongoClient()
db = client.test_database
collection = db.test_collection
posts = db.posts

for categ in p_db:
	url="http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=%s" % categ["id"]
	r = requests.get(url)
	
	#Parse and calc results
	image_url_arr=r.text.split("\n")
	len_image_url_arr=len(image_url_arr)
	print "Total items=%d for category ID=%s " % (len_image_url_arr, categ["id"])

	#Separate by percent
	for categ_per in category_percent:
		#Calc Qty for Category cercent
		categ_qty=int(category_percent[categ_per]/100.0*len_image_url_arr)
		
		i=0
		for curr in range(categ_qty):
			
			#Get element from array LIFO
			image_url=image_url_arr.pop()
			
			#Check URL
			if not image_url:
				i+=1
				continue
				
			#Calc paths
			download_storage=storage_path+categ_per+"/"+categ["name"]+"/"
			file_name=download_storage+image_url.split("/")[-1]
			file_name=file_name.replace("?", "")
			file_name=file_name.replace("=", "-")
			
			#Create dir if not exist
			if not os.path.exists(download_storage):
				os.makedirs(download_storage)
				
			# Download and save file
			try:
				r = requests.get(image_url, stream=True)
				cont_type=r.headers['content-type']
				if cont_type and cont_type.find("image/")!=0:
					print "Wrong content type for URL %s. Skip it!" % image_url
					i+=1
					continue
					
				if r.status_code == 200:
					with open(file_name, 'wb') as f:
						for chunk in r:
							f.write(chunk)

			except:
				print "Error Download URL %s" % image_url
				i+=1
				continue
				
			
			#Insert image in DB
			val = {"category": categ["name_rus"],
			       "path":file_name
			       }
			
			db_id = posts.insert_one(val).inserted_id

			i+=1
			
		print "Processed qty %d of %s, for category %s" % (i, len_image_url_arr, categ_per)
			
		




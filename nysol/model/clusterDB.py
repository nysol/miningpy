#!/usr/bin/env python
# coding: utf-8

# ## インターラクティブクラスタリング

from __future__ import print_function
import os
import sys
import json
from datetime import datetime
import random

from sampleDB import SampleDB

# 一つのクラスタクラス
class Cluster(object):
	def __init__(self,clusterID):
		self.id=clusterID
		self.title=""
		self.comment=""
		self.sampleDB=SampleDB()

	def title(self,length=10):
		print("xxxxxtitle")
		text="[%s](%d) %s"%(self.id,len(self.sampleDB),self.title[:length])
		return text

	def json_load(self,dat):
		self.id=dat["id"]
		self.title=dat["title"]
		self.comment=dat["comment"]
		self.sampleDB=SampleDB.json_load(dat["sampleDB"])

	def json_dump(self):
		dat={}
		dat["id"]=self.id
		dat["title"]=self.title
		dat["comment"]=self.comment
		dat["sampleDB"]=self.sampleDB.json_dump()
		return dat

	def show(self):
			print("-- cluster")
			print("id: %s"%(self.id))
			print("title: %s"%(self.title))
			print("comment:")
			print(self.comment)
			for smp in self.sampleDB.sampleList:
				print(smp.title(60))

####################################################################
class ClusterDB(object):
	def __init__(self):
		self.clusterList=[]
		self._i=0

	def __len__(self):
		return len(self.clusterList)

	def __iter__(self):
		return self

	def __next__(self):
		if self._i == len(self.clusterList)-1:
			raise StopIteration()
		self._i += 1
		return self.clusterList[self._i]

	def add(self,cluster):
		self.clusterList.append(cluster)

	def show(self):
		print("-- ClusterDB")
		for cluster in self.clusterList:
			cluster.show()
		self.clusterList.append(cluster)

if __name__=="__main__":
	import json
	import numpy as np
	from sklearn.cluster import KMeans
	from sampleDB import SampleDB
	from clusterDB import ClusterDB,Cluster
	sys.path.append("../apps/yahooNews/lib")
	from nysol.widget.yahooNews.lib.sample import Sample

	iFile="../libtest/DATA/icds.json"

	sampleDB=SampleDB()
	with open(iFile) as f:
		coms=json.load(f)

	for com in coms:
		#print(com)
		print(com.keys())
		sample=Sample(0)
		sample.fromJSON(com)
		sampleDB.add(sample)
	exit()
	vecs=[]
	for sample in sampleDB:
		vecs.append(sample.vector)
	vecs=np.array(vecs)

	model=KMeans(n_clusters=8)
	pred=model.fit_predict(vecs)
	print("####### pred")
	print(pred)
	print("####### unique(pred)")
	print(np.unique(pred))
	clusterDB=ClusterDB()
	for clusterNo in sorted(np.unique(pred)):
		cluster=Cluster(clusterNo)
		clusterDB.add(cluster)
	for sampleNo,clusterNo in enumerate(pred):
		cluster=clusterDB.clusterList[clusterNo]
		cluster.sampleDB.add(sampleDB.sampleList[sampleNo])
	#clusterDB.show()
	print("####### clusterDB")
	for c in clusterDB:
		c.show()


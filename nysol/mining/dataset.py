#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import nysol.mcmd as nm
import numpy as np

# category変数のdummy変数化
def mkDummy(svec):
	# svec: string vector (category variable)
	# ["a","c","a","b"]
	num2str=np.unique(svec) # ["a","b","c"]
	str2num={}
	for i,s in enumerate(num2str):
		str2num[s]=i

	data=np.zeros((len(svec), len(num2str)))
	for i,s in enumerate(svec):
		data[i,str2num[s]]=1
	return data

class Category(object):
	def __init__(self,name,data):
		self.name=name
		# data: string vector (category variable)
		# ["a","c","a","b"]
		self.num2str=np.unique(data) # ["a","b","c"]
		self.str2num={}
		for i,s in enumerate(self.num2str):
			self.str2num[s]=i

		self.data=np.zeros((len(data), len(self.num2str)))
		for i,s in enumerate(data):
			self.data[i,self.str2num[s]]=1.0

	def _summary(self):
		print("self.name:",self.name)
		print("self.num2str:",self.num2str)
		print("self.str2num:",self.str2num)
		print("self.data:",self.data.shape,self.data[0:10])

# iSize
# aSize
# data
# num2alpha
# alpha2num
class Item(object):
	def __init__(self,name,iSize,data):
		self.name=name
		self.iSize=iSize
		# data: string ndarray (item variable)
		# ["a","c","a","b"]
		self.num2alpha=np.unique(data) # ["a","b","c"]
		self.alpha2num={}
		for i,s in enumerate(self.num2alpha):
			self.alpha2num[s]=i
		self.data=data
		self.aSize=len(self.num2alpha)

	def _summary(self):
		print("self.name:",self.name)
		print("self.iSize:",self.iSize)
		print("self.num2alpha:",self.num2alpha)
		print("self.alpha2num:",self.alpha2num)
		print("self.data:",self.data.shape,self.data[0:10])

class Itemset(object):
	def __init__(self,config,idList):
		self.name=config["name"]
		self.iSize=int(config["iSize"])
		self.alpha2num=set([])
		self.num2alpha=[]
		self.data=[]

		idList_i=0
		f=None
		f<<=nm.mcut(f="id,item",i=self.name)
		f<<=nm.mdelnull(f="*")
		f<<=nm.muniq(k="id,item")
		for block in f.keyblock(k="id",s="item",dtype={"id":"str","item":"str"}):
			items=[]
			sid=block[0][0]
			while sid>idList[idList_i]:
				self.data.append([]) # データにidがないので追加
				idList_i+=1
			# この条件(idListにないsampleID)はありえないはずだがエラーとせずスキップさせる
			if sid<idList[idList_i]:
				continue
			for line in block:
				items.append(line[1])
				self.alpha2num.add(line[1])
			self.data.append(items)
			#self.data.append((idList[idList_i],items))
			idList_i+=1

		# データの最後のidがidListの最後でない場合、空のitemsetを追加
		while idList_i<len(idList):
			self.data.append([])
			#self.data.append((idList[idList_i],[]))
			idList_i+=1
		#print("itemset",len(self.data))

		self.num2alpha=sorted(list(self.alpha2num))
		self.alpha2num={}
		for i,alpha in enumerate(self.num2alpha):
			self.alpha2num[alpha]=i
		#print(self.num2alpha)
		#print(self.alpha2num)

		self.aSize=len(self.num2alpha)

	def _summary(self):
		print("self.name:",self.name)
		print("self.aSize:",self.aSize)
		print("self.iSize:",self.iSize)
		print("self.num2alpha:",self.num2alpha)
		print("self.alpha2num:",self.alpha2num)
		print("self.data:",len(self.data),self.data[0:10])

class Sequence(object):
	def __init__(self,config,idList):
		self.name=config["name"]
		self.iSize=int(config["iSize"])
		flds=config["fields"].split(",")
		self.idFld=flds[0]
		self.timeFN=flds[1]
		self.itemFN=flds[2]
		self.alpha2num=set([])
		self.num2alpha=[]
		self.data=[]

		items=set()
		f=None
		f<<=nm.mcut(f="%s,%s,%s"%(self.idFld,self.timeFN,self.itemFN),i=self.name)
		f<<=nm.muniq(k="%s,%s,%s"%(self.idFld,self.timeFN,self.itemFN))
		for line in f:
			items.add(line[2])

		idList_i=0
		f=None
		f<<=nm.mcut(f="id,time,item",i=self.name)
		f<<=nm.mdelnull(f="*")
		f<<=nm.muniq(k="id,time,item")
		for block in f.keyblock(k="id",s="time%n",dtype={"id":"str","time":"int","item":"str"}):
			sid=block[0][0]
			while sid>idList[idList_i]:
				self.data.append([sid,[]]) # データにidがないので追加
				#self.data.append((idList[idList_i],[])) # データにidがないので追加
				idList_i+=1
			# この条件(idListにないsampleID)はありえないはずだがエラーとせずスキップさせる
			if sid<idList[idList_i]:
				continue

			seq=[]
			items=[]
			timeBreak=False
			prevTime=block[0][1]
			for line in block:
				time=line[1]
				if prevTime!=time:
					seq.append([prevTime,items])
					items=[]
					prevTime=time
				items.append(line[2])
				self.alpha2num.add(line[2])
			self.data.append([sid,seq])
			#self.data.append((idList[idList_i],items))
			idList_i+=1

		# データの最後のidがidListの最後でない場合、空のseqを追加
		while idList_i<len(idList):
			self.data.append([idList[idList_i],[]])
			#self.data.append((idList[idList_i],[]))
			idList_i+=1
		#print("itemset",len(self.data))

		self.num2alpha=sorted(list(self.alpha2num))
		self.alpha2num={}
		for i,alpha in enumerate(self.num2alpha):
			self.alpha2num[alpha]=i
		print(self.num2alpha)
		print(self.alpha2num)

		self.aSize=len(self.num2alpha)

	def _summary(self):
		print("self.name:",self.name)
		print("self.aSize:",self.aSize)
		print("self.iSize:",self.iSize)
		print("self.num2alpha:",self.num2alpha)
		print("self.alpha2num:",self.alpha2num)
		print("self.data:",len(self.data),self.data[0:10])

class dataset(object):
	def readBaseFile(self):
		cats=[]
		items=[]
		for line in nm.mdelnull(f="*",i=self.iFile_name).msortf(f=self.idFld).getline(otype="dict"):
			### null値対応
			### itemFld対応 => indexing対象となるcategoryFld
			# sample-id項目
			self.id.append(line[self.idFld])

			# 目的変数
			if self.iFile_yType=="r": # regression
				self.y.append(float(line[self.iFile_yFld]))
			else:                # classification
				self.y.append(line[self.iFile_yFld])

			# 数値変数
			if self.iFile_nFlds:
				smp=[]
				for v in self.iFile_nFlds:
					#print(line[v])
					smp.append(float(line[v]))
				self.nums.append(smp)

			# カテゴリ変数
			if self.iFile_cFlds:
				smp=[]
				for v in self.iFile_cFlds:
					smp.append(line[v])
				cats.append(smp)

			# アイテム変数(indexing対象のcategory変数)
			if self.iFile_iFlds:
				smp=[]
				for v in self.iFile_iFlds:
					smp.append(line[v])
				items.append(smp)

		### List => ndarray
		self.y=np.array(self.y)
		self.sampleSize=len(self.y)
		self.nums=np.array(self.nums)

		for i,cat in enumerate(np.array(cats).transpose()):
			self.cats.append(Category(self.iFile_cFlds[i],cat))
			#print(self.cats[-1].data)

		for i,item in enumerate(np.array(items).transpose()):
			self.items.append(Item(self.iFile_iFlds[i],self.iFile_iSize[i],item))

	def __init__(self,config):
		self.idFld=config["idFld"] # サンプルID項目名
		self.iFile=config["iFile"] # 入力ファイル
		self.iFile_name=self.iFile["name"] # 入力ファイル名
		self.iFile_yFld=self.iFile["yFld"] # 目的変数名
		self.iFile_yType=self.iFile["yType"] # 目的変数タイプ:regression/classification

		self.iFile_nFlds=self.iFile["nFlds"] # 数値項目名
		self.iFile_cFlds=self.iFile["cFlds"] # カテゴリ項目名
		self.iFile_iFlds=self.iFile["iFlds"] # item項目名
		self.iFile_iSize=self.iFile["iSize"] # item項目indexサイズ


		self.id=[]
		self.y=[]
		self.nums=[]
		self.cats=[]
		self.items=[]
		# self.id,self.yなどの基本変数はここでセットされる
		self.readBaseFile()

		self.itemsets=[]
		if "traFiles" in config:
			for param in config["traFiles"]:
				self.itemsets.append(Itemset(param,self.id))
				#print("ds.id",len(ds.itemsets[-1].data))

		self.sequences=[]
		for param in config["seqFiles"]:
			self.sequences.append(Sequence(param,self.id))
			#print("ds.id",len(ds.itemsets[-1].data))

	def _summary(self):	
		print("self.idFld:",self.idFld)
		print("self.iFile_name:",self.iFile_name)
		print("self.iFile_yFld:",self.iFile_yFld)
		print("self.iFile_yType:",self.iFile_yType)
		print("self.iFile_nFlds:",self.iFile_nFlds)
		print("self.iFile_cFlds:",self.iFile_cFlds)
		print("self.iFile_iFlds:",self.iFile_iFlds)
		print("self.iFile_iSize:",self.iFile_iSize)

		print("### ID")
		print("self.id",len(self.id),self.id[0:10])
		print("### OBJECTIVE VARIABLE")
		print("self.y",self.y.shape,self.y[0:10])
		print("### NUMERIC VARIABLE")
		print("self.nums",self.nums.shape,self.nums[0:10])
		print("### CATEGORY VARIABLE")
		for cat in self.cats:
			cat._summary()
		print("### ITEM VARIABLE")
		for item in self.items:
			item._summary()
		print("### ITEMSET VARIABLE")
		for itemset in self.itemsets:
			itemset._summary()
		print("### SEQUENCE VARIABLE")
		for sequence in self.sequences:
			sequence._summary()

if __name__ == '__main__':
	import importlib
	configFile=os.path.expanduser(sys.argv[1])
	sys.path.append(os.path.dirname(configFile))
	config=importlib.import_module(os.path.basename(configFile).replace(".py",""))

	ds=dataset(config.dataset)
	ds._summary()


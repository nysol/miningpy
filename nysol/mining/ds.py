#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import nysol.mcmd as nm
import numpy as np
import pandas as pd
import json
import importlib
import tempfile

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
	def __init__(self,name,data,id_):
		self.name=name
		# data: string vector (category variable)
		# ["a","c","a","b"]
		self.num2str=np.unique(data).tolist() # ["a","b","c"]
		self.str2num={}
		for i,s in enumerate(self.num2str):
			self.str2num[s]=i

		self.data=np.zeros((len(data), len(self.num2str)))
		for i,s in enumerate(data):
			self.data[i,self.str2num[s]]=1.0
		self.data=pd.DataFrame(self.data,index=id_,columns=[name+"_"+s for s in self.num2str])

	def _summary(self):
		print("self.name:",self.name)
		print("self.num2str:",self.num2str)
		print("self.str2num:",self.str2num)
		print("self.data:",self.data.shape,self.data[0:10])

	def dump(self):
		dat={}
		dat["name"]=self.name
		dat["num2str"]=self.num2str
		dat["str2num"]=self.str2num
		return dat

# iSize
# aSize
# data
# num2alpha
# alpha2num
class Item(object):
	def __init__(self,name,iSize,data,id_):
		self.name=name
		self.iSize=iSize
		self.id_=id_
		# data: string ndarray (item variable)
		# ["a","c","a","b"]
		self.num2alpha=np.unique(data).tolist() # ["a","b","c"]
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

	def dump(self):
		dat={}
		dat["name"]=self.name
		dat["iSize"]=self.iSize
		dat["num2alpha"]=self.num2alpha
		dat["alpha2num"]=self.alpha2num
		return dat

class Itemset(object):
	def __init__(self,config,idList):
		self.name=config["name"]
		self.key=config["key"]
		self.item=config["item"]
		self.iSize=int(config["iSize"])
		self.alpha2num=set([])
		self.num2alpha=[]
		self.data=[]

		idList_i=0
		f=None
		f<<=nm.mcut(f="%s,%s"%(self.key,self.item),i=self.name)
		f<<=nm.mdelnull(f="*")
		f<<=nm.muniq(k="%s,%s"%(self.key,self.item))
		for block in f.keyblock(k=self.key,s=self.item,dtype={self.key:"str",self.item:"str"}):
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

	def dump(self):
		dat={}
		dat["name"]=self.name
		dat["aSize"]=self.aSize
		dat["iSize"]=self.iSize
		dat["num2alpha"]=self.num2alpha
		dat["alpha2num"]=self.alpha2num
		return dat

class Sequence(object):
	def __init__(self,config,idList):
		self.name=config["name"]
		self.iSize=int(config["iSize"])
		flds=config["fields"].split(",")
		self.idFld=flds[0]
		self.timeFN=flds[1]
		self.itemFN=flds[2]
		self.eParams=config["eParams"]
		self.oParams=config["oParams"]
		self.tempDir=tempfile.TemporaryDirectory()
		self.oParams["oPats"]="%s/xxpats"%(self.tempDir.name)
		self.oParams["oStats"]="%s/xxstats"%(self.tempDir.name)
		self.oParams["oOccs"]=None
		self.alpha2num=set([])
		self.num2alpha=[]
		self.data=[]

		os.system("head %s"%self.name)
		flds3="%s,%s,%s"%(self.idFld,self.timeFN,self.itemFN)
		items=set()
		f=None
		f<<=nm.mcut(f=flds3,i=self.name)
		f<<=nm.muniq(k=flds3)
		for line in f:
			items.add(line[2])

		idList_i=0
		f=None
		f<<=nm.mcut(f=flds3,i=self.name)
		f<<=nm.mdelnull(f="*")
		f<<=nm.muniq(k=flds3)
		for block in f.keyblock(k=self.idFld,s=self.timeFN+"%n",dtype={self.idFld:"str",self.timeFN:"int",self.itemFN:"str"}):
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

	def dump(self):
		dat={}
		dat["name"]=self.name
		dat["aSize"]=self.aSize
		dat["iSize"]=self.iSize
		dat["num2alpha"]=self.num2alpha
		dat["alpha2num"]=self.alpha2num
		return dat

class dataset(object):
	def readBaseFile(self):

		_nums=[]
		_cats=[]
		_items=[]
		for line in nm.mdelnull(f="*",i=self.tblFile_name).msortf(f=self.idFld).getline(otype="dict"):
			### null値対応
			### itemFld対応 => indexing対象となるcategoryFld
			# sample-id項目
			self.id.append(line[self.idFld])

			# 目的変数
			if self.tblFile_yType=="r": # regression
				self.y.append(float(line[self.tblFile_yFld]))
			else:                # classification
				self.y.append(line[self.tblFile_yFld])

			# 数値変数
			if self.tblFile_nFlds:
				smp=[]
				for v in self.tblFile_nFlds:
					#print(line[v])
					smp.append(float(line[v]))
				_nums.append(smp)

			# カテゴリ変数
			if self.tblFile_cFlds:
				smp=[]
				for v in self.tblFile_cFlds:
					smp.append(line[v])
				_cats.append(smp)

			# アイテム変数(indexing対象のcategory変数)
			if self.tblFile_iFlds:
				smp=[]
				for v in self.tblFile_iFlds:
					smp.append(line[v])
				items.append(smp)

		### List => pd.DataFrame
		self.sampleSize=len(self.y)
		self.y=pd.DataFrame(self.y,index=self.id,columns=[self.tblFile_yFld])
		if len(_nums)>0:
			self.nums=pd.DataFrame(_nums,index=self.id,columns=self.tblFile_nFlds)

		if len(_cats)>0:
			for i,cat in enumerate(np.array(_cats).transpose()):
				self.cats.append(Category(self.tblFile_cFlds[i],cat,self.id))

		if len(_items)>0:
			for i,item in enumerate(np.array(_items).transpose()):
				self.items.append(Item(self.tblFile_iFlds[i],self.tblFile_iSize[i],item,self.id))

	def __init__(self,configF):
		path=configF.replace("/",".").replace(".py","")
		config=importlib.import_module(path)
		config=config.dataset
		self.idFld=config["idFld"] # サンプルID項目名
		self.tblFile=config["tblFile"] # 入力ファイル
		self.tblFile_name=self.tblFile["name"] # 入力ファイル名
		self.tblFile_yFld=self.tblFile["yFld"] # 目的変数名
		self.tblFile_yType=self.tblFile["yType"] # 目的変数タイプ:regression/classification
		self.tblFile_nFlds= self.tblFile_cFlds= self.tblFile_iFlds= self.tblFile_iSize=None
		if "nFlds" in self.tblFile:
			self.tblFile_nFlds=self.tblFile["nFlds"] # 数値項目名
		if "cFlds" in self.tblFile:
			self.tblFile_cFlds=self.tblFile["cFlds"] # カテゴリ項目名
		if "iFlds" in self.tblFile:
			self.tblFile_iFlds=self.tblFile["iFlds"] # item項目名
			self.tblFile_iSize=self.tblFile["iSize"] # item項目indexサイズ

		self.id=[]
		self.y=[]
		self.nums=None # ここだけNone重要
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
		if "seqFiles" in config:
			for param in config["seqFiles"]:
				self.sequences.append(Sequence(param,self.id))
				#print("ds.id",len(ds.itemsets[-1].data))

	def _summary(self):	
		print("self.idFld:",self.idFld)
		print("self.tblFile_name:",self.tblFile_name)
		print("self.tblFile_yFld:",self.tblFile_yFld)
		print("self.tblFile_yType:",self.tblFile_yType)
		print("self.tblFile_nFlds:",self.tblFile_nFlds)
		print("self.tblFile_cFlds:",self.tblFile_cFlds)
		print("self.tblFile_iFlds:",self.tblFile_iFlds)
		print("self.tblFile_iSize:",self.tblFile_iSize)

		print("### ID")
		if self.id is not None:
			print("self.id",len(self.id),self.id[0:10])
		print("### OBJECTIVE VARIABLE")
		if self.y is not None:
			print("self.y",self.y.shape,self.y[0:10])
		print("### NUMERIC VARIABLE")
		if self.nums is not None:
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

	# datasetのmeta-dataを出力
	def save_summary(self,oPath):	
		dat={}
		dat["idFld"]=self.idFld
		dat["tblFile_name"]=self.tblFile_name
		dat["tblFile_yFld"]=self.tblFile_yFld
		dat["tblFile_yType"]=self.tblFile_yType
		dat["tblFile_nFlds"]=self.tblFile_nFlds
		dat["tblFile_cFlds"]=self.tblFile_cFlds
		dat["tblFile_iFlds"]=self.tblFile_iFlds
		dat["tblFile_iSize"]=self.tblFile_iSize
		dat["len(id)"]=len(self.id)
		dat["y.shape"]=self.y.shape
		if self.nums is not None:
			dat["nums.shape"]=self.nums.shape
		dat["cats"]=[]
		for cat in self.cats:
			dat["cats"].append(cat.dump())
		dat["items"]=[]
		for item in self.items:
			dat["items"].append(item.dump())
		dat["itemsets"]=[]
		for itemset in self.itemsets:
			dat["itemsets"].append(itemset.dump())
		dat["sequences"]=[]
		for sequence in self.sequences:
			dat["sequences"].append(sequence.dump())

		# jsonで保存
		json_dump = json.dumps(dat, ensure_ascii=False, indent=2)
		with open("%s/dataset.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

if __name__ == '__main__':
	import importlib
	configFile=os.path.expanduser(sys.argv[1])
	sys.path.append(os.path.dirname(configFile))
	config=importlib.import_module(os.path.basename(configFile).replace(".py",""))

	ds=dataset(config.dataset)
	ds._summary()


#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pandas as pd
import copy
import csv
import importlib
import nysol.mining.mspade as mm
from nysol.util.mmkdir import mkDir
from nysol.mining.rtree import rtree
from nysol.mining.ctree import ctree 
from nysol.mining.ds import dataset 

import warnings
warnings.filterwarnings('ignore')

from skopt import gp_minimize

class AlphabetIndex(object):
	def __init__(self):
		#self.config=config
		self.no=0
		self.counter=0
		#self.items=[] # item vectorのvector
		#self.iSize=[] # indexSize
		#self.num2alpha=[] # num=>alphabet
		#self.alpha2num={} # alphabet=>num
		self.spaces=[] # 探索空間
		#self.model=ctree(config["dTree"])

		self.features=[]
		self.featuresALL = []
		self.optimal_score=None
		self.optimal_model = None

	# item変数,itemset変数,sequence変数のindexing探索空間を設定する(spaces)
	# spcacesはbayes最適化探索空間で使われる一次元ベクトルなので、
	# 変数×値別にindexSizeをフラットに設定する
	def setSpaces(self,ds):

		self.ds=ds

		# item変数
		for item in self.ds.items:
			for _ in range(item.aSize):
				self.spaces.append(list(range(item.iSize)))

		# itemset変数
		for itemset in self.ds.itemsets:
			for _ in range(itemset.aSize):
				self.spaces.append(list(range(itemset.iSize))) # bayes最適化探索空間

		# sequence変数
		for sequence in self.ds.sequences:
			for _ in range(sequence.aSize):
				self.spaces.append(list(range(sequence.iSize))) # bayes最適化探索空間

	def getAI(self,spaces):
		ai=[]
		base_i=0
		# item変数
		for obj in self.ds.items:
			dat=["item",obj.name,[]]
			for j in range(obj.aSize):
				dat[2].append([obj.num2alpha[j],spaces[base_i+j]])
			ai.append(dat)
		base_i+=obj.aSize

		# itemset変数
		for obj in self.ds.itemsets:
			dat=["itemset",obj.name,[]]
			for j in range(obj.aSize):
				dat[2].append([obj.num2alpha[j],spaces[base_i+j]])
			ai.append(dat)
		base_i+=obj.aSize

		# sequence変数
		for obj in self.ds.sequences:
			dat=["isequence",obj.name,[]]
			for j in range(obj.aSize):
				dat[2].append([obj.num2alpha[j],spaces[base_i+j]])
			ai.append(dat)
		base_i+=obj.aSize

		return ai

	def showSpaces(self,spaces,verbose=3):
		if verbose==0:
			return
		self.counter+=1
		print("#### Alphabet-Index (iter=#%d)"%self.counter)
		if verbose==1:
			return

		ai=self.getAI(spaces)
		for dat in ai:
			if verbose==2:
				print(dat[1],"".join([str(v[1]) for v in dat[2]]))
			else:
				print(dat[1],",".join([str(v[0])+"="+str(v[1]) for v in dat[2]]))

	def enumSeqpatterns(self,name,data,eParams,oParams) :

		datas={name:data}
		iParams={ "iData":datas }
		spade=mm.Spade(iParams,eParams,oParams)
		rules=spade.run()
		return rules

	# bayes最適化で選ばれたalphabet-indexパラメータspacesに基づいて、
	# オリジナルのalphabetデータセットをindex化されたデータセットに変換する。
	# 以下は2つのitem変数i1,i2のindexing例。i1のindexサイズは2,i2のindexサイズは3。
	# ds.ietms  spaces                     itemIndex[0][0~sampleSize][0,1]
	# i1       a,b,c,A,B,C,D  i1           i1-0,i1-1
	# a        0,0,1,0,1,2,0  0            1    0   
	# b        ^              0            1    0   
	# a     base_i            0            1    0   
	# c  -------------------> 1  --------> 0    1   
	# b         index化       0   dummy化  1    0 
  #
	# ds.ietms  spaces                     itemIndex[1][0~sampleSize][0,1,2]
	# i2       a,b,c,A,B,C,D  i2           i2-0,i2-1,i2-2
	# A        0,0,1,0,1,2,0  0            1    0    0
	# A              ^        0            1    0    0
	# B           base_i      1            0    1    0
	# C  -------------------> 2  --------> 0    0    1
	# D         index化       0   dummy化  1    0    0
  #
	def indexing(self,spaces):
		self.showSpaces(spaces)

		# spaces上の現変数の開始位置
		# 変数,値の2次元空間を、spacesでは1次元空間に設定しているため(いわゆる2次元ポインタ)
		base_i=0

		#### item
		self.itemIndex=[]
		self.itemIndexfeatures=[]
	
		for i,item in enumerate(self.ds.items): # item変数数
			# sampleSize×indexSizeのdummy行列
			self.itemIndex.append(np.zeros((self.ds.sampleSize,item.iSize)))
			for j,alpha in enumerate(item.data):
				k=spaces[base_i+item.alpha2num[alpha]]
				# alphabet=>index置換: あるitem変数のalphabetをspaces[i]に置換
				self.itemIndex[i][j][k]=-1.0 # iは変数,jはサンプル,kはindex

			sfstk =	[ [] for _ in range(item.iSize) ]
			for ii , vv  in enumerate(spaces[base_i:base_i+item.aSize]):
				sfstk[vv].append(item.num2alpha[ii])
			for vvv in sfstk:
				self.itemIndexfeatures.append("%s_(%s)"%(item.name,",".join(vvv)))

			base_i+=item.aSize # i番目のitem変数のalphabetサイズ分base_iを飛ばす

		# pd.DataFrameに変換
		for i in range(len(self.itemIndex)):
			#self.ds.items[i]._summary()
			columns=[self.ds.items[i].name+"_"+str(j) for j in range(self.ds.items[i].iSize)]
			self.itemIndex[i]=pd.DataFrame(self.itemIndex[i],index=self.ds.y.index,columns=columns)
			#print(self.itemIndex[i])

		#### itemset
		# indexing dataの初期化
		self.itemsetIndex=[]
		self.itemsetfeatures=[]
		
		for i, itemset in enumerate(self.ds.itemsets):
			#itemset._summary()
			self.itemsetIndex.append(np.zeros((self.ds.sampleSize,self.ds.itemsets[i].iSize)))
			for j, items in enumerate(itemset.data):
				for alpha in items:
					k=spaces[base_i+itemset.alpha2num[alpha]]
					self.itemsetIndex[i][j][k]=-1.0

			sfstk =	[ [] for _ in range(itemset.iSize) ]
			for ii , vv  in enumerate(spaces[base_i:base_i+itemset.aSize]):
				sfstk[vv].append(itemset.num2alpha[ii])
			for vvv in sfstk:
				self.itemsetfeatures.append("%s_(%s)"%(itemset.item,",".join(vvv)))
			base_i+=itemset.aSize

		# pd.DataFrameに変換
		for i in range(len(self.itemsetIndex)):
			#self.ds.itemsets[i]._summary()
			columns=[self.ds.itemsets[i].name+"_"+str(j) for j in range(self.ds.itemsets[i].iSize)]
			self.itemsetIndex[i]=pd.DataFrame(self.itemsetIndex[i],index=self.ds.y.index,columns=columns)
			#print(self.itemsetIndex[i])
		
		#### sequence
		self.sequenceIndex = []
		self.sequenceIndexfeatures = []

		#id変換表
		idmap={x:i for i,x in enumerate(self.ds.id)}
		for i, sequence in enumerate(self.ds.sequences):
			#sequence._summary()
			indexedSequence=[]
			for elements in sequence.data:
				# print(elements)
				# ['100', [[97, ['b', 'h']], [194, ['b', 'd']], [256, ['g', 'j']], [353, ['d', 'e']]]]
				sid=elements[0]
				indexedElements=[]
				for itemset in elements[1]:
					# print(itemset)
					# [97, ['b', 'h']]
					time=itemset[0]
					indexedItemset=set()
					for alpha in itemset[1]:
						index=spaces[base_i+sequence.alpha2num[alpha]]
						indexedItemset.add(str(index)) # mspade:数値だとおかしくなる
					indexedElements.append([time,list(indexedItemset)])
				indexedSequence.append([sid,indexedElements])

			# enumerate itemset sequence patterns
			rules = self.enumSeqpatterns(sequence.name,indexedSequence,sequence.eParams,sequence.oParams)

			#{
			# クラス名
			#	'c1': (
			# pattern:クラス名,pid,time,item:  {A,B,F} , {D}{B,F}{A}
			#		[['c1', 0, 0, 'D'], ['c1', 0, 1, 'B'], ['c1', 0, 1, 'F'], ['c1', 0, 2, 'A']],
			# stats:クラス名,pid,size,len,occ
			#		[['c1', 0, 4, 3, 2, 0, 1.0]],
			# 出現:クラス名,pid,recordID
			#		[['c1', 0, '1'], ['c1', 0, '4']]
			#	),
			#	'c2': (
			#		[['c2', 1, 0, 'B'], ['c2', 1, 0, 'C'], ['c2', 1, 0, 'D'], ['c2', 2, 0, 'D'], ['c2', 2, 1, 'C'], ['c2', 2, 1, 'D'], ['c2', 2, 2, 'D']],
			#		[['c2', 1, 3, 1, 2, 0, 1.0], ['c2', 2, 4, 3, 2, 0, 1.0]],
			#		[['c2', 1, '5'], ['c2', 1, '7'], ['c2', 2, '5'], ['c2', 2, '8']]
			#	)
			#}
			#self.ds.sampleSize
			#print(sequence._summary())
			columns=[]
			for rule in rules.values():
				for stat in rule[1]:
					clsName=stat[0]
					patNo  =stat[1]
					columns.append("%s_%d"%(clsName,patNo))
			self.sequenceIndexfeatures += columns

			rowSize=self.ds.sampleSize
			colSize=len(columns)
			data=np.zeros((rowSize,colSize))
			for rule in rules.values():
				pats=rule[0]
				stat=rule[1]
				occs=rule[2]
				for occ in occs:
					row=idmap[occ[2]]
					col=occ[1]
					data[row][col] = -1.0
			self.sequenceIndex.append(pd.DataFrame(data,index=self.ds.y.index,columns=columns))

			base_i+=sequence.aSize
		#print(self.sequenceIndex)

	# self.xにモデル用データセットのx作成
	def mkx(self,space):

		self.features = []
		##1 indexing実行
		self.indexing(space) # self.itemIndex: item,itemsetデータをxでindexingする

		# np.hstackするためのダミー列作成
		#self.x=np.empty((len(self.ds.y),1))
		self.x = pd.DataFrame(index=self.ds.y.index, columns=[])

		##2 データセットの結合
		# 数値変数
		if len(self.ds.nums) !=0 :
			#self.x=np.hstack((self.x,self.ds.nums))
			self.x=self.x.join(self.ds.nums)
			for xx in self.ds.tblFile_nFlds:
				self.features.append(xx)

		# category変数
		for cat in self.ds.cats:
			#self.x=np.hstack((self.x,cat.data))
			self.x=self.x.join(cat.data)
			for v in cat.num2str:
				self.features.append("%s_%s"%(cat.name,v))

		# index化されたitem変数
		for dummy in self.itemIndex:
			#self.x=np.hstack((self.x,dummy))
			self.x=self.x.join(dummy)

		for v in self.itemIndexfeatures:
			self.features.append(v)		

		# index化されたitemset変数
		for dummy in self.itemsetIndex:
			#self.x=np.hstack((self.x,dummy))
			self.x=self.x.join(dummy)

		for v in self.itemsetfeatures:
			self.features.append(v)		

		# index化されたsequence変数
		for dummy in self.sequenceIndex:
			#self.x=np.hstack((self.x,dummy))
			self.x=self.x.join(dummy)

		for v in self.sequenceIndexfeatures:
			self.features.append(v)		

		# join用の列を削除
		#self.x=self.x[:,1:]
		#print(self.x)
		self.featuresALL.append(self.features)
		#print(self.featuresALL)
		#print(list(self.x.columns))
		#exit()


	# bayes最適化目的関数
	##1. indexing対象項目があれば、indexingしてdummy化されたデータを作成
	##2. 各変数種別別のデータセットを結合して説明変数を作成
	##3. モデル構築
	##4. 最適化スコア(accuracy等)を返す
	def objFunction(self,space): # xはself.spaces
		self.mkx(space)

		##3. モデル構築
		#print(self.x)
		#print(self.ds.y)
		print(self.model)
		self.model.setDataset(self.x,self.ds.y)
		self.model.build(self.params,visualizing=False)

		##4. スコアを返す(-1を返すのはbayes最適化が最小化のため)
		score=self.model.score
		print("accuracy",score)

		if self.optimal_score == None or self.optimal_score < score:
			self.optimal_score = score
			self.optimal_model = copy.deepcopy(self.model)
			self.optimal_features = copy.deepcopy(self.features)
			self.optimal_param = self.model.opt_param
			
		return (-1)*score

	def predict(self,space,optimal_param): # xはself.spaces
		self.mkx(space)

		##3. モデル構築 & prediction
		self.model.setDataset(self.x,self.ds.y)
		self.pred=self.optimal_model.predict(self.x)
		self.pred.evaluate(self.ds.y)

	# bayes最適化実行
	def optimize(self,modelName,params,n_calls=20):
		self.modelName=modelName
		self.params=params
		try:
			self.model=eval(modelName) # rtree()
		except NameError:
			raise ValueError("##ERROR: unknown modeling function:%s"%(modelName))

		if len(self.spaces)==0:
			self.mkx(None)
			self.model.setDataset(self.x,self.ds.y)
			self.model.build(params,visualizing=False)
			self.optimal_param = self.model.opt_param
			self.optimal_score = self.model.score
			self.optimal_model = self.model
			self.optimal_features = self.features
			self.optimal_space = self.spaces
			#print("score",self.model.score)
			#print("opt_param",self.model.opt_param)

		else:
			#print(self.spaces)
			res=gp_minimize(self.objFunction, self.spaces, n_calls=n_calls, random_state=11)
			self.features = self.featuresALL[res.x_iters.index(res.x)]
			self.optimal_space = res.x

class mcarm(object):
	def __checkConfig(self,config):
		print(config.dataset)
		return
		if not os.path.exists(config["dataset"]["tblFile"]["name"]):
			raise Exception("## ERROR: file not found: %s"%config["dataset"]["tblFile"]["name"])
			# iFldsとiSizeのサイズが異なればエラー
			# indexSizeがアイテムの種類数を超えた時のチェックどうするか？

	def __init__(self,configF):
		self.configF = configF
		path=configF.replace("/",".").replace(".py","")
		self.config=importlib.import_module(path)
		self.__checkConfig(self.config)

	def build(self,params,n_calls=20):
		self.params=params
		self.ds=dataset(self.config.dataset)
		#self.ds._summary()
		self.ai=AlphabetIndex()
		self.ai.setSpaces(self.ds)
		self.ai.optimize("ctree()",params,n_calls=n_calls)

	def predict(self):#,x_df):
		self.ai.predict(self.ai.optimal_space,self.ai.optimal_param)

	def save(self,oPath):
		os.makedirs(oPath,exist_ok=True)
		self.ai.optimal_model.visualize()
		self.ai.optimal_model.save(oPath)
		self.ai.pred.save(oPath)

		ai=self.ai.getAI(self.ai.optimal_space)
		with open("%s/alphabetIndex.csv"%(oPath),"w") as f:
			writer = csv.writer(f)
			writer.writerow(["type","variable","alphabet","index"])
			for dat in ai:
				for line in dat[2]:
					writer.writerow([dat[0],dat[1],line[0],line[1]])

if __name__ == '__main__':
	#import json
	#configFile="bonfig/config_yakir.json"
	#with open(configFile, 'r') as rp:
	#	config = json.load(rp)
	#config=importlib.import_module(os.path.basename(configFile).replace(".py",""))
	#configFile="bonfig_ctd.py"

	params={
		"max_depth":10
	}
	configF="bonfig/config_crx.py"

	model=mcarm(configF)
	model.build(params,n_calls=20)
	model.predict()
	model.save("xxbon_crx")


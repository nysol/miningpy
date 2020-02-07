#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pandas as pd
import pickle
import copy
import csv
import tempfile
import nysol.mining.mspade as mm
from nysol.util.mmkdir import mkDir
from nysol.mining.rtree import rtree
from nysol.mining.ctree import ctree 

import warnings
warnings.filterwarnings('ignore')

from skopt import gp_minimize

class AlphabetIndex(object):
	def __init__(self,ds):
		self.ds=ds
		self.no=0
		self.counter=0
		self.spaces=[] # 探索空間
		self.bo_his=None # bayes最適化の結果履歴(Noneなら新規学習,学習済モデルなら再学習)
		self.optimal_score=None
		self.optimal_model = None

		# item変数,itemset変数,sequence変数のindexing探索空間を設定する(spaces)
		# spcacesはbayes最適化探索空間で使われる一次元ベクトルなので、
		# 変数×値別にindexSizeをフラットに設定する
		# item変数
		for item in self.ds.items:
			for _ in range(item.aSize):
				self.spaces.append(list(range(item.iSize)))
		# itemset変数
		for itemset in self.ds.itemsets:
			for _ in range(itemset.aSize):
				self.spaces.append(list(range(itemset.iSize))) # bayes最適化探索空間
		# sequence変数
		self.seq_tempDir=tempfile.TemporaryDirectory()
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

	# optimal modelの保存(modelとalphabet-index)
	def save(self,oPath):
		if self.optimal_model is not None:
			self.optimal_model.save(oPath)

		# optimal alphaabet-indexをCSV出力
		ai=self.getAI(self.optimal_space)
		with open("%s/alphabetIndex.csv"%(oPath),"w") as f:
			writer = csv.writer(f)
			writer.writerow(["type","variable","alphabet","index"])
			for dat in ai:
				for line in dat[2]:
					writer.writerow([dat[0],dat[1],line[0],line[1]])

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
		iParams={"iData":datas }
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
	def indexing(self,spaces,ds):
		if spaces is None:
			return
		self.showSpaces(spaces)

		# spaces上の現変数の開始位置
		# 変数,値の2次元空間を、spacesでは1次元空間に設定しているため(いわゆる2次元ポインタ)
		base_i=0

		#### item
		self.itemIndex=[]
	
		for i,item in enumerate(ds.items): # item変数数
			# sampleSize×indexSizeのdummy行列
			self.itemIndex.append(np.zeros((ds.sampleSize,item.iSize)))
			for j,alpha in enumerate(item.data):
				k=spaces[base_i+item.alpha2num[alpha]]
				# alphabet=>index置換: あるitem変数のalphabetをspaces[i]に置換
				self.itemIndex[i][j][k]=-1.0 # iは変数,jはサンプル,kはindex
			base_i+=item.aSize # i番目のitem変数のalphabetサイズ分base_iを飛ばす

		# pd.DataFrameに変換
		for i in range(len(self.itemIndex)):
			#self.ds.items[i]._summary()
			columns=[ds.items[i].name+"_"+str(j) for j in range(ds.items[i].iSize)]
			self.itemIndex[i]=pd.DataFrame(self.itemIndex[i],index=ds.id,columns=columns)
			#print(self.itemIndex[i])

		#### itemset
		# indexing dataの初期化
		self.itemsetIndex=[]
		
		for i, itemset in enumerate(ds.itemsets):
			#itemset._summary()
			self.itemsetIndex.append(np.zeros((ds.sampleSize,ds.itemsets[i].iSize)))
			for j, items in enumerate(itemset.data):
				for alpha in items:
					k=spaces[base_i+itemset.alpha2num[alpha]]
					self.itemsetIndex[i][j][k]=-1.0

		# pd.DataFrameに変換
		for i in range(len(self.itemsetIndex)):
			#self.ds.itemsets[i]._summary()
			columns=[ds.itemsets[i].name+"_"+str(j) for j in range(ds.itemsets[i].iSize)]
			self.itemsetIndex[i]=pd.DataFrame(self.itemsetIndex[i],index=ds.id,columns=columns)
			#print(self.itemsetIndex[i])
		
		#### sequence
		self.sequenceIndex = []

		#id変換表
		idmap={x:i for i,x in enumerate(ds.id)}
		for i, sequence in enumerate(ds.sequences):
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

			# rules:
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

			rowSize=ds.sampleSize
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
			self.sequenceIndex.append(pd.DataFrame(data,index=ds.id,columns=columns))

			base_i+=sequence.aSize
		#print(self.sequenceIndex)

	# モデル用データセットxの作成
	def mkx(self,ds,space=None):
		##1 item,itemset,sequenceデータをspaceでindexingする
		self.indexing(space,ds)

		##2 データセットの結合
		# indexのみの空データ
		x = pd.DataFrame(index=ds.id, columns=[])
		# 数値変数
		if ds.nums is not None:
			x=x.join(ds.nums)
		# category変数
		for cat in ds.cats:
			x=x.join(cat.data)
		# index化されたitem変数
		for dummy in self.itemIndex:
			x=x.join(dummy)
		# index化されたitemset変数
		for dummy in self.itemsetIndex:
			x=x.join(dummy)
		# index化されたsequence変数
		for dummy in self.sequenceIndex:
			x=x.join(dummy)
		return x

	# bayes最適化目的関数
	##1. indexing対象項目があれば、indexingしてdummy化されたデータを作成
	##2. 各変数種別別のデータセットを結合して説明変数を作成
	##3. モデル構築
	##4. 最適化スコア(accuracy等)を返す
	def objFunction(self,space): # xはself.spaces
		x=self.mkx(self.ds,space)

		##3. モデル構築
		#print(self.x)
		#print(self.ds.y)
		self.model.setDataset(x,self.ds.y)
		self.model.build(self.params,visualizing=False)

		##4. スコアを返す(-1を返すのはbayes最適化が最小化のため)
		score=self.model.score
		print("## score",score)

		if self.optimal_score == None or self.optimal_score < score:
			self.optimal_space = copy.deepcopy(space)
			self.optimal_score = score
			self.optimal_model = copy.deepcopy(self.model)
			self.optimal_param = self.model.opt_param
			for seq in self.ds.sequences:
				name=seq.name.replace("/","_").replace(".","")
				os.system("cp %s %s/seq_patterns_%s.csv"%(seq.oParams["oPats"],self.seq_tempDir.name,name))
				os.system("cp %s %s/seq_stats_%s.csv"%(seq.oParams["oStats"],self.seq_tempDir.name,name))
			#print(self.optimal_model.tree_text)
			#print(self.optimal_space)
			#print("-------------")
		return (-1)*score

	# optimal_space,optimal_modelで予測
	def predict(self,ds):
		x=self.mkx(ds,self.optimal_space)
		pred=self.optimal_model.predict(x)
		return pred

	# bayes最適化実行
	# x0,y0が設定されていれば再学習
	def optimize(self,modelFunc,params,n_calls=200,n_random_starts=20,x0=None,y0=None):
		self.modelFunc=modelFunc
		self.params=params
		try:
			self.model=eval(modelFunc) # ctree()
		except NameError:
			raise ValueError("##ERROR: unknown modeling function:%s"%(modelFunc))

		if len(self.spaces)==0:
			x=self.mkx(self.ds)
			self.model.setDataset(x,self.ds.y)
			self.model.build(params,visualizing=False)
			self.optimal_param = self.model.opt_param
			self.optimal_score = self.model.score
			self.optimal_model = self.model
			self.optimal_space = self.spaces
			#print("score",self.model.score)
			#print("opt_param",self.model.opt_param)

		else:
			#print(self.spaces)
			if x0 is None or y0 is None: # 新規学習の場合
				self.bo_his=gp_minimize(self.objFunction, self.spaces, n_calls=n_calls, n_random_starts=n_random_starts,random_state=11)
			else: # 再学習の場合(n_random_starts=0でcallされる)
				self.bo_his=gp_minimize(self.objFunction, self.spaces, n_calls=n_calls, n_random_starts=n_random_starts,random_state=11,x0=x0,y0=y0)
			#self.optimal_space = self.bo_his.x

class mcarm(object):
	def __checkConfig(self,config):
		print(config.dataset)
		return
		if not os.path.exists(config["dataset"]["tblFile"]["name"]):
			raise Exception("## ERROR: file not found: %s"%config["dataset"]["tblFile"]["name"])
			# iFldsとiSizeのサイズが異なればエラー
			# indexSizeがアイテムの種類数を超えた時のチェックどうするか？

	def __init__(self,ds=None):
		if ds is not None:
			self.setDataset(ds)

	def setDataset(self,ds):
		print("##MSG: setting dataset ...")
		self.ds=ds
		self.ai=AlphabetIndex(self.ds)
		#self.ds._summary()

	def build(self,modelFunc,params,n_calls=20,n_random_starts=10):
		# 新規学習
		if self.ai.bo_his is None:
			self.ai.optimize(modelFunc,params,n_calls=n_calls,n_random_starts=n_random_starts)
		# 再学習(既存のboの履歴から探索したspaceとその値をリストで与える)
		else:
			x0=self.ai.bo_his.x_iters
			y0=self.ai.bo_his.func_vals
			self.ai.optimize(modelFunc,params,n_calls=n_calls,n_random_starts=0,x0=x0,y0=y0)
		self.ai.optimal_model.visualize()

	def predict(self,ds):
		pred=self.ai.predict(ds)
		return pred

	def load(iFile):
		with open(iFile, 'rb') as fpr:
			model = pickle.load(fpr)
		# tempfile(dir)はcloseした時に自動削除されるので再作成
		model.seq_tempDir=tempfile.TemporaryDirectory()
		for seq in model.ds.sequences:
			seq.tempDir=tempfile.TemporaryDirectory()
			seq.oParams["oPats"]="%s/xxpats"%(seq.tempDir.name)
			seq.oParams["oStats"]="%s/xxstats"%(seq.tempDir.name)
		return model

	def save(self,oPath):
		os.makedirs(oPath,exist_ok=True)
		self.ds.save_summary(oPath) # datasetのsummayを保存
		self.ai.save(oPath)         # 最適モデルとそのalphabet-indexの保存
		for seq in self.ds.sequences: # sequence patternの保存
			os.system("cp %s/* %s"%(self.ai.seq_tempDir.name,oPath))

		oFile="%s/model.sav"%(oPath)
		with open(oFile, 'wb') as fpw:
			pickle.dump(self, fpw)

if __name__ == '__main__':
	from nysol.mining.ds import dataset 
	def run_example(configF,oPath,n_calls,n_random_starts):
		ds=dataset(configF)
		ds._summary()

		modelFunc="ctree()"
		params={
			"max_depth":10
		}
		model=mcarm(ds)
		model.build(modelFunc,params,n_calls=n_calls,n_random_starts=n_random_starts)
		model.save(oPath)

		pred=model.predict(ds)
		pred.evaluate(ds.y)
		pred.save(oPath)

	def run_relearn(configF,oPath,n_calls):
		ds=dataset(configF)
		ds._summary()

		modelFunc="ctree()"
		params={
			"max_depth":10
		}
		model=None
		model=mcarm.load(oPath+"/model.sav")
		model.build(modelFunc,params,n_calls=n_calls) # 再学習
		model.save(oPath)

		pred=model.predict(ds)
		pred.evaluate(ds.y)
		pred.save(oPath)

	#run_example("bonfig_ctd.py","xxbon_ctd")
	#run_example("bonfig/config_crx.py","xxbon_crx")
	#run_example("bonfig/config_crx_seq.py","xxbon_crx_seq",50,20)
	run_relearn("bonfig/config_crx_seq.py","xxbon_crx_seq",50)


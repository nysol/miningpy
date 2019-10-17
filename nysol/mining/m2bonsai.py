#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import copy
import nysol.mining.mspade as mm

import warnings
warnings.filterwarnings('ignore')

from skopt import gp_minimize
from dtree import dtree
from dataset import dataset

def checkConfig(config):

	if not os.path.exists(config.dataset["iFile"]["name"]):
		raise Exception("## ERROR: file not found: %s"%config.iFile)

	# iFldsとiSizeのサイズが異なればエラー

	# indexSizeがアイテムの種類数を超えた時のチェックどうするか？

class AlphabetIndex(object):

	def __init__(self):
		self.no=0
		#self.items=[] # item vectorのvector
		#self.iSize=[] # indexSize
		#self.num2alpha=[] # num=>alphabet
		#self.alpha2num={} # alphabet=>num
		self.spaces=[] # 探索空間
		self.model=dtree(config.dTree)
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




	def enumSeqpatterns(self,name,data) :

		datas={name:data}
		iParams={ "iData":datas }
		eParams={
			"minSup":5,        # 最小サポート(件数)
			"minSupProb":None, # 最小サポート(確率) minSupがNoneでなければminSup優先
			"maxSize":4,       # パターンを構成する総アイテム数の上限
			"maxLen":3,        # パターンを構成する総エレメント数の上限
			"minGap":None,     # エレメント間最小ギャップ長
			"maxGap":None,     # エレメント間最大ギャップ長
			"maxWin":4         # 全体のマッチ幅最大長
		}
		oParams={
			"rule":False,        # 未実装
			"maximal":False,     # 極大パターンのみ選択
			"topk":10,           # 上位ルール
			"minSize":None,      # maxSizeの最小版
			"minLen":None,       # maxLenの最小版
			"maxSup":None,       # minSupの最大版
			"minPprob":None,      # 最小事後確率
			#"minPprob":0.7,      # 最小事後確率
			"oPats":"./xxoutOpats",# 出現出力ファイル(Noneで出力しない)
			"oStats":"./xxoutOstats",# 出現出力ファイル(Noneで出力しない)
			"oOccs":"./xxoutOccs"  # 出現出力ファイル(Noneで出力しない)
		}
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
				self.itemIndex[i][j][k]=1.0 # iは変数,jはサンプル,kはindex

			sfstk =	[ [] for _ in range(item.iSize) ]
			for ii , vv  in enumerate(spaces[base_i:base_i+item.aSize]):
				sfstk[vv].append(item.num2alpha[ii])
			for vvv in sfstk:
				self.itemIndexfeatures.append("%s_(%s)"%(item.name,",".join(vvv)))

			base_i+=item.aSize # i番目のitem変数のalphabetサイズ分base_iを飛ばす



		#### itemset
		# indexing dataの初期化
		self.itemsetIndex=[]
		self.itemsetfeatures=[]
		
		for i, itemset in enumerate(self.ds.itemsets):
			self.itemsetIndex.append(np.zeros((self.ds.sampleSize,self.ds.itemsets[i].iSize)))
			for j, items in enumerate(itemset.data):
				for alpha in items:
					k=spaces[base_i+itemset.alpha2num[alpha]]
					self.itemsetIndex[i][j][k]=1.0

			sfstk =	[ [] for _ in range(itemset.iSize) ]
			for ii , vv  in enumerate(spaces[base_i:base_i+itemset.aSize]):
				sfstk[vv].append(itemset.num2alpha[ii])
			for vvv in sfstk:
				self.itemsetfeatures.append("%s_(%s)"%(itemset.name,",".join(vvv)))
			base_i+=itemset.aSize

		
		#### sequence
		#id変換表
		idmap={}
		for i,x in enumerate(self.ds.id):
			idmap[x]=i	

		self.indexedSequences=[]
		self.sequenceIndex = []

		self.sequenceIndexfeatures = []


		for i, sequence in enumerate(self.ds.sequences):

			indexedSequence=[]
			for elements in sequence.data:
				sid=elements[0]
				indexedElements=[]
				for itemset in elements[1]:
					indexedItemset=set()
					time=itemset[0]
					for alpha in itemset[1]:
						index=spaces[base_i+sequence.alpha2num[alpha]]
						#indexedItemset.add(index)
						indexedItemset.add(str(index))
					indexedElements.append([time,list(indexedItemset)])
				indexedSequence.append([sid,indexedElements])


			rules = self.enumSeqpatterns(sequence.name,indexedSequence)

			sfstk =	[ [] for _ in range(sequence.iSize) ]
			for ii , vv  in enumerate(spaces[base_i:base_i+sequence.aSize]):
				sfstk[vv].append(sequence.num2alpha[ii])

			for v in rules.values():

				if len(v[0]) == 0: # これこれでいい？
					continue
					
				# 応急処置
				pidstk =[]

				pre = None
				for vv in v[2]: # ['c2', 0, '752']
					if pre != vv[1]:
						pidstk.append(vv[1]) 
					pre = vv[1]
				

				self.sequenceIndex.append(np.zeros((self.ds.sampleSize,len(pidstk))))

				pre = v[2][0][1]
				pos=0
				for vv in v[2]: # ['c2', 0, '752']
					if pre != vv[1]:
						pos+=1 

					self.sequenceIndex[-1][idmap[vv[2]]][pos] = 1.0
					pre = vv[1]

				name = v[0][0][0]
				pre1 = v[0][0][1]
				pre2 = v[0][0][2]
				fstr = ""

				#もちょっと考える
				skip=False
				for vv1 in v[0]: 

					if not vv1[1] in pidstk :
						skip=True
						continue

					if skip :
						pre1 = vv1[1]
						pre2 = vv1[2]
						skip=False
						
			
					if pre1 != vv1[1]:
						self.sequenceIndexfeatures.append("%s_%s"%(name,fstr))
						pre1 = vv1[1]
						pre2 = vv1[2]
					elif pre2 != vv1[2]:
						fstr+=">"
						pre2 = vv1[2]

					fstr += "[" + ",".join(sfstk[int(vv1[3])]) + "]"
	
				self.sequenceIndexfeatures.append("%s_%s"%(name,fstr))

			base_i+=sequence.aSize



	# self.xにモデル用データセットのx作成
	def mkx(self,space):

		self.features = []
		##1 indexing実行
		self.indexing(space) # self.itemIndex: item,itemsetデータをxでindexingする

		# np.hstackするためのダミー列作成
		self.x=np.empty((len(self.ds.y),1))

		##2 データセットの結合
		# 数値変数
		if len(self.ds.nums) !=0 :
			self.x=np.hstack((self.x,self.ds.nums))
		for xx in self.ds.iFile_nFlds:
			self.features.append(xx)

		# category変数
		for cat in self.ds.cats:
			self.x=np.hstack((self.x,cat.data))
			for v in cat.num2str:
				self.features.append("%s_%s"%(cat.name,v))

		# index化されたitem変数
		for dummy in self.itemIndex:
			self.x=np.hstack((self.x,dummy))

		for v in self.itemIndexfeatures:
			self.features.append(v)		


		# index化されたitemset変数
		for dummy in self.itemsetIndex:
			self.x=np.hstack((self.x,dummy))

		for v in self.itemsetfeatures:
			self.features.append(v)		


		#print(self.x.transpose().shape)
		#np.savetxt('xxham_%d.txt'%self.no, self.x)
		#self.no+=1
		#print(self.x)

		for dummy in self.sequenceIndex:
			print(dummy)
			self.x=np.hstack((self.x,dummy))


		for v in self.sequenceIndexfeatures:
			self.features.append(v)		

		# join用の列を削除
		self.x=self.x[:,1:]
		self.featuresALL.append(self.features)


	# bayes最適化目的関数
	##1. indexing対象項目があれば、indexingしてdummy化されたデータを作成
	##2. 各変数種別別のデータセットを結合して説明変数を作成
	##3. モデル構築
	##4. 最適化スコア(accuracy等)を返す
	def objFunction(self,space): # xはself.spaces

		self.features = []
		##1 indexing実行
		self.indexing(space) # self.itemIndex: item,itemsetデータをxでindexingする
		
		##2 データセットの結合
		# 数値変数
		#print(len(self.ds.y))
		self.x=np.empty((len(self.ds.y),1))
		#print(self.x)
		#print(np.asarray(self.x))
		#exit()
		if len(self.ds.nums) !=0 :
			self.x=np.hstack((self.x,self.ds.nums))
		for xx in self.ds.iFile_nFlds:
			self.features.append(xx)

		# category変数
		for cat in self.ds.cats:
			self.x=np.hstack((self.x,cat.data))
			for v in cat.num2str:
				self.features.append("%s_%s"%(cat.name,v))

		# index化されたitem変数
		for dummy in self.itemIndex:
			self.x=np.hstack((self.x,dummy))

		for v in self.itemIndexfeatures:
			self.features.append(v)		


		# index化されたitemset変数
		for dummy in self.itemsetIndex:
			self.x=np.hstack((self.x,dummy))

		for v in self.itemsetfeatures:
			self.features.append(v)		


		#print(self.x.transpose().shape)
		#np.savetxt('xxham_%d.txt'%self.no, self.x)
		#self.no+=1
		#print(self.x)

		for dummy in self.sequenceIndex:
			print(dummy)
			self.x=np.hstack((self.x,dummy))


		for v in self.sequenceIndexfeatures:
			self.features.append(v)		

		# join用の列を削除
		self.x=self.x[:,1:]
		
		
		"""

		##2 データセットの結合
		# 数値変数
		self.x=self.ds.nums
		for xx in self.ds.iFile_nFlds:
			self.features.append(xx)

		# category変数
		for cat in self.ds.cats:
			self.x=np.hstack((self.x,cat.data))
			for v in cat.num2str:
				self.features.append("%s_%s"%(cat.name,v))


		# index化されたitem変数
		for dummy in self.itemIndex:
			self.x=np.hstack((self.x,dummy))

		for v in self.itemIndexfeatures:
			self.features.append(v)		


		# index化されたitemset変数
		for dummy in self.itemsetIndex:
			self.x=np.hstack((self.x,dummy))

		for v in self.itemsetfeatures:
			self.features.append(v)		

		for dummy in self.sequenceIndex:
			self.x=np.hstack((self.x,dummy))


		for v in self.sequenceIndexfeatures:
			self.features.append(v)		
		"""


		self.featuresALL.append(self.features)
		##3. モデル構築
		self.model.setDataset(self.x,self.ds.y)
		self.model.build()

		##4. スコアを返す(-1を返すのはbayes最適化が最小化のため)
		score=self.model.score
		print("accuracy",score)

		self.model.vizModel("graph.pdf",None)

		if self.optimal_score == None or self.optimal_score < score:
			self.optimal_score = score
			self.optimal_model = copy.deepcopy(self.model)
			self.optimal_features = copy.deepcopy(self.features)
			
		return (-1)*score


	# bayes最適化実行
	def optimize(self):
		if len(self.spaces)==0:
			self.mkx(None)
			self.model.setDataset(self.x,self.ds.y)
			self.model.build()
			self.optimal_score = self.model.score
			self.optimal_model = self.model
			self.optimal_features = self.features

		else:
			res=gp_minimize(self.objFunction, self.spaces, n_calls=10, random_state=11)
			self.features = self.featuresALL[res.x_iters.index(res.x)]


##########
# entry point
argv=sys.argv
if len(argv)!=2:
	print("m2bonsai.py ")
	print("%s 設定ファイル(py)"%argv[0])
	exit()

# configファイルの読み込み
import importlib
configFile=os.path.expanduser(argv[1])
sys.path.append(os.path.dirname(configFile))
config=importlib.import_module(os.path.basename(configFile).replace(".py",""))
checkConfig(config)

ds=dataset(config.dataset)

ai=AlphabetIndex()
ai.setSpaces(ds)
ai.optimize()

print(ai.optimal_score)
print(ai.optimal_features)

ai.optimal_model.vizModel("graph.pdf",None)
ai.optimal_model.vizModel("graph.pdf",ai.optimal_features)


exit()

model=Dtree()
model.setDataset(ds.x,ds.y)
model.build()
model.vizModel("graph.pdf")


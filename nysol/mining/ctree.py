#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
warnings.simplefilter('ignore')

import os
import sys
import numpy as np
import pickle
import json
import re

from sklearn import tree
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
import pydotplus
from sklearn.externals.six import StringIO

from skopt import gp_minimize
from nysol.mining.model import ClassificationPredicted

class ctree(object):
	def __init__(self,x_df,y_df,config):
		if len(y_df.columns)!=1:
			raise BaseException("##ERROR: DataFrame of y variable must be one column data")

		self.config=config

		self.yName=y_df.columns[0]
		classDist=y_df[self.yName].value_counts().to_dict()
		# print(classDist)
		# {'-': 373, '+': 305}
		self.labels=sorted([c for c in classDist.keys()])
		# ['+', '-']

		# オリジナルクラス値を0/1に変換 => cross validationでのみ利用(文字型のクラスを受け付けないので)
		str2num={c:i for i,c in enumerate(self.labels)}
		# print(str2num)
		# {'+': 0, '-': 1}
		self.y01=np.array([str2num[v] for v in y_df[self.yName].values])
		self.y=y_df.values.reshape((-1,))

		self.xNames=x_df.columns.to_list()
		self.x=x_df.values.reshape((-1,len(x_df.columns)))

		self.tree_chart=None

		# クラスサイズ最小値が10以下ならcross validationできないことを判定させるため=>build()の最初で利用
		self.y_minClassSize=min(classDist.values())

	def objectiveFunction(self,spaces):
		params=self.config
		params["min_samples_leaf"]=spaces[0]
		clf=tree.DecisionTreeClassifier(**params)

		#skFold=KFold(n_splits=10,random_state=11)
		skFold=StratifiedKFold(n_splits=10,random_state=11)

		#print(cross_val_score(clf, self.x, self.y, cv=skFold, scoring='neg_mean_squared_error'))
		score=np.mean(cross_val_score(clf, self.x, self.y01, cv=skFold, scoring='neg_mean_squared_error'))*(-1)
		print("space",spaces[0],score)
		return score

	def build(self):
		params=self.config
		#print("params",params)

		self.cv_minFun=None
		self.cv_minX=None
		#print(self.y_minClassSize)
		#print(params["min_samples_leaf"])
		#if self.y_minClassSize>=10 and not "min_samples_leaf" in params and params["min_samples_leaf"]==0.0:
		if self.y_minClassSize>=10 and params["min_samples_leaf"]==0.0:
			if False:
				grid_param ={'min_samples_leaf':[i/100 for i in range(1,50,5)]}

				clf=tree.DecisionTreeClassifier(**params)
				grid_search = GridSearchCV(clf, param_grid=grid_param, cv=10, scoring='neg_mean_squared_error',verbose = 2)
				grid_search.fit(self.x,self.y01)
				params["min_samples_leaf"]=grid_search.best_params_['min_samples_leaf']
				print("opt","%f,%f"%(grid_search.best_params_['min_samples_leaf'],grid_search.best_score_))
			else:
				# ベイズ最適化による最適min_samples_leafの探索(CVによる推定)
				spaces = [(0.0001,0.5, 'uniform')] # min_samples_leafの最大は0.5
				res = gp_minimize(self.objectiveFunction, spaces, n_calls=15, random_state=11)
				self.cv_minFun=res.fun # 最小の目的関数値
				self.cv_minX=res.x[0] # 最適パラメータ(枝刈り度)
				#print(res) # 目的関数値
				#print(minFun,minX) # 目的関数値
				#print(res.x) # min_impurity_decrease 最適値
				#exit()	
				# 最適枝刈り度のセット
				params["min_samples_leaf"]=self.cv_minX
				print("opt","%f,%f"%(self.cv_minX,self.cv_minFun))
		elif self.y_minClassSize<10:
			del params["min_samples_leaf"]
		self.model=tree.DecisionTreeClassifier(**params)
		self.model.fit(self.x, self.y)
		#print(dir(self.model))

		self.score=self.model.score(self.x, self.y)
		#print("m accuracy",self.score)

	def predict(self,x_df):
		pred=ClassificationPredicted()
		x=x_df.values.reshape((-1,len(x_df.columns)))

		# 以下の各処理では、例外なく0.0/1.0のクラス値は元のクラス名に戻してやる
		pred.y_pred=self.model.predict(x)
		pred.y_prob=self.model.predict_proba(x)
		pred.probClassOrder=self.model.classes_ # y_probの出力順
		pred.id=x_df.index.to_list()
		pred.labels=self.labels
		return pred

	def load(iFile):
		with open(iFile, 'rb') as fpr:
			model = pickle.load(fpr)
		return model

	def save(self,oPath):
		os.makedirs(oPath,exist_ok=True)
		oFile="%s/model.sav"%(oPath)
		with open(oFile, 'wb') as fpw:
			pickle.dump(self, fpw)

		with open("%s/tree.txt"%(oPath),"bw") as f:
			f.write(self.tree_text.encode("utf-8"))

		if self.tree_chart:
			self.tree_chart.write_png("%s/tree.png"%(oPath))
			#self.tree_chart.write_pdf("%s/tree.pdf"%(oPath))

	def visualize(self):#,oFile,features=None,classes=None):
		classes=[str(v) for v in self.model.classes_] # y_probの出力順

		# image
		dot_data = StringIO()
		#tree.export_graphviz(self.model, out_file=dot_data,feature_names=self.xNames)
		dot=tree.export_graphviz(self.model,feature_names=self.xNames,class_names=classes)

		# dot フォーマット強制変換
		#あとで項目名対応する or　treeのメソッドを実装
		newdot=[]
		pre_pattern = r'^[0-9]* \[label="'
		suf_pattern = r'"] ;$'
		for line in dot.split('\n'):
			if re.match(pre_pattern , line):
				lbl = re.sub(suf_pattern , '' ,re.sub(pre_pattern,'',line))
				lbldata = lbl.split("\\n")
				if len(lbldata) == 5:
					lblval=lbldata[0].split(' ')
					lblval0 = lblval[0].split("_")
					if len(lblval0) > 1:
						if lblval[-2] == "<=":
							nn = "_".join(lblval0[0:-1])							
							newlable = 'label="%s == %s\\\\n%s\\\\n%s\\\\n%s\\\\n%s"] ;'%(nn,lblval0[-1],lbldata[1],lbldata[2],lbldata[3],lbldata[4])
							newdot.append(re.sub(r'label=".*"] ;',newlable,line))

						else:
							nn = "_".join(lblval0[0:-1])							
							newlable = 'label="%s != %s\\\\n%s\\\\n%s\\\\n%s\\\\n%s"] ;'%(nn,lblval0[-1],lbldata[1],lbldata[2],lbldata[3],lbldata[4])
							newdot.append(re.sub(r'label=".*"] ;',newlable,line))
					else:
						newdot.append(line)

				else:
					newdot.append(line)

			else:
				newdot.append(line)

		newdotstr = '\n'.join(newdot)
		self.tree_chart=pydotplus.graph_from_dot_data(newdotstr)

		# text
		self.tree_text=tree.export_text(self.model,feature_names=self.xNames,show_weights=True)

if __name__ == '__main__':
	import dataset as ds

	configFile="./config/crx2.dsc"
	crx=ds.mkTable(configFile,"./data/crx2.csv")
	#ds.show(crx)

	crx=crx.dropna()
	crx_y=ds.cut(crx,["class"])
	crx_x=ds.cut(crx,["class"],reverse=True)

	config={"max_depth": 10}
	model=ctree(crx_x,crx_y,config)
	model.build()
	print("cv_minFunc",model.cv_minFun)
	print("cv_minX",model.cv_minX)
	print("score",model.score)
	model.visualize()
	model.save("xxctree_model_crx")

	pred=model.predict(crx_x)
	pred.evaluate(crx_y)
	pred.save("xxctree_pred_crx")
	#print(pred.y_pred)
	#print(pred.y_prob)

	model=None
	model=ctree.load("xxctree_model_crx/model.sav")
	pred=model.predict(crx_x)
	pred.save("xxctree_pred_crx2")


	from sklearn.datasets import load_iris
	iris = load_iris()
	print(iris.data)
	print(iris.target)

	config={}
	config["type"]="table"
	config["names"]=["sepal length","sepal width","petal length","petal width"]
	config["convs"]=["numeric()","numeric()","numeric()","numeric()"]
	iris_x=ds.mkTable(config,iris.data)
	ds.show(iris_x)

	config={}
	config["type"]="table"
	config["names"]=["species"]
	config["convs"]=["category()"]
	iris_y=ds.mkTable(config,iris.target)
	ds.show(iris_y)

	config={"max_depth": 10}
	model=ctree(iris_x,iris_y,config)

	#print(tbl.__class__.__name__)
	model.build()
	model.visualize()
	model.save("xxctree_model_iris")

	pred=model.predict(iris_x) # ClassificationPredicted class
	#print(pred.y_prob[0],pred.y_pred[0])
	pred.evaluate(iris_y)
	pred.save("xxctree_pred_iris")
	#print(pred.y_pred)
	#print(pred.y_prob)

	model=None
	model=ctree.load("xxctree_model_iris/model.sav")
	pred=model.predict(iris_x)
	pred.save("xxctree_pred_iris2")
	print(model.labels)


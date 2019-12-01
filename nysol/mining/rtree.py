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
#from sklearn.model_selection import KFold
#from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
import pydotplus
from sklearn.externals.six import StringIO
from skopt import gp_minimize
from nysol.mining.model import RegressionPredicted

class rtree(object):
	def __init__(self,x_df,y_df,config):
		if len(y_df.columns)!=1:
			raise BaseException("##ERROR: DataFrame of y variable must be one column data")
		self.config=config

		self.yName=y_df.columns[0]
		self.y=y_df.values.reshape((-1,))

		self.xNames=x_df.columns.to_list()
		self.x=x_df.values.reshape((-1,len(x_df.columns)))

		self.tree_chart=None

		self.opt_hyper_parameter=None

	def objectiveFunction(self,spaces):
		params=self.config
		params["min_samples_leaf"]=spaces[0]
		regr=tree.DecisionTreeRegressor(**params)

		#print(clf.get_params())
		skFold=KFold(n_splits=10,random_state=11)

		return np.mean(cross_val_score(regr, self.x, self.y, cv=skFold, scoring='neg_mean_squared_error'))
		#return np.mean(cross_val_score(regr, self.x, self.y, cv=skFold, scoring='neg_mean_absolute_error'))
		#scores = cross_validation.cross_val_score(regr, X_digits, Y_digits, scoring='mean_squared_error', cv=loo,)

	def build(self):
		params=self.config
		# ベイズ最適化による最適min_samples_leafの探索(CVによる推定)
		self.cv_minFun=None
		self.cv_minX=None
		if len(self.y)>=10 and not "min_samples_leaf" in params:
			#parameters = {'min_impurity_decrease':list(np.arange(0.0,0.1,0.01))}
			# ベイズ最適化による最適min_impurity_decreaseの探索(CVによる推定)
			spaces = [(0.001,0.3, 'uniform')]
			res = gp_minimize(self.objectiveFunction, spaces, n_calls=15, random_state=11)
			self.cv_minFun=res.fun # 最小の目的関数値
			self.cv_minX=res.x[0] # 最適パラメータ(枝刈り度)
			#print(res) # 目的関数値
			#print(minFun,minX) # 目的関数値
			#print(res.x) # min_impurity_decrease 最適値
			#exit()	
			# 最適枝刈り度のセット
			params["min_samples_leaf"]=self.cv_minX

		self.model=tree.DecisionTreeRegressor(**params)
		self.model.fit(self.x, self.y)
		self.score=self.model.score(self.x, self.y)

	def predict(self,x_df):
		pred=RegressionPredicted()
		x=x_df.values.reshape((-1,len(x_df.columns)))

		pred.y_pred=self.model.predict(x)
		pred.id=x_df.index.to_list()
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
			#self.tree_chart.write_png("%s/tree.png"%(oPath))
			self.tree_chart.write_pdf("%s/tree.pdf"%(oPath))

	def visualize(self):
		classes=None

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

	config={}
	config["type"]="table"
	["Sex","Length","Diameter","Height","Whole","Shucked","Viscera","Shell","Rings","id"]

	config["names"]=["Sex","Length","Diameter","Height","Whole","Shucked","Viscera","Shell","Rings","id"]
	config["convs"]=["dummy()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()"]
	aba=ds.mkTable(config,"./data/abalone.csv")
	aba_y=ds.cut(aba,["Rings"])
	aba_x=ds.cut(aba,["Rings"],reverse=True)
	ds.show(aba_x)
	ds.show(aba_y)

	config={"max_depth": 10}
	#config["min_samples_leaf"]=100 # 指定すればCVなし
	model=rtree(aba_x,aba_y,config)
	model.build()
	model.visualize()
	model.save("xxrtree_model_aba")

	pred=model.predict(aba_x) # ClassificationPredicted class
	pred.evaluate(aba_y)
	pred.save("xxrtree_pred_aba")

	model=None
	model=rtree.load("xxrtree_model_aba/model.sav")
	pred=model.predict(aba_x)
	pred.save("xxrtree_pred2_aba")
	

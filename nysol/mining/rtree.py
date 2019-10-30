#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

from sklearn import tree
#from sklearn.model_selection import KFold
#from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

#import sklearn
#print(sklearn.metrics.SCORERS.keys())
#exit()

import warnings
warnings.filterwarnings('ignore')
from skopt import gp_minimize

class rtree(object):
	def __init__(self,config):
		self.config=config
		self.min_impurity_decrease=None
		pass

	# https://own-search-and-study.xyz/2016/12/25/scikit-learn%E3%81%A7%E5%AD%A6%E7%BF%92%E3%81%97%E3%81%9F%E6%B1%BA%E5%AE%9A%E6%9C%A8%E6%A7%8B%E9%80%A0%E3%81%AE%E5%8F%96%E5%BE%97%E6%96%B9%E6%B3%95%E3%81%BE%E3%81%A8%E3%82%81/
	def setDataset(self,x,y):
		self.x=x
		self.y=y

	def objectiveImpurity(self,spaces):
		params=self.config
		#params["min_impurity_decrease"]=spaces[0]
		params["min_samples_leaf"]=spaces[0]
		regr=tree.DecisionTreeRegressor(**params)

		#print(clf.get_params())
		skFold=KFold(n_splits=10,random_state=11)
		# dict_keys(['explained_variance', 'r2', 'max_error', 'neg_median_absolute_error', 'neg_mean_absolute_error', 'neg_mean_squared_error', 'neg_mean_squared_log_error', 'accuracy', 'roc_auc', 'balanced_accuracy', 'average_precision', 'neg_log_loss', 'brier_score_loss', 'adjusted_rand_score', 'homogeneity_score', 'completeness_score', 'v_measure_score', 'mutual_info_score', 'adjusted_mutual_info_score', 'normalized_mutual_info_score', 'fowlkes_mallows_score', 'precision', 'precision_macro', 'precision_micro', 'precision_samples', 'precision_weighted', 'recall', 'recall_macro', 'recall_micro', 'recall_samples', 'recall_weighted', 'f1', 'f1_macro', 'f1_micro', 'f1_samples', 'f1_weighted', 'jaccard', 'jaccard_macro', 'jaccard_micro', 'jaccard_samples', 'jaccard_weighted'])

		return np.mean(cross_val_score(regr, self.x, self.y, cv=skFold, scoring='neg_mean_squared_error'))
		#return np.mean(cross_val_score(regr, self.x, self.y, cv=skFold, scoring='neg_mean_absolute_error'))
		#scores = cross_validation.cross_val_score(regr, X_digits, Y_digits, scoring='mean_squared_error', cv=loo,)


	def build(self):
		#parameters = {'min_impurity_decrease':list(np.arange(0.0,0.1,0.01))}

		# ベイズ最適化による最適min_impurity_decreaseの探索(CVによる推定)
		spaces = [(0,0.3, 'uniform')]
		#res = gp_minimize(self.objectiveImpurity, spaces, acq_func="EI", n_calls=10, random_state=11)
		res = gp_minimize(self.objectiveImpurity, spaces, n_calls=10, random_state=11)
		#print(res.fun) # 目的関数値(accuracy*(-1))
		print(res.x) # min_impurity_decrease 最適値

		# モデル構築
		params=self.config
		#params["min_impurity_decrease"]=res.x[0]
		params["min_samples_leaf"]=res.x[0]
		self.min_impurity_decrease = res.x[0] # << 変数名変える


		self.model=tree.DecisionTreeRegressor(**params)
		self.model.fit(self.x, self.y)
		#print(dir(self.model))
		self.score=self.model.score(self.x, self.y)

	def pbuild(self,min_impurity_decrease):
		params=self.config

		if min_impurity_decrease != None:
			params["min_samples_leaf"]=min_impurity_decrease

		self.model=tree.DecisionTreeRegressor(**params)
		self.model.fit(self.x, self.y)

		self.score=self.model.score(self.x, self.y)
		print("pbuild")
		print(self.score)


	def vizModel(self,oFile,features=None,classes=None):
		import pydotplus
		from sklearn.externals.six import StringIO
		dot_data = StringIO()

		#print(self.y)
		
		tree.export_graphviz(self.model, out_file=dot_data,feature_names=features)

		dot=tree.export_graphviz(self.model,feature_names=features,class_names=classes)
		newdot=[]
		import re
		pre_pattern = r'^[0-9]* \[label="'
		suf_pattern = r'"] ;$'
		for line in dot.split('\n'):
			if re.match(pre_pattern , line):
				lbl = re.sub(suf_pattern , '' ,re.sub(pre_pattern,'',line))
				lbldata = lbl.split("\\n")
				if len(lbldata) == 4:
					lblval=lbldata[0].split(' ')
					lblval0 = lblval[0].split("_")
					if len(lblval0) > 1:
						if lblval[-2] == "<=":
							#項目名対応する
							nn = "_".join(lblval0[0:-1])							
							newlable = 'label="%s == %s\\\\n%s\\\\n%s\\\\n%s"] ;'%(nn,lblval0[-1],lbldata[1],lbldata[2],lbldata[3])
							newdot.append(re.sub(r'label=".*"] ;',newlable,line))

						else:
							nn = "_".join(lblval0[0:-1])							
							newlable = 'label="%s != %s\\\\n%s\\\\n%s\\\\n%s"] ;'%(nn,lblval0[-1],lbldata[1],lbldata[2],lbldata[3])
							newdot.append(re.sub(r'label=".*"] ;',newlable,line))
					else:
						newdot.append(line)

				else:
					newdot.append(line)

			else:
				newdot.append(line)

		newdotstr = '\n'.join(newdot)

		#graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
		graph = pydotplus.graph_from_dot_data(newdotstr)
		graph.write_pdf(oFile)
		print(tree.export_text(self.model,feature_names=features))

if __name__ == '__main__':
	import importlib
	from dataset import dataset
	configFile=os.path.expanduser(sys.argv[1])
	sys.path.append(os.path.dirname(configFile))

	config=importlib.import_module(os.path.basename(configFile).replace(".py",""))
	print(config.dataset)

	ds=dataset(config.dataset)
	print(ds)
	x=ds.nums
	# category変数
	for cat in ds.cats:
		x=np.hstack((x,cat.data))

	model=rtree(config.rTree)
	model.setDataset(x,ds.y)
	model.build()
	model.vizModel("graph.pdf")


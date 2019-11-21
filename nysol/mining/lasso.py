#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV,Lasso


from sklearn import tree
#from sklearn.model_selection import KFold
#from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold

import warnings
warnings.filterwarnings('ignore')
from skopt import gp_minimize

class lasso(object):
	def __init__(self,config):
		self.config=config

	# https://own-search-and-study.xyz/2016/12/25/scikit-learn%E3%81%A7%E5%AD%A6%E7%BF%92%E3%81%97%E3%81%9F%E6%B1%BA%E5%AE%9A%E6%9C%A8%E6%A7%8B%E9%80%A0%E3%81%AE%E5%8F%96%E5%BE%97%E6%96%B9%E6%B3%95%E3%81%BE%E3%81%A8%E3%82%81/
	def setDataset(self,x,y):
		self.x=x
		self.y=y

	def build(self):
		print(self.config)
		# CVによる最適α(いわゆるλ)の推定
		scaler = StandardScaler()
		scaler.fit(self.x)
		cvm = LassoCV(alphas=10 ** np.arange(-6, 1, 0.1), cv=5)
		cvm.fit(scaler.transform(self.x), self.y)
		print(cvm.alpha_)
		print(cvm.coef_)
		print(cvm.intercept_)

		# モデル構築
		scaler = StandardScaler()
		scaler.fit(self.x)
		self.model = Lasso(alpha=cvm.alpha_)
		self.model.fit(scaler.transform(self.x), self.y)
		print(self.model.coef_)
		print(self.model.intercept_)

		'''
		parameters = {'min_impurity_decrease':list(np.arange(0.0,0.1,0.01))}

		# ベイズ最適化による最適min_impurity_decreaseの探索(CVによる推定)
		spaces = [(0.0,0.1, 'uniform')]
		#res = gp_minimize(self.objectiveImpurity, spaces, acq_func="EI", n_calls=10, random_state=11)
		res = gp_minimize(self.objectiveImpurity, spaces, n_calls=10, random_state=11)
		#print(res.fun) # 目的関数値(accuracy*(-1))
		#print(res.x) # min_impurity_decrease 最適値

		# モデル構築
		params=self.config
		params["min_impurity_decrease"]=res.x[0]
		self.model=tree.DecisionTreeClassifier(**params)
		self.model.fit(self.x, self.y)
		#print(dir(self.model))
		self.score=self.model.score(self.x, self.y)
'''
	def vizModel(self,oFile):
		import pydotplus
		from sklearn.externals.six import StringIO
		dot_data = StringIO()
		tree.export_graphviz(self.model, out_file=dot_data)
		graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
		graph.write_pdf(oFile)

if __name__ == '__main__':
	import importlib
	from dataset import dataset
	configFile=os.path.expanduser(sys.argv[1])
	sys.path.append(os.path.dirname(configFile))
	config=importlib.import_module(os.path.basename(configFile).replace(".py",""))

	ds=dataset(config.dataset)
	ds._summary()
	x=ds.nums
	# category変数
	for cat in ds.cats:
		x=np.hstack((x,cat.data))

	model=lasso(config.dTree)
	model.setDataset(x,ds.y)
	model.build()
	#model.vizModel("graph.pdf")


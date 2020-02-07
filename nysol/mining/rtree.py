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
import time
import pandas as pd

from sklearn import tree
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
import pydotplus
from sklearn.externals.six import StringIO
from skopt import gp_minimize
from nysol.mining.rPredict import rPredict

class rtree(object):
	def __init__(self,x_df=None,y_df=None):
		if x_df is not None and y_df is not None:
			self.setDataset(x_df,y_df)

		self.tree_chart=None
		self.opt_hyper_parameter=None

	def setDataset(self,x_df,y_df):
		print("##MSG: setting dataset ...")
		if len(y_df.columns)!=1:
			raise BaseException("##ERROR: DataFrame of y variable must be one column data")
		# nullデータチェック
		for i,isnull in enumerate(x_df.isnull().any()):
			if isnull:
				raise BaseException("##ERROR: null data found in field '%s'"%(x_df.columns[i]))
		for i,isnull in enumerate(y_df.isnull().any()):
			if isnull:
				raise BaseException("##ERROR: null data found in field '%s'"%(y_df.columns[i]))

		self.yName=y_df.columns[0]
		self.y=y_df.values.reshape((-1,))

		self.xNames=x_df.columns.to_list()
		self.x=x_df.values.reshape((-1,len(x_df.columns)))

	def objectiveFunction(self,spaces):
		params=self.params
		params["min_samples_leaf"]=spaces[0]
		regr=tree.DecisionTreeRegressor(**params)

		#print(clf.get_params())
		skFold=KFold(n_splits=10,random_state=11)

		score=np.mean(cross_val_score(regr, self.x, self.y, cv=skFold, scoring='neg_mean_squared_error'))*(-1)
		print("space",spaces[0],score)
		return score
		#return np.mean(cross_val_score(regr, self.x, self.y, cv=skFold, scoring='neg_mean_absolute_error'))
		#scores = cross_validation.cross_val_score(regr, X_digits, Y_digits, scoring='mean_squared_error', cv=loo,)

	def build(self,params,opt_param=None,visualizing=True):
		print("##MSG: building model ...")
		if opt_param is not None:
			params["min_samples_leaf"]=opt_param
		if "min_samples_leaf" not in params:
			params["min_samples_leaf"]=0.0
		self.params=params

		self.cv_minFun=None
		self.cv_minX=None
		if len(self.y)>=10 and params["min_samples_leaf"]==0.0:
			if True:
				grid_param ={'min_samples_leaf':[i/100 for i in range(1,50,1)]}

				clf=tree.DecisionTreeRegressor(**params)
				grid_search = GridSearchCV(clf, param_grid=grid_param, cv=10, scoring='neg_mean_squared_error',verbose = 0)
				grid_search.fit(self.x,self.y)
				params["min_samples_leaf"]=grid_search.best_params_['min_samples_leaf']
				#print("opt","%f,%f"%(grid_search.best_params_['min_samples_leaf'],grid_search.best_score_))
			else:	
				#parameters = {'min_impurity_decrease':list(np.arange(0.0,0.1,0.01))}
				# ベイズ最適化による最適min_impurity_decreaseの探索(CVによる推定)
				spaces = [(0.01,0.5, 'uniform')]
				res = gp_minimize(self.objectiveFunction, spaces, n_calls=20, random_state=11)
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
		self.opt_param=params["min_samples_leaf"]

		if visualizing:
			self.visualize()

	def predict(self,x_df):
		print("##MSG: predicting ...")
		x=x_df.values.reshape((-1,len(x_df.columns)))

		y_pred=self.model.predict(x)
		y_pred=pd.DataFrame(y_pred)
		y_pred.index=x_df.index.to_list()

		pred=rPredict(y_pred)
		return pred

	def load(modelF):
		print("##MSG: loading model ...")
		with open(modelF, 'rb') as fpr:
			model = pickle.load(fpr)
		return model

	def save(self,oPath):
		print("##MSG: saving model ...")
		os.makedirs(oPath,exist_ok=True)
		oFile="%s/model.sav"%(oPath)
		with open(oFile, 'wb') as fpw:
			pickle.dump(self, fpw)

		with open("%s/tree.txt"%(oPath),"bw") as f:
			f.write(self.tree_text.encode("utf-8"))

		if self.tree_chart:
			self.tree_chart.write_svg("%s/tree.svg"%(oPath))

	def visualize(self):
		print("##MSG: visualizing ...")
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
	def senario1():
		st=time.time()
		config={}
		config["type"]="table"
		header="101,102,103,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,124,126,127,128,129,150,151,152,153,154,155,160,161,162,163,164,171,172,173,191,192,193,194,195,196,197,200,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,201,2010,2011,2012,2013,2014,2016,2017,2018,2019,202,2020,2021,2022,2024,203,210,211,2110,2140,2142,2150,2151,2152,2160,2161,2162,2163,2164,2165,2167,2168,2169,2170,2171,2172,2173,2174,2175,2176,2180,2181,2182,2183,2184,2185,2186,2187,2188,2189,2190,2191,2192,2193,2194,2195,2198,2199,220,221,222,230,231,232,233,234,235,236,237,240,241,242,243,244,245,251,252,253,260,261,262,264,266,268,270,271,272,273,274,275,280,282,284,286,288,290,292,294,296,297,300,3001,3002,3003,3004,3005,3008,3009,3013,3014,3018,3019,3023,310,311,312,313,3147,3148,3149,320,321,322,323,324,325,326,327,330,331,332,333,334,335,340,341,342,344,345,350,351,352,353,355,360,361,362,363,370,371,372,401,402,403,405,406,407,408,4199,4201,4202,4203,4204,4205,4206,4210,4211,4212,4213,4214,4215,4216,4217,4218,4219,4220,4221,4222,4223,4224,4225,4226,4227,4230,4231,503,5124,5126,5127,5128,5129,5130,5131,5132,5133,5134,5135,5136,5137,5138,5139,5140,5141,5142,5143,5144,5146,5147,5148,5149,5150,5151,5152,5153,5154,5155,5156,533,534,538,539,540,541,543,544,545,548,549,553,567,568,575,576,577,578,579,580,581,582,583,584,585,586,588,618,619,621,622,625,626,627"
		config["vars"]=[]
		for name in header.split(","):
			config["vars"].append([name,"numeric",{}])
		config["vars"].append(["金額","numeric",{}])

		data=ds.mkTable(config,"./test.csv")
		y=ds.cut(data,["金額"])
		x=ds.cut(data,["金額"],reverse=True)
		#ds.show(x)
		#ds.show(y)

		model=rtree(x,y)
		params={"max_depth": 10}
		model.build(params)
		model.save("xxrtree_model_yaki")

		pred=model.predict(x)
		#print(pred.y_pred)
		pred.evaluate(y)
		#print(pred.y_true)
		#print(pred.y)
		#print(pred.stats)
		#print(pred.charts)
		#pred.charts["true_pred_scatter"].savefig("xxa.png")
		#pred.charts["true_pred_scatter"]
		#plt.show()
		pred.save("xxrtree_pred_yaki")

		# 作成したmodelを読み込んでの予測
		model=rtree.load("xxrtree_model_yaki/model.sav")
		#print("time8=",time.time()-st)
		pred=model.predict(x)
		#print(pred)
		pred.evaluate(y)
		#print("tim9=",time.time()-st)
		pred.save("xxrtree_pred2_yaki")
		#print("timea=",time.time()-st)
	
	def abalone():
		config={}
		config["type"]="table"
		config["vars"]=[
			["Sex"     ,"dummy",{"drop_first":True,"dummy_na":False,"dtype":float}],
			["Length"  ,"numeric",{}],
			["Diameter","numeric",{}],
			["Height"  ,"numeric",{}],
			["Whole"   ,"numeric",{}],
			["Shucked" ,"numeric",{}],
			["Viscera" ,"numeric",{}],
			["Shell"   ,"numeric",{}],
			["Rings"   ,"numeric",{}],
			["id"      ,"id",{}]
		]
		data=ds.mkTable(config,"./data/abalone.csv")
		y=ds.cut(data,["Rings"])
		x=ds.cut(data,["Rings"],reverse=True)
		ds.show(x)
		ds.show(y)

		model=rtree(x,y)
		params={"max_depth": 10}
		model.build(params)
		model.save("xxrtree_model_abalone")

		pred=model.predict(x)
		#print(pred.y_pred)
		pred.evaluate(y)
		#print(pred.y_true)
		#print(pred.y)
		#print(pred.stats)
		#print(pred.charts)
		#pred.charts["true_pred_scatter"].savefig("xxa.png")
		#pred.charts["true_pred_scatter"]
		#plt.show()
		pred.save("xxrtree_pred_abalone")

		# 作成したmodelを読み込んでの予測
		model=rtree.load("xxrtree_model_abalone/model.sav")
		#print("time8=",time.time()-st)
		pred=model.predict(x)
		#print(pred)
		pred.evaluate(y)
		#print("tim9=",time.time()-st)
		pred.save("xxrtree_pred2_abalone")
		#print("timea=",time.time()-st)
	
	#senario1()
	abalone()


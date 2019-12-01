#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pickle
import json

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV,Lasso
from sklearn.linear_model import LogisticRegressionCV,LogisticRegression
from matplotlib import pyplot as plt
from sklearn.multiclass import OneVsRestClassifier
import scipy

#from sklearn.metrics import confusion_matrix
#from sklearn.metrics import accuracy_score
#from sklearn.metrics import precision_score
#from sklearn.metrics import recall_score
import sklearn.metrics as metrics

from sklearn import tree
#from sklearn.model_selection import KFold
#from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold

import warnings
warnings.filterwarnings('ignore')
from skopt import gp_minimize
#from model import ClassificationModel
from nysol.mining.model import ClassificationPredicted

import model

class classo(object):
	def __init__(self,x_df,y_df):
		if len(y_df.columns)!=1:
			raise BaseException("##ERROR: DataFrame of y variable must be one column data")

		self.yName=y_df.columns[0]
		self.labels=y_df[self.yName].cat.categories.to_list()
		self.y=y_df.values.reshape((-1,))

		self.xNames=x_df.columns.to_list()
		self.x=x_df.values.reshape((-1,len(x_df.columns)))

		self.mse_chart=None
		self.coef_chart=None

	def build(self,penalty="l1",cv=10,Cs=40):
		self.penalty=penalty
		self.cv=cv
		self.Cs=Cs

		# xの標準化
		self.scaler = StandardScaler()
		self.scaler.fit(self.x)
		x_trans=self.scaler.transform(self.x)

		# https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html#sklearn.linear_model.LogisticRegressionCV
		self.model = LogisticRegressionCV(penalty=self.penalty,cv=self.cv,Cs=self.Cs,solver="saga",random_state=0, multi_class='multinomial')
		self.model.fit(x_trans, self.y)
		self.score=self.model.score(x_trans, self.y)
		#print(self.model.coef_)
		#print(self.model.intercept_)
		#print(self.model.predict(self.x_trans))
		#print(self.y)

		# 回帰係数
		self.coef=[]
		self.coef.append(["class","x","coef"])
		if len(self.labels)==2:
			cnos=[0]
		else:
			cnos=range(len(self.labels))
		for c in cnos:
			self.coef.append([str(self.labels[c]),"intercept",float(self.model.intercept_[c])])
			for i in range(len(self.xNames)):
				self.coef.append([str(self.labels[c]),self.xNames[i],float(self.model.coef_[c][i])])

		# 最適λ
		self.opt_lambda=[]
		self.opt_lambda.append(["class","lambda"])
		for c in cnos:
			self.opt_lambda.append([str(self.labels[c]),float(self.model.C_[c])])

	def predict(self,x_df):
		pred=ClassificationPredicted()
		x=x_df.values.reshape((-1,len(x_df.columns)))
		x_trans=self.scaler.transform(x)

		pred.y_pred=self.model.predict(x_trans)
		pred.y_prob=self.model.predict_proba(x_trans)
		pred.probClassOrder=self.model.classes_ # y_probの出力順
		pred.id=x_df.index.to_list()
		pred.labels=self.labels

		''' # predict_probabの検算
		d=x_trans[0]
		c=self.model.coef_[0]
		b=self.model.intercept_[0]
		a=np.sum(d*c)+b
		#a=np.dot(d,c.T)+b
		aa=np.c_[-a, a]
		print(scipy.special.softmax(aa))
		'''
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

		json_dump = json.dumps(self.coef, ensure_ascii=False, indent=2)
		with open("%s/coef.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

		json_dump = json.dumps(self.opt_lambda, ensure_ascii=False, indent=2)
		with open("%s/opt_lambda.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

		if self.mse_chart:
			self.mse_chart.savefig("%s/mse.png"%(oPath))
		if self.coef_chart:
			self.coef_chart.savefig("%s/coef.png"%(oPath))

	def visualize(self):
		##### visualization
		m_log_alphas = self.model.Cs_ # lambda path (x axis)

		# MSE path chart
		clsSize=len(self.model.scores_)
		#print(clsSize)
		fig, axs = plt.subplots(nrows=clsSize, figsize=(10,6*clsSize))
		if axs.__class__.__name__=="AxesSubplot": # binary classの場合はここに引っかかる
			axs=[axs]

		i=0
		for key,scores in self.model.scores_.items():
			#print(key,scores.shape)
			#print(key,scores.mean(axis=0).shape)
			#print(i)
			#axs[i] = plt.gca()
			axs[i].plot(m_log_alphas, scores.mean(axis=0), linewidth=2)
			axs[i].errorbar(m_log_alphas, scores.mean(axis=0), yerr = scores.std(axis=0), capsize=2, fmt='o', markersize=1, ecolor='black', markeredgecolor = "black", color='w')
			axs[i].set_xscale('log') # set_xlimより前に実行must
			axs[i].set_xlim(axs[i].get_xlim()[::-1])  # reverse axis
			axs[i].set_title('Mean square error: class='+str(key))
			axs[i].set_xlabel('-log(alpha)')
			i+=1
		self.mse_chart=fig

		# coefficient path chart
		coefs=[]
		for c in reversed(self.model.Cs_):
			model = LogisticRegression(penalty=self.penalty,C=c, solver="saga",random_state=0, multi_class='multinomial')
			model.fit(self.scaler.transform(self.x), self.y)
			coefs.append(model.coef_[0])
		#print("coef.shape",coefs[0].shape)
		#print("alpha.shape",m_log_alphas.shape)

		fig=plt.figure()
		ax = plt.gca()
		ax.plot(m_log_alphas, coefs)
		ax.set_xscale('log')
		ax.set_xlim(ax.get_xlim()[::-1])  # reverse axis
		plt.xlabel('-log(alpha)')
		plt.ylabel('weights')
		plt.title('Lasso coefficients as a function of the regularization')
		plt.axis('tight')
		self.coef_chart=fig

if __name__ == '__main__':
	import dataset as ds

	#'''
	configFile="./config/crx2.dsc"
	tbl=ds.mkTable(configFile,"./data/crx2.csv")
	#ds.show(tbl)

	configFile="config/crx_tra.dsc"
	tra=ds.mkTable(configFile,"data/crx_tra1.csv")
	#ds.show(tra)
	tratbl=ds.tra2tbl(tra,"id","item")
	#ds.show(tratbl)

	crx=ds.join([tbl,tratbl])
	#ds.show(crx)

	crx=crx.dropna()
	crx_y=ds.cut(crx,["class"])
	crx_x=ds.cut(crx,["class"],reverse=True)

	model=classo(crx_x,crx_y)
	model.build()
	#print(model.coef)
	#print(model.opt_lambda)
	model.visualize()
	model.save("xxclasso_model_crx")

	pred=model.predict(crx_x)
	pred.evaluate(crx_y)
	pred.save("xxclasso_pred_crx")
	#print(pred.y_pred)
	#print(pred.y_prob)

	#'''
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

	model=classo(iris_x,iris_y)

	#print(tbl.__class__.__name__)
	model.build()
	print(model.coef)
	print(model.opt_lambda)
	model.visualize()
	model.save("xxclasso_model_iris")

	pred=model.predict(iris_x) # ClassificationPredicted class
	#print(pred.y_prob[0],pred.y_pred[0])
	pred.evaluate(iris_y)
	pred.save("xxclasso_pred_iris")
	#print(pred.y_pred)
	#print(pred.y_prob)

	model=None
	model=classo.load("xxclasso_model_iris/model.sav")
	pred=model.predict(iris_x)
	pred.save("xxclasso_pred_iris2")
	print(model.labels)
	#'''

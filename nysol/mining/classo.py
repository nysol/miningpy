#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pickle
import json
import csv
import pandas as pd

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

from nysol.mining.cPredict import cPredict

class classo(object):
	def __init__(self,x_df,y_df,standardize=False):
		print("##MSG: initializing model ...")

		if len(y_df.columns)!=1:
			raise BaseException("##ERROR: DataFrame of y variable must be one column data")
		# nullデータチェック
		for i,isnull in enumerate(x_df.isnull().any()):
			if isnull:
				raise BaseException("##ERROR: null data found in field '%s'"%(x_df.columns[i]))
		for i,isnull in enumerate(y_df.isnull().any()):
			if isnull:
				raise BaseException("##ERROR: null data found in field '%s'"%(y_df.columns[i]))

		self.y_name=y_df.columns[0]
		self.labels=y_df[self.y_name].cat.categories.to_list()
		self.y=y_df.values.reshape((-1,))

		self.x_names=x_df.columns.to_list()
		self.x=x_df.values.reshape((-1,len(x_df.columns)))

		# standardize x variables
		if standardize:
			self.scaler = StandardScaler()
			self.scaler.fit(self.x)
			self.x_trans=self.scaler.transform(self.x)
		else:
			self.scaler = None
			self.x_trans=self.x

		self.mse_chart = None
		self.coef_chart= None

	def build(self,l1_ratio=1.0,cv=10,Cs=40,max_iter=100):
		print("##MSG: building model ...")
		self.penalty="elasticnet"
		self.l1_ratio=l1_ratio
		self.cv=cv
		self.Cs=Cs
		self.max_iter=max_iter
		# https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html#sklearn.linear_model.LogisticRegressionCV
		self.model = LogisticRegressionCV(penalty=self.penalty,l1_ratios=[self.l1_ratio],cv=self.cv,Cs=self.Cs,solver="saga",random_state=0, max_iter=self.max_iter,multi_class='multinomial')
		self.model.fit(self.x_trans, self.y)
		self.score=self.model.score(self.x_trans, self.y)
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
			for i in range(len(self.x_names)):
				self.coef.append([str(self.labels[c]),self.x_names[i],float(self.model.coef_[c][i])])

		# 最適λ
		self.opt_lambda=[]
		self.opt_lambda.append(["class","lambda"])
		for c in cnos:
			#self.opt_lambda.append([str(self.labels[c]),float(self.model.C_[c])])
			self.opt_lambda.append([self.labels[c],float(self.model.C_[c])])

		self.visualize()

	def predict(self,x_df):
		print("##MSG: predicting ...")
		x=x_df.values.reshape((-1,len(x_df.columns)))
		if self.scaler is None:
			x_trans=x
		else:
			x_trans=self.scaler.transform(x)

		y_pred=self.model.predict(x_trans) # [0 0 0 0 0 0 0 ...] # pred class表
		y_prob=self.model.predict_proba(x_trans) # sample * class prob 表
		# [[9.86925146e-01 1.30748490e-02 5.13506829e-09]
		#  [9.81685740e-01 1.83142489e-02 1.10697584e-08]...

		# y_prob等のclassの出力順
		orderedLabels=self.model.classes_

		# id込みのDataFrameに変換
		y_pred=pd.DataFrame(y_pred)
		y_pred.index=x_df.index.to_list()
		y_pred.columns=["y_predicted"]

		y_prob=pd.DataFrame(y_prob)
		y_prob.index=x_df.index.to_list()
		names=[]
		for c in orderedLabels:
			names.append("prob_"+str(c))
		y_prob.columns=names

		pred=cPredict(y_pred,y_prob,orderedLabels)

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

		json_dump = json.dumps(self.coef, ensure_ascii=False, indent=2)
		with open("%s/coef.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))
		with open("%s/coef.csv"%(oPath),"w") as f:
			writer = csv.writer(f)
			for row in self.coef:
				writer.writerow(row)

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
			model = LogisticRegression(penalty=self.penalty,l1_ratio=self.l1_ratio,C=c, solver="saga",random_state=0, max_iter=self.max_iter, multi_class='multinomial')

			#model.fit(self.scaler.transform(self.x), self.y)
			model.fit(self.x, self.y)
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
	def senario1():
		config={}
		config["type"]="table"
		config["vars"]=[
			["id","id",{}],
			["n1","numeric",{}],
			["n2","numeric",{}],
			["n3","numeric",{}],
			["n4","numeric",{}],
			["d1","dummy",{"dummy_na":True,"drop_first":True,"dtype":float}],
			["d2","dummy",{}],
			["d3","dummy",{}],
			["i1","dummy",{}],
			["i2","dummy",{}],
			["class","class",{}]
		]
		data=ds.mkTable(config,"./data/crx2.csv")
		data=data.dropna()
		y=ds.cut(data,["class"])
		x=ds.cut(data,["class"],reverse=True)
		ds.show(x)
		ds.show(y)

		model=classo(x,y)
		model.build()
		model.save("xxclasso_model_crx")

		pred=model.predict(x)
		pred.evaluate(y)
		#print(pred.y_pred)
		#print(pred.y_true)
		#print(pred.y)
		#print(pred.stats)
		#print(pred.charts)
		#pred.charts["true_pred_scatter"].savefig("xxa.png")
		#pred.charts["roc_chart"]
		#pred.charts["confusion_matrix_plot"]
		#plt.show()
		pred.save("xxclasso_pred_crx")

		model=classo.load("xxclasso_model_crx/model.sav")
		pred=model.predict(x)
		pred.evaluate(y)
		pred.save("xxclasso_pred_crx2")

	def iris():
		from sklearn.datasets import load_iris
		iris = load_iris()
		config={}
		config["type"]="table"
		config["vars"]=[
			["sepal length","numeric",{}],
			["sepal width" ,"numeric",{}],
			["petal lengt" ,"numeric",{}],
			["petal width" ,"numeric",{}]
		]
		x=ds.mkTable(config,iris.data)

		config={}
		config["type"]="table"
		config["vars"]=[
			["species","category",{}]
		]
		y=ds.mkTable(config,iris.target)
		ds.show(x)
		ds.show(y)

		model=classo(x,y)
		# build(self,l1_ratio=1.0,cv=10,Cs=40,max_iter=100)
		model.build(max_iter=10000)
		model.save("xxclasso_model_iris")

		pred=model.predict(x)
		pred.evaluate(y)
		pred.save("xxclasso_pred_iris")

		model=classo.load("xxclasso_model_iris/model.sav")
		pred=model.predict(x)
		pred.evaluate(y)
		pred.save("xxclasso_pred_iris2")

	senario1()
	#iris()


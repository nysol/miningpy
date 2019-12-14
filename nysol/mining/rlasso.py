#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pickle
import json
import csv

from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV,RidgeCV,Lasso,Ridge

from nysol.mining.rPredict import rPredict

class rlasso(object):
	def __init__(self,x_df,y_df):
		if len(y_df.columns)!=1:
			raise BaseException("##ERROR: DataFrame of y variable must be one column data")
		#self.config=config

		self.yName=y_df.columns[0]
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

		if penalty=="l1":
			self.model = LassoCV(cv=self.cv,n_alphas=self.Cs)
		elif penalty=="l2":
			self.model = RidgeCV(cv=self.cv)
		
		self.model.fit(x_trans, self.y)
		self.score=self.model.score(x_trans, self.y)
		#print("coef",self.model.coef_)
		#print("intercept",self.model.intercept_)
		#print(self.model.predict(x_trans))
		#print(self.y)
		#exit()
		# 回帰係数
		self.coef=[]
		self.coef.append(["x","coef"])
		self.coef.append(["intercept",float(self.model.intercept_)])
		for i in range(len(self.model.coef_)):
			self.coef.append([self.xNames[i],float(self.model.coef_[i])])

		# 最適λ
		self.opt_lambda=[]
		self.opt_lambda.append(["lambda"])
		self.opt_lambda.append([float(self.model.alpha_)])

	def predict(self,x_df):
		pred=rPredict()
		x=x_df.values.reshape((-1,len(x_df.columns)))
		x_trans=self.scaler.transform(x)

		pred.y_pred=self.model.predict(x_trans)
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

		#print(self.coef)
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
		m_log_alphas = self.model.alphas_ # lambda path (x axis)

		# MSE path chart
		scores=self.model.mse_path_
		#print(m_log_alphas.shape)
		#print(scores.mean(axis=1).shape)
		fig = plt.figure()
		ax = plt.gca()
		ax.plot(m_log_alphas, scores.mean(axis=1), linewidth=2)
		ax.errorbar(m_log_alphas, scores.mean(axis=1), yerr = scores.std(axis=1), capsize=2, fmt='o', markersize=1, ecolor='black', markeredgecolor = "black", color='w')
		ax.set_xscale('log') # set_xlimより前に実行must
		ax.set_xlim(ax.get_xlim()[::-1])  # reverse axis
		ax.set_title('Mean square error')
		ax.set_xlabel('-log(alpha)')
		self.mse_chart=fig

		# coefficient path chart
		coefs=[]
		for alpha in self.model.alphas_:
			if self.penalty=="l1":
				model = Lasso(alpha=alpha)
			elif self.penalty=="l2":
				model = Ridge(alpha=alpha)
			model.fit(self.scaler.transform(self.x), self.y)
			coefs.append(model.coef_)
			#print("coef.shape",coefs)
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

	config={}
	config["type"]="table"
	#["Sex","Length","Diameter","Height","Whole","Shucked","Viscera","Shell","Rings","id"]

	config["names"]=["Sex","Length","Diameter","Height","Whole","Shucked","Viscera","Shell","Rings","id"]
	config["convs"]=["dummy()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()"]
	aba=ds.mkTable(config,"./data/abalone.csv")
	aba_y=ds.cut(aba,["Rings"])
	aba_x=ds.cut(aba,["Rings"],reverse=True)
	ds.show(aba_x)
	ds.show(aba_y)

	model=rlasso(aba_x,aba_y)
	model.build()
	model.visualize()
	model.save("xxrlasso_model_aba")

	pred=model.predict(aba_x) # ClassificationPredicted class
	pred.evaluate(aba_y)
	pred.save("xxrlasso_pred_aba")

	model=None
	model=rlasso.load("xxrlasso_model_aba/model.sav")
	pred=model.predict(aba_x)
	pred.save("xxrlasso_pred2_aba")
	

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pickle
import json
import csv
import time
import pandas as pd

import warnings
warnings.simplefilter('ignore')

from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV,RidgeCV,Lasso,Ridge
from sklearn.linear_model import ElasticNet,ElasticNetCV

from nysol.mining.rPredict import rPredict

class rlasso(object):
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

		self.y_name =list(y_df.columns)[0]
		self.y=y_df.values.reshape((-1,))

		self.x_names=list(x_df.columns)
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

	def build(self,l1_ratio=1.0,cv=10,max_iter=100):
		print("##MSG: building model ...")
		self.l1_ratio=l1_ratio
		self.cv=cv
		self.max_iter=max_iter

		self.model = ElasticNetCV(l1_ratio=[self.l1_ratio],cv=self.cv,random_state=0, max_iter=self.max_iter)
		
		self.model.fit(self.x_trans, self.y)
		self.score=self.model.score(self.x_trans, self.y)
		#print("coef",self.model.coef_)
		#print("intercept",self.model.intercept_)
		#print(self.model.predict(self.x_trans))
		#print(self.y)
		#exit()
		# 回帰係数
		self.coef=[]
		self.coef.append(["x","coef"])
		self.coef.append(["intercept",float(self.model.intercept_)])
		for i in range(len(self.model.coef_)):
			self.coef.append([self.x_names[i],float(self.model.coef_[i])])

		# 最適λ
		self.opt_lambda=[]
		self.opt_lambda.append(["lambda"])
		self.opt_lambda.append([float(self.model.alpha_)])

		self.visualize()

	def predict(self,x_df):
		print("##MSG: predicting ...")
		x=x_df.values.reshape((-1,len(x_df.columns)))
		if self.scaler is None:
			x_trans=x
		else:
			x_trans=self.scaler.transform(x)

		y_pred=self.model.predict(x_trans)
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
		#oFile="%s/scaler.sav"%(oPath)
		#with open(oFile, 'wb') as fpw:
		#	pickle.dump(self.scaler, fpw)

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

		if self.mse_chart is not None:
			self.mse_chart.savefig("%s/mse.png"%(oPath))
		if self.coef_chart is not None:
			self.coef_chart.savefig("%s/coef.png"%(oPath))

	def visualize(self):
		print("##MSG: visualizing ...")
		##### visualization
		m_log_alphas = self.model.alphas_ # lambda path (x axis)

		# MSE path chart
		scores=self.model.mse_path_
		#print(scores)
		#print(m_log_alphas.shape)
		#print(scores.mean(axis=1))
		#print(scores.std(axis=1)/self.cv**(0.5))
		fig = plt.figure()
		ax = plt.gca()
		ax.plot(m_log_alphas, scores.mean(axis=1), linewidth=2)
		# cross-validation standard error:
		# https://www.stat.cmu.edu/~ryantibs/advmethods/notes/errval.pdf
		ax.errorbar(m_log_alphas, scores.mean(axis=1), yerr = scores.std(axis=1)/self.cv**(0.5), capsize=2, fmt='o', markersize=1, ecolor='black', markeredgecolor = "black", color='w')
		ax.set_xscale('log') # set_xlimより前に実行must
		ax.set_xlim(ax.get_xlim()[::-1])  # reverse axis
		ax.set_title('Mean square error')
		ax.set_xlabel('-log(alpha)')
		self.mse_chart=fig

		# coefficient path chart
		coefs=[]
		for alpha in self.model.alphas_:
			model = ElasticNet(alpha=alpha,l1_ratio=self.l1_ratio,random_state=0, max_iter=self.max_iter)
			model.fit(self.x_trans, self.y)
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

		model=rlasso(x,y,standardize=True)
		model.build()
		model.save("xxrlasso_model_yaki")

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
		pred.save("xxrlasso_pred_yaki")

		# 作成したmodelを読み込んでの予測
		model=rlasso.load("xxrlasso_model_yaki/model.sav")
		#print("time8=",time.time()-st)
		pred=model.predict(x)
		#print(pred)
		pred.evaluate(y)
		#print("tim9=",time.time()-st)
		pred.save("xxrlasso_pred2_yaki")
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

		# Sex,Length,Diameter,Height,Whole,Shucked,Viscera,Shell,Rings,id
		# M,0.455,0.365,0.095,0.514,0.2245,0.101,0.15,15,0
		# M,0.35,0.265,0.09,0.2255,0.0995,0.0485,0.07,7,1
		dtype={
			"Sex"     :"category",
			"Length"  :"float",
			"Diameter":"float",
			"Height"  :"float",
			"Whole"   :"float",
			"Shucked" :"float",
			"Viscera" :"float",
			"Shell"   :"float",
			"Rings"   :"float",
			"id"      :"object"
		}
		data=pd.read_csv("./data/abalone.csv",dtype=dtype)
		print(data.dtypes)

		data=pd.get_dummies(data,columns=["Sex"],drop_first=True, dummy_na=True, dtype=int)
		data=data.set_index("id")
		data=data.dropna()
		print(data)
		print(data.dtypes)
		print(data.index)
		#data=ds.mkTable(config,"./data/abalone.csv")
		y=pd.DataFrame(data["Rings"])
		x=data.drop(["Rings"],axis=1)
		#ds.show(x)
		#ds.show(y)
		print(type(y))

		model=rlasso(x,y,standardize=True)
		model.build(max_iter=10000)
		model.save("xxrlasso_model_abalone")

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
		pred.save("xxrlasso_pred_abalone")

		# 作成したmodelを読み込んでの予測
		model=rlasso.load("xxrlasso_model_abalone/model.sav")
		#print("time8=",time.time()-st)
		pred=model.predict(x)
		#print(pred)
		pred.evaluate(y)
		#print("tim9=",time.time()-st)
		pred.save("xxrlasso_pred2_abalone")
		#print("timea=",time.time()-st)
	
	#senario1()
	abalone()


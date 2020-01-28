#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pickle
import json
import csv
import time
import tempfile
import shutil

import pyper
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
#from sklearn.linear_model import LassoCV,RidgeCV,Lasso,Ridge
#from sklearn.linear_model import ElasticNet,ElasticNetCV
#from sklearn.linear_model import LassoLarsCV,LassoLars

from nysol.mining.rPredict import rPredict

class rlasso(object):
	def __init__(self,x_df=None,y_df=None,modelPath=None):
		print("##MSG: initializing model ...")
		self.tmpdir = tempfile.TemporaryDirectory()
		#print(self.tmpdir.name)
		self.rlogF=self.tmpdir.name+"/rlog.txt"
		self.r = pyper.R()
		self.r("sink(file='%s', split=T)"%(self.rlogF))
		self.r("library(glmnet)")

		if modelPath is not None:
			modelF="%s/model.robj"%(modelPath)
			self.r("load('%s')"%(modelF))

		elif x_df is not None and y_df is not None:
			if len(y_df.columns)!=1:
				raise BaseException("##ERROR: DataFrame of y variable must be one column data")

			self.x_names=list(x_df.columns)
			self.y_name =list(y_df.columns)[0]
			#print(self.x_names)
			#print(self.y_name)

			y_csv=self.tmpdir.name+"/xxY"
			x_csv=self.tmpdir.name+"/xxX"
			y.to_csv(y_csv,index=False)
			x.to_csv(x_csv,index=False)

			self.r("x=read.csv('%s')"%(x_csv))
			self.r("y=read.csv('%s')"%(y_csv))
			self.r("x=as.matrix(x)")
			self.r("y=as.matrix(y)")
		else:
			raise BaseException("##ERROR: invalid initialization")

	def load(self,iPath):
		print("##MSG: loading model ...")
		self.tmpdir = tempfile.TemporaryDirectory()
		self.rlogF=self.tmpdir.name+"/rlog.txt"
		modelF="%s/model.robj"%(iPath)
		self.r = pyper.R()
		self.r("sink(file='%s', split=T)"%(self.rlogF))
		self.r("library(glmnet)")
		self.r("load('%s')"%(modelF))

	def build(self,nfolds=10,alpha=0.5):
		print("##MSG: building model ...")
		self.nfolds=nfolds
		self.alpha=alpha

		# CVでlambda_minとlambda_1seの推定
		self.r("m_cv=cv.glmnet(x,y,nfolds=%d,alpha=%f)"%(nfolds,alpha))
		self.r("print(summary(m_cv))") # log出力
		lambda_min=self.r.get("m_cv$lambda.min")
		lambda_1se=self.r.get("m_cv$lambda.1se")

		# lambda_minとlambda_1seのモデル構築
		self.r("m_min=glmnet(x,y,lambda=%f, alpha=%f)"%(lambda_min,alpha))
		self.r("m_1se=glmnet(x,y,lambda=%f, alpha=%f)"%(lambda_1se,alpha))
		self.r("print(summary(m_min))") # log出力
		self.r("print(summary(m_1se))") # log出力

	def predict(self,x,s="lambda.min"):
		print("##MSG: predicting ...")
		#print(self.tmpdir.name)
		x_csv=self.tmpdir.name+"/xxXp"
		x.to_csv(x_csv,index=False)
		self.r("xp=read.csv('%s')"%(x_csv))
		self.r("xp=as.matrix(xp)")

		if type(s)==str:
			s="'%s'"%s
		else:
			s=str(s)
		self.r("prd = predict(m_cv,xp,s=%s)"%(s))
		self.r("prd = as.data.frame(prd)")
		self.r("colnames(prd)=c('prd')")
		prd=self.r.get("prd")

		# オブジェクトを初期化して返す
		pred=rPredict(prd)
		return pred

	def save(self,oPath):
		print("##MSG: saving model ...")
		os.makedirs(oPath,exist_ok=True)

		#######
		# cv.glmentのRモデル保存
		self.r("save(m_cv ,file='%s/model.robj')"%oPath)

		# CVの結果統計
		stats={}
		stats["lambda_min"]=self.r.get("m_cv$lambda.min")
		stats["lambda_1se"]=self.r.get("m_cv$lambda.1se")
		self.lambdas=[stats["lambda_min"],stats["lambda_1se"]]

		json_dump = json.dumps(stats, ensure_ascii=False, indent=2)
		with open("%s/stats.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

		# lambda別統計
		lambda_=self.r.get("m_cv$lambda")
		cvm    =self.r.get("m_cv$cvm")
		cvsd   =self.r.get("m_cv$cvsd")
		cvup   =self.r.get("m_cv$cvup")
		cvlo   =self.r.get("m_cv$cvlo")
		nzero  =self.r.get("m_cv$nzero")
		lmd=[]
		i_min=i_1se=None
		for i in range(len(lambda_)):
			lmd.append([lambda_[i], nzero[i], cvm[i], cvsd[i], cvup[i], cvlo[i]])

		with open("%s/lambda.csv"%(oPath),"w") as f:
			writer = csv.writer(f, lineterminator='\n')
			writer.writerow(["lambda","nzero","cvm","cvsd","cvup","cvlo"])
			for row in lmd:
				writer.writerow(row)

		# 各種チャート保存
		self.r("png('%s/coef.png')"%oPath)
		self.r("plot(m_cv)")
		self.r("dev.off()")
		self.r("png('%s/mse.png')"%oPath)
		self.r("plot(m_cv$glmnet.fit)")
		self.r("dev.off()")

		#######
		# lambda_minとlambda_1seモデルの保存
		for mName in ["min","1se"]:
			op="%s/model_%s"%(oPath,mName)
			os.makedirs(op,exist_ok=True)

			# モデル保存
			self.r("save(m_%s ,file='%s/model.robj')"%(mName,op))

			beta=self.r.get("m_%s$beta"%(mName))
			a0  =self.r.get("m_%s$a0"%(mName))

			with open("%s/coef.csv"%(op),"w") as f:
				writer = csv.writer(f, lineterminator='\n')
				writer.writerow(["name","coefficient"])
				writer.writerow(["intercept",a0])
				for i in range(len(beta)):
					#print(float(beta[i]),float(0.0))
					if float(beta[i])!=float(0.0):
						writer.writerow([self.x_names[i],beta[i]])

			stats={}
			stats["dim"]=[int(v) for v in self.r.get("m_%s$dim"%(mName))]
			stats["nob"]=int(self.r.get("m_%s$nob"%(mName)))
			stats["lambda"]=float(self.r.get("m_%s$lambda"%(mName)))
			stats["dev.ratio"]=float(self.r.get("m_%s$dev.ratio"%(mName)))
			stats["nulldev"]=float(self.r.get("m_%s$nulldev"%(mName)))
			stats["npasses"]=int(self.r.get("m_%s$npasses"%(mName)))
			json_dump = json.dumps(stats, ensure_ascii=False, indent=2)
			with open("%s/stats.json"%(op),"bw") as f:
				f.write(json_dump.encode("utf-8"))

		# Rのログ終了&書き込み
		self.r("sink()")
		os.system("cp %s %s"%(self.rlogF,oPath))

if __name__ == '__main__':
	import dataset as ds

	st=time.time()
	#'''
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

	'''
	config={}
	config["type"]="table"
	#config["names"]=["Sex","Length","Diameter","Height","Whole","Shucked","Viscera","Shell","Rings","id"]
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
	#config["convs"]=["dummy(drop_first=True,dummy_na=False,dtype=float)","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()","numeric()"]
	data=ds.mkTable(config,"./data/abalone.csv")
	y=ds.cut(data,["Rings"])
	x=ds.cut(data,["Rings"],reverse=True)
	#ds.show(x)
	#ds.show(y)
	'''

	model=rlasso(x,y)
	model.build()
	model.save("xxrlasso_model")

	pred=model.predict(x,s="lambda.min")
	#print(pred.y_pred)
	pred.evaluate(y)
	#print(pred.y_true)
	#print(pred.y)
	#print(pred.stats)
	#print(pred.charts)
	#pred.charts["true_pred_scatter"].savefig("xxa.png")
	#pred.charts["true_pred_scatter"]
	#plt.show()
	pred.save("xxrlasso_pred")

	# 作成したmodelを読み込んでの予測
	model=rlasso(modelPath="xxrlasso_model")
	#print("time8=",time.time()-st)
	pred=model.predict(x,s=0.01)
	#print(pred)
	pred.evaluate(y)
	#print("tim9=",time.time()-st)
	pred.save("xxrlasso_pred2")
	#print("timea=",time.time()-st)
	

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt
import sklearn.metrics as metrics
import scipy.stats as stats
import seaborn as sb

class rPredict(object):
	def __init__(self):
		self.x=None
		self.y_true=None
		self.y_pred=None
		self.values=None
		self.charts=None

	#metrics.explained_variance_score(y_true, y_pred)	Explained variance regression score function
	#metrics.max_error(y_true, y_pred)	max_error metric calculates the maximum residual error.
	#metrics.mean_absolute_error(y_true, y_pred)	Mean absolute error regression loss
	#metrics.mean_squared_error(y_true, y_pred[, …])	Mean squared error regression loss
	#metrics.mean_squared_log_error(y_true, y_pred)	Mean squared logarithmic error regression loss
	#metrics.median_absolute_error(y_true, y_pred)	Median absolute error regression loss
	#metrics.r2_score(y_true, y_pred[, …])
	def evaluate(self,y_pd):
		self.y_true=y_pd.values.reshape((-1,))

		if self.y_pred is None:
			print("##WARNING not predicted yet")
			return

		values={} # jsonで保存できる結果
		charts={} # pltオブジェクト等

		# report(各種スコア)の作成と保存
		values["mean_squared_error"]=metrics.mean_squared_error(self.y_true,self.y_pred)
		values["mean_absolute_error"]=metrics.mean_absolute_error(self.y_true,self.y_pred)
		values["median_absolute_error"]=metrics.median_absolute_error(self.y_true,self.y_pred)
		values["max_error"]=metrics.max_error(self.y_true,self.y_pred)
		values["r2_score"]=metrics.r2_score(self.y_true,self.y_pred)

		#fig=sb.jointplot(self.y_true,self.y_pred,kind="scatter",stat_func=stats.pearsonr)
		tp=np.hstack([self.y_true.reshape((-1,1)), self.y_pred.reshape((-1,1))])
		df=pd.DataFrame(tp,columns=["y_true","y_predicted"])
		fig=sb.jointplot(x="y_true",y="y_predicted",data=df,kind="scatter")
		#fig.annotate(stats.pearsonr)
		charts["true_pred_scatter"]=fig
		#fig.savefig("output.png")

		self.values=values
		self.charts=charts

	def save(self,oPath):
		if self.y_pred is None:
			print("##WARNING not predicted yet")
			return

		os.makedirs(oPath,exist_ok=True)

		# サンプル別予測結果,予測値の出力
		prd=[]
		names=["id","y_pred"]
		if not self.y_true is None:
			names.append("y_true")

		#print(self.probClassOrder,self.labels)
		#exit()
		prd.append(names)

		for i in range(len(self.y_pred)):
			line=[]
			line.append(self.id[i])
			line.append(float(self.y_pred[i]))
			if not self.y_true is None:
				line.append(float(self.y_true[i]))
			prd.append(line)
		
		json_dump = json.dumps(prd, ensure_ascii=False, indent=2)
		with open("%s/predict.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

		# 各種統計
		if self.values is None:
			return
		json_dat={}

		for key in ["mean_squared_error","mean_absolute_error","median_absolute_error","max_error","r2_score"]:
			if key in self.values.keys():
				if self.values[key].__class__.__name__=="ndarray":
					json_dat[key]=self.values[key].tolist()
				else:
					json_dat[key]=self.values[key]

		json_dump = json.dumps(json_dat, ensure_ascii=False, indent=2)
		with open("%s/stats.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

		# roc chartとconfusion matrix chart
		if self.charts is None:
			return
		self.charts["true_pred_scatter"].savefig("%s/true_pred_scatter.png"%oPath)


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
	def __init__(self,y_pred):
		self.y_pred=y_pred
		self.y_true=None
		self.y     =None
		self.values=None
		self.charts=None

	#metrics.explained_variance_score(y_true, y_pred)	Explained variance regression score function
	#metrics.max_error(y_true, y_pred)	max_error metric calculates the maximum residual error.
	#metrics.mean_absolute_error(y_true, y_pred)	Mean absolute error regression loss
	#metrics.mean_squared_error(y_true, y_pred[, …])	Mean squared error regression loss
	#metrics.mean_squared_log_error(y_true, y_pred)	Mean squared logarithmic error regression loss
	#metrics.median_absolute_error(y_true, y_pred)	Median absolute error regression loss
	#metrics.r2_score(y_true, y_pred[, …])
	def evaluate(self,y_true):
		self.y_true=y_true.reset_index(drop=True)
		#self.y=y_true.join(self.y_pred)
		self.y=y_true.copy()
		self.y["prd"]=self.y_pred.values
		self.y.columns=["y_true","y_predicted"]
		self.y=self.y.reset_index()

		# report(各種スコア)の作成と保存
		self.stats={} # jsonで保存できる結果
		self.stats["mean_squared_error"]=metrics.mean_squared_error(self.y_true,self.y_pred)
		self.stats["mean_absolute_error"]=metrics.mean_absolute_error(self.y_true,self.y_pred)
		self.stats["median_absolute_error"]=metrics.median_absolute_error(self.y_true,self.y_pred)
		self.stats["max_error"]=metrics.max_error(self.y_true,self.y_pred)
		self.stats["r2_score"]=metrics.r2_score(self.y_true,self.y_pred)

		# pltオブジェクト等
		self.charts={}
		fig=sb.jointplot(x="y_true",y="y_predicted",data=self.y,kind="scatter")
		self.charts["true_pred_scatter"]=fig

	def save(self,oPath):
		if self.y is None:
			print("##WARNING not predicted yet")
			return

		os.makedirs(oPath,exist_ok=True)

		# 予測値-実装値表
		self.y.to_csv("%s/predict.csv"%(oPath),index=False)

		# 各種統計
		if self.stats is not None:
			json_dat={}
			for key,val in self.stats.items():
				json_dat[key]=float(val)#.tolist()
			json_dump = json.dumps(json_dat, ensure_ascii=False, indent=2)
			with open("%s/stats.json"%(oPath),"bw") as f:
				f.write(json_dump.encode("utf-8"))

		# pred-trueの散布図
		if self.charts is not None:
			self.charts["true_pred_scatter"].savefig("%s/true_pred_scatter.png"%oPath)


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

class ClassificationPredicted(object):
	def __init__(self):
		self.x=None
		self.y_true=None
		self.y_pred=None
		self.values=None
		self.charts=None

	def plot_confusion_matrix(self,cm,output_file):
		hrate_cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
		vrate_cm = cm.astype('float') / cm.sum(axis=0)[:, np.newaxis]
		trate_cm = cm.astype('float') / cm.sum()
		hit=np.sum(np.diag(cm))
		accuracy=hit.astype('float')/cm.sum()

		fig=plt.figure()
		plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
		title="Confusion Matrix\n"
		title+="total accuracy=%.3f (%d/%d)\n"%(accuracy,hit,cm.sum())
		title+="(total ratio, holizontal raion(color strength), vertical ratio from the top)"
		plt.title(title)
		plt.colorbar()
		tick_marks = np.arange(len(self.labels))
		plt.xticks(tick_marks, self.labels)#, rotation=45)
		plt.yticks(tick_marks, self.labels)

		thresh = cm.max() / 2.
		for i in range(cm.shape[0]):
			for j in range(cm.shape[1]):
				text=""
				text+="%d\n"%(cm[i, j])
				text+="(%.2f)\n"%(trate_cm[i, j])
				text+="(%.2f)\n"%(hrate_cm[i, j])
				text+="(%.2f)"%(vrate_cm[i, j])
				plt.text(j, i,text,
					 verticalalignment="center",
					 horizontalalignment="center",
					 color="white" if cm[i, j] > thresh else "black")

		plt.tight_layout()
		plt.ylabel('True class')
		plt.xlabel('Predicted class')
		return fig

	def evaluate(self,y_pd):
		self.y_true=y_pd.values.reshape((-1,))

		if self.y_pred is None or self.y_prob is None:
			print("##WARNING not predicted yet")
			return

		values={} # jsonで保存できる結果
		charts={} # pltオブジェクト等

		# report(各種スコア)の作成と保存
		values["labels"]=self.labels
		values["recall"]=metrics.recall_score(self.y_true,self.y_pred,average=None)
		values["precision"]=metrics.precision_score(self.y_true,self.y_pred,average=None)
		values["f1"]=metrics.f1_score(self.y_true,self.y_pred,average=None)

		# confusion matrix
		cm=metrics.confusion_matrix(self.y_true,self.y_pred)
		values["accuracy"]=np.sum(np.diag(cm)).astype('float')/cm.sum()
		values["confusion_matrix"]=cm

		# confusion matrixのプロット
		charts["confusion_matrix_plot"]=self.plot_confusion_matrix(values["confusion_matrix"], "xxcm1.png")

		# ROC曲線, AUC
		fig=plt.figure()
		#ax = fig.add_subplot()
		auc=[]

		cls2idx={c:i for i,c in enumerate(self.probClassOrder)}
		for i,c in enumerate(self.probClassOrder):
			#print(self.y_true)
			#print([c])
			#exit()
			#print(self.y_prob[:,c])
			yt=np.array([cls2idx[v] for v in self.y_true],dtype=float)
			fpr, tpr, thresholds = metrics.roc_curve(yt, self.y_prob[:,i], pos_label=i)
			auc.append(metrics.auc(fpr, tpr))
			axs = fig.gca() # 同一グラフに各クラスの結果を重ねる
			axs.plot(fpr, tpr, label='class=%s, auc=%.3f)'%(c,auc[-1]))
			axs.legend()
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.grid(True)
		plt.title('ROC curve')

		values["auc"]=auc
		charts["roc_chart"]=fig

		self.values=values
		self.charts=charts
		#print(self.values.keys())

	def save(self,oPath):
		if self.y_prob is None:
			print("##WARNING not predicted yet")
			return

		os.makedirs(oPath,exist_ok=True)

		# サンプル別予測結果,予測確率の出力
		prd=[]
		names=["id","y_pred"]
		for c in self.probClassOrder: #self.labels:
			#names.append("prob_"+str(self.labels[c]))
			names.append("prob_"+str(c))
		if not self.y_true is None:
			names.append("y_true")
		prd.append(names)

		cast=str
		if self.y_pred[0].__class__.__name__[0]=="i":
			cast=int

		for i in range(len(self.y_pred)):
			line=[]
			line.append(self.id[i])
			line.append(cast(self.y_pred[i]))
			for p in self.y_prob[i]:
				line.append(float(p))
			if not self.y_true is None:
				line.append(cast(self.y_true[i]))
			prd.append(line)
		
		json_dump = json.dumps(prd, ensure_ascii=False, indent=2)
		with open("%s/predict.json"%(oPath),"bw") as f:
			f.write(json_dump.encode("utf-8"))

		# 各種統計
		if self.values is None:
			return
		json_dat={}
		for key in ['labels', 'recall', 'precision', 'f1', 'accuracy', 'confusion_matrix', 'auc']:
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
		self.charts["roc_chart"].savefig("%s/roc_chart.png"%oPath)
		self.charts["confusion_matrix_plot"].savefig("%s/confusion_matrix.png"%oPath)


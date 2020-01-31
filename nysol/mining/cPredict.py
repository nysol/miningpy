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

class cPredict(object):
	def __init___old(self):
		self.y_true=None
		self.y_pred=None
		self.values=None
		self.charts=None

	def __init__(self,y_pred,y_prob,orderedLabels):
		self.y_pred=y_pred
		self.y_prob=y_prob
		self.orderedLabels=orderedLabels
		self.y_true=None
		self.y     =None
		self.stats =None
		self.charts=None

	#def plot_confusion_matrix_chart(self,cm):
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
		tick_marks = np.arange(len(self.orderedLabels))
		plt.xticks(tick_marks, self.orderedLabels)#, rotation=45)
		plt.yticks(tick_marks, self.orderedLabels)

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

	def evaluate(self,y_true):
		self.y_true=y_true.copy()
		self.y_true.columns=["y_true"]

		# y_true,y_pred,y_probの結合
		self.y=y_true.join(self.y_pred)
		self.y=self.y.join(self.y_prob)
		self.y=self.y.reset_index()

		stats={} # jsonで保存できる結果
		charts={} # pltオブジェクト等

		# report(各種スコア)の作成と保存
		stats["labels"]=self.orderedLabels
		stats["recall"]=metrics.recall_score(self.y_true.values,self.y_pred.values,average=None)
		stats["precision"]=metrics.precision_score(self.y_true,self.y_pred,average=None)
		stats["f1"]=metrics.f1_score(self.y_true,self.y_pred,average=None)

		# confusion matrix
		cm=metrics.confusion_matrix(self.y_true,self.y_pred)
		stats["accuracy"]=np.sum(np.diag(cm)).astype('float')/cm.sum()
		stats["confusion_matrix"]=cm

		# confusion matrixのプロット
		charts["confusion_matrix_plot"]=self.plot_confusion_matrix(stats["confusion_matrix"], "xxcm1.png")

		# ROC曲線, AUC
		fig=plt.figure()
		#ax = fig.add_subplot()
		auc=[]

		cls2idx={c:i for i,c in enumerate(self.orderedLabels)}
		for i,c in enumerate(self.orderedLabels):
			yt=np.array([cls2idx[v[0]] for v in self.y_true.values],dtype=float)
			fpr, tpr, thresholds = metrics.roc_curve(yt, self.y_prob.values[:,i], pos_label=i)
			auc.append(metrics.auc(fpr, tpr))
			axs = fig.gca() # 同一グラフに各クラスの結果を重ねる
			axs.plot(fpr, tpr, label='class=%s, auc=%.3f)'%(c,auc[-1]))
			axs.legend()
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.grid(True)
		plt.title('ROC curve')

		stats["auc"]=auc
		charts["roc_chart"]=fig

		self.stats =stats
		self.charts=charts

	def save(self,oPath):
		if self.y is None:
			print("##WARNING not evaluated yet. run evaluate.")
			return

		os.makedirs(oPath,exist_ok=True)

		# 予測値-実装値表
		self.y.to_csv("%s/predict.csv"%(oPath),index=False)

		# 各種統計
		if self.stats is not None:
			json_dat={}
			for key in ['labels', 'recall', 'precision', 'f1', 'accuracy', 'confusion_matrix', 'auc']:
				if key in self.stats.keys():
					if type(self.stats[key])==np.ndarray:
						json_dat[key]=self.stats[key].tolist()
					else:
						json_dat[key]=self.stats[key]

			json_dump = json.dumps(json_dat, ensure_ascii=False, indent=2)
			with open("%s/stats.json"%(oPath),"bw") as f:
				f.write(json_dump.encode("utf-8"))

		# roc chartとconfusion matrix chart
		if self.charts is None:
			return
		self.charts["roc_chart"].savefig("%s/roc_chart.png"%oPath)
		self.charts["confusion_matrix_plot"].savefig("%s/confusion_matrix.png"%oPath)


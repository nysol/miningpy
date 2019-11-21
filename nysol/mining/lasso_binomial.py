#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV,Lasso
from sklearn.linear_model import LogisticRegressionCV,LogisticRegression
from matplotlib import pyplot as plt
from sklearn.multiclass import OneVsRestClassifier

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

class lasso(object):
	def __init__(self,x,y,xNames,yName,cNames,config):
		self.x=x
		self.y=y
		self.xNames=xNames
		if xNames is None:
			self.xNames=[str(i) for i in range(self.x.shape[1])]
		self.yName=yName
		if yName is None:
			self.yName="y"
		self.cNames=cNames
		# cNames==Noneの場合はモデル構築後に決まる

		# xの標準化
		self.scaler = StandardScaler()
		self.scaler.fit(self.x)
		self.trans_x=self.scaler.transform(self.x)

		# yの件数カウント
		self.labels, counts = np.unique(self.y, return_counts=True)
		self.counts=dict(zip(self.labels, counts))
		#print(self.counts)

		self.config=config
		self.pred={}

	# https://own-search-and-study.xyz/2016/12/25/scikit-learn%E3%81%A7%E5%AD%A6%E7%BF%92%E3%81%97%E3%81%9F%E6%B1%BA%E5%AE%9A%E6%9C%A8%E6%A7%8B%E9%80%A0%E3%81%AE%E5%8F%96%E5%BE%97%E6%96%B9%E6%B3%95%E3%81%BE%E3%81%A8%E3%82%81/
	#def setDataset(self,x,y):

	def build(self):
		cv=10
		Cs=40
		penalty="l1"
		if "penalty" in self.config:
			penalty=self.config["penalty"]
		if "cv" in self.config:
			cv=self.config["cv"]
		if "Cs" in self.config:
			Cs=self.config["Cs"]


		#>>> OneVsRestClassifier(LinearSVC(random_state=0)).fit(X, y).predict(X)

		self.model = LogisticRegressionCV(penalty=penalty,cv=cv,Cs=Cs,solver="saga",random_state=0, multi_class='multinomial')
		#self.model = OneVsRestClassifier(
		#		LogisticRegressionCV(penalty=penalty,cv=cv,Cs=Cs,solver="saga",random_state=0, multi_class='multinomial')
		#		)
		self.model.fit(self.trans_x, self.y)
		self.score=self.model.score(self.trans_x, self.y)
		if self.cNames is None:
			self.cNames=[str(i) for i in range(len(self.model.classes_))]
		self.classSize=len(self.cNames)

		#print(self.cNames)
		#print(self.model.classes_)
		#print(self.model.coef_)
		#print(self.model.intercept_)
		#print(self.model.predict(self.trans_x))
		#print(self.y)
		#exit()

	def predict(self,x,y=None):
		trans_x=self.scaler.transform(x)
		predicted={}
		predicted["predict"]=self.model.predict(trans_x)
		predicted["predict_prob"]=self.model.predict_proba(trans_x)
		if not y is None:
			#print(trans_x.shape,y.shape)
			predicted["score"]=self.model.score(trans_x,y)

		print(predicted["predict"])
		#print(self.y)
		print(predicted["predict_proba"])
		print(predicted["score"])
		return predicted


	def plot_confusion_matrix(self,cm, classes, output_file,
							  normalize=False,
							  title='Confusion matrix',
							  cmap=plt.cm.Blues):
		print("cm",cm)

		"""
		This function prints and plots the confusion matrix.
		Normalization can be applied by setting `normalize=True`.
		"""
		if normalize:
			cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
			print("Normalized confusion matrix")
		else:
			print('Confusion matrix, without normalization')

		print(cm)

		plt.imshow(cm, interpolation='nearest', cmap=cmap)
		plt.title(title)
		plt.colorbar()
		tick_marks = np.arange(len(classes))
		plt.xticks(tick_marks, classes, rotation=45)
		plt.yticks(tick_marks, classes)

		fmt = '.2f' if normalize else 'd'
		thresh = cm.max() / 2.
		#for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
		for i in range(cm.shape[0]):
			for j in range(cm.shape[1]):
				plt.text(j, i, format(cm[i, j], fmt),
					 horizontalalignment="center",
					 color="white" if cm[i, j] > thresh else "black")

		plt.tight_layout()
		plt.ylabel('True label')
		plt.xlabel('Predicted label')
		plt.savefig(output_file)

	def evaluate(self,oPath):
		y_pred=self.model.predict(self.trans_x)

		# accuracyはscoreに同じ
		accuracy=self.score

		# confusion matrixの作成
		cnf_matrix=metrics.confusion_matrix(self.y,y_pred,labels=self.labels)
		print(cnf_matrix)

		# report(各種スコア)の作成と保存
		report=metrics.classification_report(self.y,y_pred,labels=self.labels)
		recall=metrics.recall_score(self.y,y_pred,labels=self.labels,average=None)
		precision=metrics.precision_score(self.y,y_pred,labels=self.labels,average=None)
		f1=metrics.f1_score(self.y,y_pred,labels=self.labels,average=None)

		print("recall",recall)
		print("precision",precision)
		print("f1",f1)
		#report_file=open(result_dir+"/report.txt","w")
		#report_file.write(report)
		#report_file.close()
		print(report)

		#fig, axs = plt.subplots(nrows=self.classSize, figsize=(8,8*self.classSize))
		#if axs.__class__.__name__=="AxesSubplot":
		#	axs=[axs]
		prob=self.model.predict_proba(self.trans_x)
		auc=[]
		for c in range(self.classSize):
			fpr, tpr, thresholds = metrics.roc_curve(self.y, prob[:,c], pos_label=c)
			auc.append(metrics.auc(fpr, tpr))

			axs = plt.gca()
			axs.plot(fpr, tpr, label='class=%s, auc=%.3f)'%(self.cNames[c],auc[c]))
	
		print("auc",auc)
		plt.legend()
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.grid(True)
		plt.title('ROC curve')
		plt.savefig("roc.png")
		plt.close()

		# confusion matrixのプロット、保存、表示
		title="overall accuracy:"+str(np.round(accuracy,3))
		plt.figure()
		print(cnf_matrix)
		self.plot_confusion_matrix(cnf_matrix, self.labels,"xxcm1.png",title=title)
		plt.figure()
		self.plot_confusion_matrix(cnf_matrix, self.labels,"xxcm2.png", normalize=True,title=title)

	def vizModel(self,oPath):
		#fig = plt.figure()
		#ax = fig.add_subplot(1, 1, 1)
		#y_pred = self.model.predict(self.scaler.transform(self.x))
		#print(y_pred)
		#exit()
		#sns.stripplot(x='variable', y='value', data=df_melt, jitter=True, color='black', ax=ax)

		#ax.scatter(self.y,y_pred,s=5)
		#ax.set_xlabel('true')
		#ax.set_ylabel('predicted')
		#ax.set_aspect('equal')
		#fig.show()
		#fig.savefig(oFile)

		m_log_alphas = self.model.Cs_

		# MSE path chart
		clsSize=len(self.model.scores_)
		#print(clsSize)
		fig, axs = plt.subplots(nrows=clsSize, figsize=(10,6*clsSize))
		print(axs.__class__.__name__)
		print(axs)
		if axs.__class__.__name__=="AxesSubplot":
			axs=[axs]

		i=0
		for key,scores in self.model.scores_.items():
			#print(key,scores)
			print(key,scores.mean(axis=0))
			print(i)
			axs[i] = plt.gca()
			axs[i].plot(m_log_alphas, scores.mean(axis=0), linewidth=2)
			axs[i].errorbar(m_log_alphas, scores.mean(axis=0), yerr = scores.std(axis=0), capsize=2, fmt='o', markersize=1, ecolor='black', markeredgecolor = "black", color='w')
			axs[i].set_xscale('log') # set_xlimより前に実行must
			axs[i].set_xlim(axs[i].get_xlim()[::-1])  # reverse axis
			axs[i].set_title('Mean square error: class='+str(key))
			axs[i].set_xlabel('-log(alpha)')
			i+=1
		fig.savefig("mse.png")
		plt.close()

		# coefficient path chart
		coefs=[]
		for c in reversed(self.model.Cs_):
			model = LogisticRegression(penalty="l1",C=c, solver="saga",random_state=0, multi_class='multinomial')
			model.fit(self.scaler.transform(self.x), self.y)
			coefs.append(model.coef_[0])
		#print("coef.shape",coefs[0].shape)
		#print("alpha.shape",m_log_alphas.shape)

		plt.figure()
		ax = plt.gca()
		ax.plot(m_log_alphas, coefs)
		ax.set_xscale('log')
		ax.set_xlim(ax.get_xlim()[::-1])  # reverse axis
		plt.xlabel('-log(alpha)')
		plt.ylabel('weights')
		plt.title('Lasso coefficients as a function of the regularization')
		plt.axis('tight')
		plt.savefig("coefs.png")
		plt.close()

if __name__ == '__main__':
	import yaml
	from dataset import dataset
	configFile=os.path.expanduser(sys.argv[1])

	with open(configFile, 'r') as rp:
		config = yaml.load(rp)
	print(config["dataset"])

	ds=dataset(config["dataset"])
	#ds._summary()

	# 変数名のセット
	xNames=ds.iFile_nFlds
	xNames+=ds.iFile_cFlds
	yName=ds.iFile_yFld
	cNames=ds.ovlist

	# 数値変数
	x=ds.nums
	# category変数
	for cat in ds.cats:
		x=np.hstack((x,cat.data))
	y=ds.y
	#print(y)
	#print(ds.ovmap)
	#print(ds.ovlist)
	model=lasso(x,y,xNames,yName,cNames,config["lasso_logistic"])

	#'''
	from sklearn.datasets import load_iris
	iris = load_iris()
	print(iris.data)
	print(iris.target)
	x=iris.data
	y=iris.target
	model=lasso(x,y,None,None,None,config["lasso_logistic"])
	#'''

	model.build()
	model.evaluate("xxo")
	model.vizModel("graph.pdf")
	pred=model.predict(x,y)
	print(pred)


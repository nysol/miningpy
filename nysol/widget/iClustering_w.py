#!/usr/bin/env python
# coding: utf-8

# ## インターラクティブクラスタリング

from __future__ import print_function
import os
import sys
import json
from datetime import datetime
import random
import numpy as np
import h5py

import ipywidgets as widgets
from gensim.models import Word2Vec

sys.path.append("../../lib")
from sampleDB import sampleDB
from sample_w import sampleList_w

from fileBrowser import FileBrowser
from news import NewsDB
from cluster_W import ClusterList_W
from icSample import Sample
from sampleDB import sampleDB
#from interactiveClustering import InteractiveClustering

####################################################################
class InteractiveClustering_W(object):
	def __init__(self,iPath,oFile):
		self.iPath=iPath
		self.oFile=oFile
		self.icdb=sampleDB()

		#self.commentList_W=[]
		#self.ic=InteractiveClustering()

	# SampleにfilesのJSONからセットし、widgetを更新
	def load_H(self,iFile):
		self.out.value="データの読込中..."
		with open(iFile[0]) as f:
			coms=json.load(f)

		for com in coms:
			sample=Sample(0)
			sample.fromJSON(com)
			self.icdb.addSample(sample)
		self.out.value="データの読込中...完了"

		self.commentList_W.randomSelect_H(None) # shuffleボタンを押す
		self.tab.selected_index = 1 # sample widgetへ

	# tooltipにはaIDがセットされている
	def delNews_H(self,event):
		self.out.value="ニュースを削除中..."
		self.newsDB_W.delNews(event.tooltip)
		self.out.value="ニュースを削除中...完了"

	def delall_H(self,event):
		self.out.value="ニュースを全削除中..."
		self.newsDB_W.delAllNews()
		self.out.value="ニュースを全削除中...完了"
	#
	def save_H(self,b):
		if len(self.newsDB)==0:
			self.out.value="ニュースファイルが選択されていません"
			return
		self.out.value="データセット作成中..."
		total=len(self.newsDB)
		samples=[]
		for i,com in enumerate(self.newsDB):
			sample=Sample(i)
			sample.property["aID"]     = com.parent.aID
			sample.property["comID"]   = com.com["comID"]
			sample.property["date"]    = com.com["date"]
			sample.property["agree"]   = com.com["agree"]
			sample.property["disagree"]= com.com["disagree"]
			sample.property["text"]    = com.com["text"]

			#print("loading model...",flush=True)
			model = Word2Vec.load("model/word2vec.h5")
			vecseq=[]
			for word in com.com["words"]:
				if word in model.wv:
					vecseq.append(model.wv[word].tolist())
			vecseq=np.array(vecseq,dtype=np.float32)
			sample.vector=np.mean(vecseq,axis=0)
			sample.vecseq=vecseq

			samples.append(sample)
			self.out.value="データセット作成中...done(%d/%d) %s"%(i+1,total,com.com["comID"])

		#print("saving embeddingAll vectors ...",flush=True)
		self.out.value="データセット保存中..."
		jsonList=[]
		for sample in samples:
			jsonList.append(sample.toJSON())
		sample_dump = json.dumps(jsonList, ensure_ascii=False, indent=2)
		with open(self.oFile,"bw") as f:
			f.write(sample_dump.encode("utf-8"))
		self.out.value="データセット保存中...完了"

		#for sample in samples:
		#	sample.show()

	def quit_H(self,b):
		self.box.close_all()
		print("done")

	def setTabTitle(self,index,title):
		self.tab.set_title(index,title)

	def sampleList_m(self,signature,sample):
		print(signature,sample)

	def widget(self):
		### fileBox
		config={
			"multiSelect":False,
			"property":True,
			"propertyRows":20,
			"actionHandler":self.load_H,
			"actionTitle":"選択"
	   }
		fb=FileBrowser(self.iPath,config)
		fileBox = fb.widget()

		### コメント表示
		config={
			"db":self.icdb,
			"message":self.sampleList_m
	   }
		self.commentList_W=sampleList_w(config)
		commentBox=self.commentList_W.widget()

		#delall_W=widgets.Button(description='全ニュース削除')
		#delall_W.on_click(self.delall_H)
		#self.commentList_W=SampleList_W(self)
		#commentBox=self.commentList_W.widget()

		# cluster
		self.clusterList_W=ClusterList_W(self)
		clusterBox=self.clusterList_W.widget()

		# top
		#self.out = widgets.Output(layout=widgets.Layout(height='40px', border='1px solid white', width='99%'))
		#self.out = widgets.Output(rows=1,layout={'border': '1px solid white'})
		quit_W=widgets.Button(description='終了')
		quit_W.on_click(self.quit_H)
		#save_W=widgets.Button(description='データセット作成',layout=widgets.Layout(width='200px'))
		save_W=widgets.Button(description='保存')
		save_W.on_click(self.save_H)
		button_W=widgets.HBox([save_W,quit_W])

		# メッセージ窓
		self.out = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		### tabコンテナ
		children=[]
		children.append(fileBox)
		children.append(commentBox)
		children.append(clusterBox)
		self.tab = widgets.Tab()
		self.tab.children = children
		self.tab.set_title(0, "ファイル")
		self.tab.set_title(1, "コメント")
		self.tab.set_title(2, "クラスタ")

		self.box=widgets.VBox([button_W,self.out,self.tab])
		return self.box


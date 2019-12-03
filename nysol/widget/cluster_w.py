#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from ipywidgets import Button, Layout
import os
import json
from datetime import datetime

####################################################################
class cluster_w(object):
	def __init__(self,data,parent):
		self.data=data # Clusterオブジェクト
		self.parent=parent

	def delete_h(self,b):
		self.parent.delCluster(self.data.id)

	def addSample(self,sample):
		self.samples.append(sample)
		
	def submit_h(self,b):
		self.title=self.titleTxt.value
		self.description=self.descriptionTxt.value
		self.parent.updCluster()

	def sampleList_m(self,signature,sample):
		print(signature,sample)
	
	def widget(self):
		# ボタン系
		submit_w=widgets.Button(description="登録")
		submit_w.on_click(self.submit_h)

		lb0=widgets.Label(value="cID: %s"%self.data.id)
		lb1=widgets.Label(value="タイトル：")
		title_w=widgets.Text(value="",layout=Layout(width='80%'))
		title_w.observe(self.submit_h, names='value') # HANDLER

		lb2=widgets.Label(value="詳細内容：")
		self.descriptionTxt=widgets.Textarea(rows=5,layout=Layout(width='90%'))

		lb3=widgets.Label(value="サンプル：")
		config={                                                                                                             
			"db":self.data.sampleDB,
			"message":self.sampleList_m
		}
		sl=SampleList_w(config)

		description_w=widgets.Select(options=[],rows=10,disable=True,layout=Layout(width='90%'))
		del_w=widgets.Button(description="このクラスタを削除")
		box=widgets.VBox([lb0,submit_w,lb1,title_w,lb2,descriptionTxt,lb3,description,del_w])
		return box
	
####################################################################
class clusterDB_w(object):
	def __init__(self,config={}):
		self.clusterList=[]
		self.config = config
		# config default設定
		if "db" not in self.config:
			self.config["db"]=None  # clusterDB
		if "message" not in self.config:
			self.config["message"]=None

		self.db=self.config["db"]
		print("xxxxdb",self.db.__class__.__name__)
		self.message=self.config["message"]
		if not self.db is None:
			for data in self.db:
				self.clusterList.append(cluster_w(data,self))
				print("xxxxd",data.__class__.__name__)

	def refresh(self):
		print("self.clusterList",self.clusterList)
		children=[]
		for i,cluster in enumerate(self.clusterList):
			print("xxxx1", cluster.data.__class__.__name__)
			print("xxxx2", len(cluster.data.sampleDB))
			#self.cList_w.set_title(i, cluster.data.title())
			cw=cluster_w(cluster,self)
			children.append(cw.widget())
		self.cList_w.children=children
		if not self.message is None:
			self.message("refresh",self)

	# clusterListに新規clusterを追加し、widgetを更新
	def add(self,cluster):
		c=Cluster()
		self.clusterList.append(Cluster())

		if not self.message is None:
			self.message("addCluster",self)

	def addNew(self):
		self.clusterList.addNews(Cluster())
		self.refresh()
		if not self.message is None:
			self.message("addCluster",self)

	# accordion上の１つのclusterを削除する。
	# tooltipにはaIDがセットされている
	def delCluster(self,aID):
		self.clusterList.delete(aID)
		self.refresh()
		if not self.message is None:
			self.message("delCluster",self)

	def clear_h(self):
		self.clusterList=[]
		self.refresh()
		if not self.message is None:
			self.message("clear_h",self)

	def widget(self):
		exe_w = widgets.Button(description='clear', disabled=False)
		exe_w.on_click(self.clear_h)
		self.cList_w = widgets.Accordion(children=[])
		box = widgets.VBox([exe_w,self.cList_w])
		return box


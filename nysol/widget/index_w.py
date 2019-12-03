#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import ipywidgets as widgets
from IPython.core.getipython import get_ipython
import os

class index_w(object):
	def __init__(self,shell,config={}):
    self.shell=sehll
		get_ipython()
		self.config = config
		# config default設定
		if "multiSelect" not in self.config:
			self.config["multiSelect"]=False
		if "propertyRows" not in self.config:
			self.config["propertyRows"]=20
		if "property" not in self.config:
			self.config["property"]=False
		if "actionHandler" not in self.config:
			self.config["actionHandler"]=None
		if "actionTitle" not in self.config:
			self.config["actionTitle"]="choose"
		if "message" not in self.config:
			self.config["message"]=None
		self.message=self.config["message"]

		#self.path = os.getcwd()
		#self.setFileList()

	# カレントpathのファイル一覧を作成し、widget(fList_w)に表示する
	def setFileList(self):
		self.files = []
		self.dirs = []
		if self.path!="/":
			self.dirs.append("..")
		if(os.path.isdir(self.path)):
			for f in os.listdir(self.path):
				ff = self.path + "/" + f
				if os.path.isdir(ff):
					self.dirs.append(f)
				else:
					self.files.append(f)
		self.fList_w.options=self.dirs+self.files

	# HANDLER
	# ディレクトリの変更
	def cd_h(self,b):
		if self.config["multiSelect"] and len(self.fList_w.value)!=1:
			return
		if self.config["multiSelect"]:
			fValue=self.fList_w.value[0]
		else:
			fValue=self.fList_w.value
		if fValue == '..':
			 path = os.path.split(self.path)[0]
		else:
			if self.path=="/":
				path = self.path + fValue
			else:
				path = self.path + "/" + fValue
		if not os.path.isdir(path):
			return

		self.path=path
		self.fList_w.options=self.dirs+self.files
		#self.fList_w.index=[0] # 先頭(..)を選択状態にする
		#self.fList_w.value=['..'] # 先頭(..)を選択状態にする
		#print(self.fList_w.keys)
		self.pwd_w.value=self.path
		self.setFileList()

	## HANDLER
	## chooseボタンが押されたときにcallされる
	def action_h(self,event):
		if not self.config["actionHandler"] is None:
			self.config["actionHandler"](self.chosenFiles)

	# methodをcallする雛形スクリプトをcurrent cellに置き換え表示する
	def sel_h(self,event):
		contents="""
"""
    self.shell.set_next_input(contents, replace=True)

	# description boxにmethodのdescriptionを表示する
	def method_h(self,event):
		self.selName=event.owner.value
		self.selMethod=self.name ###
		text=eval(self.selMethod+".description()")
		self.description.value=text

	def propText(self):
		return self.fileProperty.value

	def widget(self):
		#self.initBox.close()
		self.pwd_w=widgets.Text(value=self.path,disabled=True,layout=widgets.Layout(width='99%')) # current path
		#print(self.pwd_w.keys)

		# ボタン系
		sel_w=widgets.Button(description='選択')
		sel_w.on_click(self.sel_h)
		sel_w=widgets.Button(description='終了')
		quit_w.on_click(self.quit_h)
		buttons=widgets.HBox([sel_w,quit_w])#,self.cancelButton])

		# method一覧
		self.method_w=widgets.Select(options=[],rows=14) # file list
		self.method_w.observe(self.method_h, names='value') # HANDLER
		self.description_w=widgets.Textarea(rows=11,disabled=True,layout=widgets.Layout(width='99%')) # 
		listBox=widgets.HBox([self.method_w,self.desscription_w])

		# 統合
		box=widgets.VBox([buttons,listBox])
		self.setMethod()
		return box


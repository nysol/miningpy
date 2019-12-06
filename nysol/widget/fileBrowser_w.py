#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
#from ipywidgets import Button, Layout
import nysol.widget.lib as wlib
import csv
import os

class fileBrowser_w(object):
	def __init__(self,path,config={}):
		self.path = os.path.expanduser(path)
		self.path = os.path.abspath(self.path)
		self.orgPath=self.path
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
				if f[0]==".":
					continue
				ff = self.path + "/" + f
				if os.path.isdir(ff):
					self.dirs.append(f)
				else:
					self.files.append(f)
		self.fList_w.options=sorted(self.dirs)+sorted(self.files)

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
		self.pwd_w.value=self.path
		self.setFileList()

	def upd_h(self,b):
		self.setFileList()

	# fomatter
	def formatter_h(self,b):
		if self.config["multiSelect"] and len(self.fList_w.value)!=1:
			return
		if self.config["multiSelect"]:
			fValue=self.fList_w.value[0]
		else:
			fValue=self.fList_w.value
		fName=self.path + "/"+fValue
		script=wlib.sampleFormatter(fName)
		self.script_w.value=script

	## HANDLER
	## chooseボタンが押されたときにcallされる
	def action_h(self,event):
		if not self.config["actionHandler"] is None:
			self.config["actionHandler"](self.chosenFiles)
		#if not self.message is None:
		#	self.message("action_h",self)

	## HANDLER
	## fList_wの値が変わった時にcallされる
	#  * 選択されたファイル名をlistに格納
	#  * 右のproperty欄に内容表示
	def fList_h(self,event):
		# print("fList_h",event)
		# {'name': 'value', 'old': ('fileBrowser.py',), 'new': ('fileBrowser.ipynb', 'fileBrowser.py'), 'owner': SelectMultiple(index=(3, 4), options=('..', '__pycache__', '.ipynb_checkpoints', 'fileBrowser.ipynb', 'fileBrowser.py'), rows=14, value=('fileBrowser.ipynb', 'fileBrowser.py')), 'type': 'change'}
		# ファイル名のセット
		self.chosenFiles=[]
		if self.config["multiSelect"]:
			for file in event.owner.value:
				self.chosenFiles.append(self.pwd_w.value+"/"+file)
		else:
			self.chosenFiles.append(self.pwd_w.value+"/"+event.owner.value)

		# propertyへの内容表示
		if not self.config["property"]:
			return

		# multiSelectで表示するのは、ひとつのファイルを選んだ時のみ
		if self.config["multiSelect"] and len(event["new"])!=1:
			return


		propText=""
		if self.config["multiSelect"]:
			fName=self.pwd_w.value+"/"+event["new"][0]
		else:
			fName=self.chosenFiles[0]
		self.fileAttr_w.value=wlib.getFileAttribute(fName)
		if os.path.isfile(fName):
			propText=wlib.sampleTXT(fName,50)
		self.fileProperty.value=propText

	def propText(self):
		return self.fileProperty.value

	def widget(self):
		#self.initBox.close()
		self.pwd_w=widgets.Text(value=self.path,disabled=True,layout=widgets.Layout(width='99%')) # current path
		#print(self.pwd_w.keys)

		# ボタン系
		cd_w=widgets.Button( description='cd',layout=widgets.Layout(width='70px'))
		cd_w.on_click(self.cd_h) # HANDLER
		upd_w=widgets.Button( description='更新',layout=widgets.Layout(width='70px'))
		upd_w.on_click(self.upd_h) # HANDLER
		if self.config["actionHandler"] is None:
			buttons=widgets.HBox([cd_w,upd_w])#,self.cancelButton])
		else:
			action_w=widgets.Button( description=self.config["actionTitle"])
			action_w.on_click(self.action_h) # HANDLER
			buttons=widgets.HBox([cd_w,upd_w,action_w])#,self.cancelButton])

		# file list系
		if self.config["multiSelect"]:
			self.fList_w=widgets.SelectMultiple(options=[],rows=14) # file list
		else:
			self.fList_w=widgets.Select(options=[],rows=14) # file list
		self.fList_w.observe(self.fList_h, names='value') # HANDLER
		if self.config["property"]:
			self.fileAttr_w=widgets.Textarea(rows=2,disabled=True,layout=widgets.Layout(width='99%')) # 
			self.fileProperty=widgets.Textarea(rows=8,disabled=True,layout=widgets.Layout(width='99%')) # 
			fp_w=widgets.VBox([self.fileAttr_w,self.fileProperty],layout=widgets.Layout(width='99%'))
			fListBox_w=widgets.HBox([self.fList_w, fp_w])
		else:
			fListBox_w=widgets.HBox([self.fList_w])

		formatter_w=widgets.Button( description='Formatter')
		formatter_w.on_click(self.formatter_h) # HANDLER
		self.script_w=widgets.Textarea(rows=3,layout=widgets.Layout(width='99%'))
		scriptBox_w=widgets.HBox([formatter_w,self.script_w])

		# 統合
		self.fileBox=widgets.VBox([self.pwd_w,buttons,fListBox_w,scriptBox_w])
		self.setFileList()
		return self.fileBox

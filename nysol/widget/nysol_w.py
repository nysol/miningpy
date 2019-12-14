#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from ipywidgets import Button, Layout, Label
import os
import json
import copy
from datetime import datetime
from IPython.display import clear_output

from nysol.widget.fileBrowser_w import fileBrowser_w
from nysol.widget.selfield_w import selfield_w
import nysol.widget.lib as wlib
import nysol.mcmd as nm

####################################################################
class nysol_w(object):
	def __init__(self,path,tools):
		self.version="0.10"
		self.date=datetime.now()

		clear_output() # jupyter上の出力領域のクリア
		self.path=os.path.abspath(os.path.expanduser(path))
		self.tools=tools
		self.iFile=None
		self.mFile=None
		self.oFile=None
		self.proc_w=None
		#self.oPath=os.path.dirname(self.oFile)
		#os.makedirs(self.oPath, exist_ok=True)

	def exe_h(self,b):
		ret=self.proc_w.exe(self.script_w,self.output_w)
		if ret:
			self.tab.selected_index = 4

	def upd_h(self,b):
		self.setiFile2proc()
		self.setmFile2proc()
		self.setiPath2proc()
		self.setoPath2proc()

	# Dropdownメニューが変化したら呼ばれる
	def proc_h(self,event):
		val=event.owner.value
		if val=="":
			return
		val=val.split("_w")[0]+"_w" # _w以降は無視する
		name2=val.split(".")[-1]
		paras={}
		paras["name"] =val
		paras["name2"] =name2
		paras["oPath"]=self.path
		scp="""
from nysol.widget.{name} import {name2}
func_w={name2}()
""".format(**paras)

		# scpを実行してローカル変数の内容をret辞書にセット
		ret={}
		#print(scp)
		exec(scp,{},ret)
		self.proc_w=ret["func_w"] # 処理オブジェクト
		self.proc_w.setParent(self)
		#print(self.proc_w)
		self.procBox_w=widgets.VBox([self.buttons_w,self.proc_w.widget()])

		# タブの再描画(tupleが更新できないので)
		newTab=[]
		newTab.append(self.tab.children[0])
		newTab.append(self.tab.children[1])
		newTab.append(self.tab.children[2])
		newTab.append(self.procBox_w)
		newTab.append(self.tab.children[4])
		newTab.append(self.tab.children[5])
		self.tab.children=newTab

		self.setiFile2proc()
		self.setmFile2proc()
		self.setiPath2proc()
		self.setoPath2proc()

	# 処理オブジェクト(self.proc_w)に入力ファイルを伝える
	def setiFile2proc(self):
		if hasattr(self.proc_w, 'setiFile'):
			iFiles=self.iFile_w.getFiles()
			iPropText= self.iFile_w.propText()
			self.proc_w.setiFile(iFiles,iPropText)

	# 処理オブジェクト(self.proc_w)に参照ファイルを伝える
	def setmFile2proc(self):
		if hasattr(self.proc_w, 'setmFile'):
			mFiles=self.mFile_w.getFiles()
			mPropText= self.mFile_w.propText()
			self.proc_w.setmFile(mFiles,mPropText) # 処理オブジェクトに参照ファイルを伝える

	# 処理オブジェクト(self.proc_w)に入力pathを伝える
	def setiPath2proc(self):
		if hasattr(self.proc_w, 'setiPath'):
			iPath=self.iFile_w.path
			self.proc_w.setiPath(iPath)

	# 処理オブジェクト(self.proc_w)に参照ファイルを伝える
	def setoPath2proc(self):
		if hasattr(self.proc_w, 'setoPath'):
			oPath=self.oPath_w.path
			self.proc_w.setoPath(oPath) # 処理オブジェクトに参照ファイルを伝える

	def iFile_h(self,files):
		if len(files)==0:
			return

	def mFile_h(self,files):
		if len(files)==0:
			return

	def widget(self):
		### iFileBox
		if_config={
			"multiSelect":True,
			"property":True,
			"propertyRows":20,
			"actionHandler":None,
			"actionTitle":"選択"
	  }
		self.iFile_w=fileBrowser_w(self.path,if_config)

		### mFileBox
		mf_config={
			"multiSelect":False,
			"property":True,
			"propertyRows":20,
			"actionHandler":None,
			"actionTitle":"選択"
	  }
		self.mFile_w=fileBrowser_w(self.path,mf_config)

		### oFileBox
		of_config={
			"multiSelect":False,
			"property":True,
			"propertyRows":100,
			"actionHandler":None,
			"delHandler":True,
			"newHandler":True
	   }
		self.oPath_w=fileBrowser_w(self.path,of_config)

		# ボタン系
		self.procSel_w=widgets.Dropdown(description="処理",options=self.tools,layout=Layout(width='50%'))
		self.procSel_w.observe(self.proc_h,names="value") # HANDLER
		updButton_w=widgets.Button(description="更新",layout=Layout(width='70px'))
		updButton_w.on_click(self.upd_h)
		exeButton_w=widgets.Button(description="スクリプト生成",layout=Layout(width='160px'))
		exeButton_w.style.button_color = 'lightgreen'
		exeButton_w.on_click(self.exe_h)
		self.deepOutput_w=widgets.Checkbox(value=False, description='deep output',disabled=True)
		self.buttons_w=widgets.HBox([self.procSel_w,updButton_w,exeButton_w,self.deepOutput_w])

		self.blank_w =widgets.Label(value="no method selected")

		self.procBox_w=widgets.VBox([self.buttons_w,self.blank_w])

		# スクリプト出力
		self.script_w =widgets.Textarea(value="",rows=15,layout=Layout(width='100%'),disabled=False)

		# 出力系スクリプト出力
		self.output_w =widgets.Textarea(value="",rows=15,layout=Layout(width='100%'),disabled=False)


		### tabコンテナ
		children=[]
		children.append(self.iFile_w.widget())
		children.append(self.mFile_w.widget())
		children.append(self.oPath_w.widget())
		children.append(self.procBox_w)
		children.append(self.script_w)
		children.append(self.output_w)
		self.tab = widgets.Tab()
		self.tab.children = children
		self.tab.set_title(0, "入力")
		self.tab.set_title(1, "参照")
		self.tab.set_title(2, "出力パス")
		self.tab.set_title(3, "処理")
		self.tab.set_title(4, "スクリプト")
		self.tab.set_title(5, "出力系スクリプト")

		# メッセージ窓
		self.msg_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		box=widgets.VBox([self.msg_w,self.tab])
		return box


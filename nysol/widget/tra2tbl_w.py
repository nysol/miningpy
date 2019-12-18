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
class tra2tbl_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w):
		params={}
		params["iFile"]= self.iName_w.value
		params["oPath"]= self.oPath_w.value
		params["oFile"]= self.oFile_w.value

		if not wlib.iFileCheck(params["iFile"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oFile"],"出力ファイル名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		params["tid"] = self.tid_w.getValue()
		params["item"] = self.item_w.getValue()
		params["agg"]  = self.agg_w.getValue()
		params["klass"]= self.klass_w.getValue()
		params["null"]= self.null_w.value
		params["dummy"]= self.dummy_w.value
		params["stat"]= self.stat_w.value

		script1=wlib.readSource("nysol.mining.tra2tbl")
		script2="""
print("#### START")

iFile="{iFile}"
oFile="{oPath}/{oFile}"
tidFld="{tid}"
itemFld="{item}"
null={null}
dummy={dummy}
aggFld="{agg}"
aggStat="{stat}"
klassFld="{klass}"

tra2tbl(iFile,oFile,tidFld,itemFld,null=null,dummy=dummy,aggFld=aggFld,aggStat=aggStat,klassFld=klassFld)
print("#### END")
""".format(**params)

		script_w.value = script1+script2
		return True

	def setiFile(self,iFiles,propText):
		# parameter設定tabに反映
		iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.iName_w.value=iFile
		self.iText_w.value=propText # ファイル内容
		if iFile is None or not os.path.isfile(iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(iFile)
		self.tid_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))
		self.agg_w.addOptions(copy.copy(fldNames))
		self.klass_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	def widget(self):
		pbox=[]
		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='100%'),disabled=False)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=False)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

		# key 項目
		config_tid={
			"options":[],
			"title":"トランザクションID項目",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.tid_w=selfield_w(config_tid)

		# item 項目
		config_item={
			"options":[],
			"title":"アイテム項目",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.item_w=selfield_w(config_item)
		pbox.append(widgets.HBox([self.tid_w.widget(),self.item_w.widget()]))

		# 集計 項目
		config_agg={
			"options":[],
			"title":"集計項目",
			"rows":5,
			"blank":True,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.agg_w=selfield_w(config_agg)
	
		# クラス項目
		config_klass={
			"options":[],
			"title":"目的変数項目",
			"rows":5,
			"blank":True,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.klass_w=selfield_w(config_klass)
		pbox.append(widgets.HBox([self.agg_w.widget(),self.klass_w.widget()]))

		# その他パラメータ
		self.null_w=widgets.Text(description="nullの置換値",value="0",style={'description_width': 'initial'})
		self.dummy_w=widgets.Checkbox(value=True, description='dummy化(アイテムが存在するかどうかの0/1)',style={'description_width': 'initial'})
		statsList=["sum", "mean", "count", "ucount", "devsq", "var", "uvar", "sd", "usd", "USD", "cv", "min", "qtile1", "median", "qtile3", "max", "range", "qrange", "mode", "skew", "uskew", "kurt", "ukurt"]
		self.stat_w=widgets.Dropdown(description="統計量",options=statsList, value='sum', disabled=False)
		pbox.append(widgets.VBox([self.null_w,self.dummy_w,self.stat_w]))

		box=widgets.VBox(pbox)
		return box


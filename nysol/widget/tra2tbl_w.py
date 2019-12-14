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

		self.iFile=None
		self.oPath=None
		self.oFile=None

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		if self.iFile is None:
			self.parent.msg_w.value = "##ERROR: 入力ファイルが指定されていません。"
			return False
		if not os.path.isfile(self.iFile):
			self.parent.msg_w.value = "##ERROR: 入力にはcsvファイルを指定して下さい。"
			return False
		if self.oPath is None:
			self.parent.msg_w.value = "##ERROR: 出力パスが指定されていません。"
			return False
		if not os.path.isdir(self.oPath):
			self.parent.msg_w.value = "##ERROR: 出力dirにはディレクトリを指定して下さい。"
			return False

		params={}
		params["iFile"]= self.iFile
		params["oPath"]= self.oPath
		params["oFile"]= self.oFile_w.value
		params["tid"] = self.tid_w.getValue()
		params["item"] = self.item_w.getValue()
		params["agg"]  = self.agg_w.getValue()
		params["klass"]= self.klass_w.getValue()
		params["null"]= self.null_w.value
		params["dummy"]= self.dummy_w.value
		params["stat"]= self.stat_w.value

		if params["oFile"]=="":
			self.parent.msg_w.value="##ERROR: 出力ファイル名が入力されていません"
			return False

		script1=wlib.readSource("nysol.mining.tra2tbl")
		script2="""
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
""".format(**params)

		script_w.value = script1+script2
		return True




		params={}
		params["key"]=self.key_w.getValue()
		params["fld"]=self.field_w.getValue()
		params["val"]=self.value_w.value
		params["newName"]=self.newfld_w.value

		params["reverse"]=self.reverse_w.value
		params["reverse_r"]=not params["reverse"]
		oFile=self.oFile_w.value
		if oFile=="":
			self.parent.msg_w.value="##ERROR: 出力ファイルが入力されていません"
			return False
		params["oFile"]=self.oPath+"/"+oFile
		params["iFile"]=self.iFile
		
		if params["val"]=="":
			self.parent.msg_w.value="##ERROR: 「値」が入力されていません。"
			return False

		if params["newName"]=="":
			self.parent.msg_w.value="##ERROR: 「クラス名」が入力されていません。"
			return False

		_head=self.head_w.value
		_tail=self.tail_w.value
		if _head and _tail:
			sub=False
			head=False
			tail=False
		elif _head:
			sub=False
			head=True
			tail=False
		elif _tail:
			sub=False
			head=False
			tail=True
		else:
			sub=True
			head=False
			tail=False
		params["sub"]=sub
		params["head"]=head
		params["tail"]=tail

		script="""
klass=None
klass<<=nm.mselstr(k='{key}',f='{fld}',v='{val}',r={reverse},head={head},tail={tail},sub={sub},i='{iFile}')
klass<<=nm.msetstr(v='1',a='{newName}')
klass<<=nm.mcut(f='{key},{newName}')
klass<<=nm.muniq(k='{key},{newName}')

f=None
f<<=nm.mjoin(k='{key}',m=klass,f='{newName}',n=True,i='{iFile}')
f<<=nm.mselstr(f='{fld}',v='{val}',r={reverse_r},head={head},tail={tail},sub={sub})
f<<=nm.mnullto(f='{newName}',v='0',o='{oFile}')
f.run()
""".format(**params)

		header="""
#################################
# mselstr_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		lib="""
import nysol.mcmd as nm
nm.setMsgFlg(True)
"""
		output="""
# ファイル出力された結果
oFile="%s"
"""%(oFile)

		# script tabにセット
		script_w.value = header+lib+script

		# outputscript tabにセット
		output_w.value = output

		return True

	def setiFile(self,iFiles,propText):
		self.iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText

		# parameter設定tabに反映
		self.iName_w.value=self.iFile
		self.iText_w.value=self.propText # ファイル内容
		if self.iFile is None or not os.path.isfile(self.iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.iFile)
		self.tid_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))
		self.agg_w.addOptions(copy.copy(fldNames))
		self.klass_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

	def widget(self):
		pbox=[]
		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='100%'),disabled=True)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=True)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

		# key 項目
		config_tid={
			"options":[],
			"title":"traID項目",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.tid_w=selfield_w(config_tid)

		# item 項目
		config_item={
			"options":[],
			"title":"アイテム",
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
			"title":"クラス項目",
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


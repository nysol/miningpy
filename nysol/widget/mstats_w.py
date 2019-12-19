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
class mstats_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def help(self):
		return """sum:合計, mean:算術平均, count:件数, ucount:件数-1, devsq:偏差平方和, "var":分散, "uvar":不偏分散
sd:標準偏差, usd:不偏標準偏差, USD:, cv:変動係数, min:最小値, qtile1:第一四分位点, median:中央値
qtile3:第三四分位点, max:最大値, range:max-min, qrange:qtile3-qtile1, mode:最頻値, skew:歪度,
uskew:不偏歪度, kurt:尖度, ukurt:不偏尖度
"""

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

		key=self.key_w.getValue()
		field=self.field_w.getValue()
		stat=self.stat_w.value
		newfld=self.newfld_w.value

		flds=[]
		if key!="":
			flds.append(key)
		flds.append(field)
		params1="f='%s',i='%s'"%(",".join(flds),params["iFile"])
		
		params2=""
		if key!="":
			params2+="k='%s'"%(key)
		if newfld=="":
			params2+=",f='%s'"%(field)
		else:
			params2+=",f='%s:%s'"%(field,newfld)
		params2+=",c='%s',o='%s/%s'"%(stat,params["oPath"],params["oFile"])

		header="""
#################################
# mstats_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		lib="""
import nysol.mcmd as nm
nm.setMsgFlg(True)
print("#### START")
"""
		script="""
f=None
f<<=nm.mcut(%s)
f<<=nm.mstats(%s)
f.run(msg='on')
print("#### END")
"""%(params1,params2)

		script_w.value = header+lib+script
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
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	def widget(self):
		pbox=[]
		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="file name",value="",layout=Layout(width='100%'),disabled=False)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

		# key 項目
		config_k={
			"options":[],
			"title":"集計単位の項目",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":False,
			"message":None
		}
		self.key_w=selfield_w(config_k)

		# field 項目
		config_f={
			"options":[],
			"title":"集計対象の項目",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.field_w=selfield_w(config_f)
		pbox.append(widgets.HBox([self.field_w.widget(),self.key_w.widget()]))

		# 新項目名
		self.newfld_w=widgets.Text(description="出力項目名",value="",layout=Layout(width='300px'))
		newfldL_w=widgets.Label(value="指定しなければ集計対象項目名と同じ名前になる",disabled=True)
		pbox.append(widgets.HBox([self.newfld_w,newfldL_w]))

		# 統計量
		statsList=["sum", "mean", "count", "ucount", "devsq", "var", "uvar", "sd", "usd", "USD", "cv", "min", "qtile1", "median", "qtile3", "max", "range", "qrange", "mode", "skew", "uskew", "kurt", "ukurt"]
		self.stat_w=widgets.Dropdown(description="統計量",options=statsList, value='sum', disabled=False)
		pbox.append(self.stat_w)

		help_w=widgets.Textarea(value=self.help(),rows=4,layout=Layout(width='100%'),disabled=True)
		pbox.append(help_w)

		box=widgets.VBox(pbox)
		return box


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
class mcount_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

		self.iFile=None
		self.oPath=None
		self.oFile=None

	def help(self):
		return """sum:合計, mean:纂述平均, count:件数, ucount:件数-1, devsq:偏差平方和, "var":分散, "uvar":不偏分散
sd:標準偏差, usd:不偏標準偏差, USD:, cv:変動係数, min:最小値, qtile1:第一四分位点, median:中央値
qtile3:第三四分位点, max:最大値, range:max-min, qrange:qtile3-qtile1, mode:最頻値, skew:歪度,
uskew:不偏歪度, kurt:尖度, ukurt:不偏尖度
"""

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		key=self.key_w.getValue()
		newfld=self.newfld_w.value
		oFile=self.oFile_w.value
		if oFile=="":
			self.parent.msg_w.value="##ERROR: 出力ファイルが入力されていません"
			return False
		oFile=self.oPath+"/"+oFile

		flds=[]
		flds.append(key)
		flds.append(field)
		params1="f='%s',i='%s'"%(",".join(flds),self.iFile)
		
		params2=""
		if key!="":
			params2+="k='%s'"%(key)
		if newfld=="":
			params2+=",f='%s'"%(field)
		else:
			params2+=",f='%s:%s'"%(field,newfld)
		params2+=",c='%s',o='%s'"%(stat,oFile)

		header="""
#################################
# mstats_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		lib="""
import nysol.mcmd as nm
"""
		script="""
f=None
f<<=nm.mcut(%s)
f<<=nm.mstats(%s)
f.run(msg='on')
"""%(params1,params2)

		output="""
# ファイル出力された結果
oFile="%s"
"""%(self.oFile)

		# script tabにセット
		script_w.value = header+lib+script

		# outputscript tabにセット
		output_w.value = output

		return True

	def setiFile(self,iFiles,propText):
		self.iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText

		# parameter設定tabに反映
		self.fName_w.value=self.iFile
		self.fText_w.value=self.propText # ファイル内容
		if self.iFile is None or not os.path.isfile(self.iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.iFile)
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

	def widget(self):
		pbox=[]
		# ファイル名とファイル内容
		self.fName_w =widgets.Text(description="file name",value="",layout=Layout(width='100%'),disabled=True)
		self.fText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.fName_w)
		pbox.append(self.fText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=True)
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


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
	def __init__(self,iPath,oFile):
		self.version="0.10"
		self.date=datetime.now()

		clear_output() # jupyter上の出力領域のクリア
		self.iPath=os.path.abspath(os.path.expanduser(iPath))
		self.oFile=os.path.abspath(os.path.expanduser(oFile))
		self.oPath=os.path.dirname(self.oFile)
		os.makedirs(self.oPath, exist_ok=True)

	def help(self):
		return """sum:合計, mean:纂述平均, count:件数, ucount:件数-1, devsq:偏差平方和, "var":分散, "uvar":不偏分散
sd:標準偏差, usd:不偏標準偏差, USD:, cv:変動係数, min:最小値, qtile1:第一四分位点, median:中央値
qtile3:第三四分位点, max:最大値, range:max-min, qrange:qtile3-qtile1, mode:最頻値, skew:歪度,
uskew:不偏歪度, kurt:尖度, ukurt:不偏尖度
"""

	def exe_h(self,b):
		key=self.key_w.getValue()
		field=self.field_w.getValue()
		stat=self.stat_w.value
		newfld=self.newfld_w.value

		flds=[]
		if key!="":
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
		params2+=",c='%s',o='%s'"%(stat,self.oFile)

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
		self.script_w.value = header+lib+script

		# outputscript tabにセット
		self.output_w.value = output

		# 出力path画面に移動
		self.tab.selected_index = 2

	def getHeader(self,csv):
		flds=None
		with open(csv) as f:
			line=f.readline()
		if line:
			flds=line.strip().split(",")
		return flds

	def iFile_h(self,files):
		if len(files)==0:
			return
		# parameter設定tabに反映
		self.iFile=files[0] # ファイル名表示
		self.fName_w.value=self.iFile
		self.fText_w.value=self.iFile_w.propText() # ファイル内容

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.fName_w.value)
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

		# parameters画面に移動
		self.tab.selected_index = 1

	def widget(self):
		### iFileBox
		if_config={
			"multiSelect":False,
			"property":True,
			"propertyRows":20,
			"actionHandler":self.iFile_h,
			"actionTitle":"選択"
	  }
		self.iFile_w=fileBrowser_w(self.iPath,if_config)

		### oFileBox
		of_config={
			"multiSelect":False,
			"property":True,
			"propertyRows":100,
			"actionHandler":None
	   }
		self.oPath_w=fileBrowser_w(self.oPath,of_config)

		# ボタン系
		exeButton_w=widgets.Button(description="スクリプト生成")
		exeButton_w.style.button_color = 'lightgreen'
		exeButton_w.on_click(self.exe_h)
		buttons_w=widgets.HBox([exeButton_w])

		# parameters
		pbox=[]

		# ファイル名とファイル内容
		self.fName_w =widgets.Text(description="file name",value="",layout=Layout(width='100%'),disabled=True)
		self.fText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.fName_w)
		pbox.append(self.fText_w)

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

		paramBox=widgets.VBox(pbox)

		# スクリプト出力
		self.script_w =widgets.Textarea(value="",rows=15,layout=Layout(width='100%'),disabled=False)

		# 出力系スクリプト出力
		self.output_w =widgets.Textarea(value="",rows=15,layout=Layout(width='100%'),disabled=False)

		### tabコンテナ
		children=[]
		children.append(self.iFile_w.widget())
		children.append(paramBox)
		children.append(self.script_w)
		children.append(self.output_w)
		children.append(self.oPath_w.widget())
		self.tab = widgets.Tab()
		self.tab.children = children
		self.tab.set_title(0, "入力ファイル選択")
		self.tab.set_title(1, "統計量の計算")
		self.tab.set_title(2, "基本スクリプト")
		self.tab.set_title(3, "出力系スクリプト")
		self.tab.set_title(4, "出力パスブラウザ")

		# メッセージ窓
		self.msg_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		box=widgets.VBox([buttons_w,self.msg_w,self.tab])
		return box


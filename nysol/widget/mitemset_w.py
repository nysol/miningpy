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

####################################################################
class mitemset_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w):
		params={}
		params["version"]=self.version
		params["date"]=self.date
		params["iFile"]= self.iName_w.value
		params["oPath"]= self.oPath_w.value
		params["oDir"] = self.oDir_w.value

		if not wlib.iFileCheck(params["iFile"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oDir"],"出力dir名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		params["tid"]   =self.traID_w.getValue()
		params["item"]  =self.item_w.getValue()
		params["klass"] =self.class_w.getValue()
		params["pType"] =self.type_w.value[0] # 0は先頭文字の(F,C,M)
		params["minSup"]=self.minSup_w.value
		params["maxSup"]=self.maxSup_w.value
		params["minLen"]=self.minLen_w.value
		params["maxLen"]=self.maxLen_w.value
		params["minGR"] =self.minGR_w.value
		params["top"]   =self.top_w.value

		if params["item"]==params["tid"]:
			self.parent.msg_w.value="##ERROR: トランザクションIDとアイテム項目が同じ項目になってます"
			return False

		script="""
#################################
# mitemset_w.pyの自動生成スクリプト
# version: {version}
# 実行日時: {date}
#################################
import os
import nysol.take as nt
import nysol.mcmd as nm
nm.setMsgFlg(True)
print("#### START")

########### parameter設定
traFile="{iFile}" # トランザクションファイル名
oPath="{oPath}/{oDir}" # 出力ディレクトリ名
tid="{tid}" # トランザクションID項目
item="{item}" # アイテム項目
klass="{klass}" # クラス項目
pType="{pType}" # パターンタイプ(F:頻出集合,C:飽和集合,M:極大集合)
minSup={minSup} # minimum support
maxSup={maxSup} # maximum support
minLen={minLen} # minimum length of items
maxLen={maxLen} # maximum length of items
minGR={minGR} # minimum post-probability (klass指定時のみ有効)
top={top} # 抽出上位件数(supportの大きい順)

os.makedirs(oPath,exist_ok=True)

nt.mitemset(i=traFile,
				cls=klass,
				tid=tid,
				item=item,
				O=oPath,
				type=pType,
				s=minSup,
				sx=maxSup,
				l=minLen,
				u=maxLen,
				p=minGR,
				top=top).run()
print("#### END")
""".format(**params)

		# script tabにセット
		script_w.value = script
		return True

	def setiFile(self,iFiles,propText):
		# parameter設定tabに反映
		iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.iName_w.value=iFile
		self.iText_w.value=propText
		if iFile is None or not os.path.isfile(iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(iFile)
		self.traID_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))
		self.class_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	#  type= : 抽出するパターンの型【オプション:default:F, F:頻出集合, C:飽和集合, M:極大集合】
	#  s=    : 最小支持度(全トランザクション数に対する割合による指定)【オプション:default:0.05, 0以上1以下の実数】
	#  S=    : 最小支持度(件数による指定)【オプション】
	#  sx=   : 最大支持度(support)【オプション:default:1.0, 0以上1以下の実数】
	#  Sx=   : 最大支持件数【オプション】
	#  l=    : パターンサイズの下限(1以上20以下の整数)【オプション:default:制限なし】
	#  u=    : パターンサイズの上限(1以上20以下の整数)【オプション:default:制限なし】
	#  p=    : 最小事後確率【オプション:default:0.5】
	#  g=    : 最小増加率【オプション】
	#  top=  : 列挙するパターン数の上限【オプション:default:制限なし】*2
	def widget(self):
		pbox=[]

		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="トランザクション",value="",layout=Layout(width='99%'),disabled=False)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oDir_w =widgets.Text(description="ディレクトリ名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oDir_w)

		# traID 項目
		config_t={
			"options":[],
			"title":"トランザクションID",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.traID_w=selfield_w(config_t)

		# item 項目
		config_i={
			"options":[],
			"title":"アイテム項目",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.item_w=selfield_w(config_i)

		# class 項目
		config_c={
			"options":[],
			"title":"目的変数項目",
			"rows":5,
			"blank":True,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.class_w=selfield_w(config_c)
		pbox.append(widgets.HBox([self.traID_w.widget(),self.item_w.widget(),self.class_w.widget()]))

		# 各種しきい値
		self.type_w=widgets.RadioButtons(options=['F:頻出集合', 'C:飽和集合', 'M:極大集合'],
				value='F:頻出集合', description='type:', disabled=False)
		pbox.append(self.type_w)

		self.minSup_w=widgets.FloatSlider(description='minSup', value=0.01, min=0.0, max=1.0, step=0.01)
		self.maxSup_w=widgets.FloatSlider(description='maxSup', value=1.0, min=0.0, max=1.0, step=0.01)
		pbox.append(widgets.HBox([self.minSup_w,self.maxSup_w]))

		self.minLen_w=widgets.IntSlider(description='minLen', value=1, min=1, max=10, step=1)
		self.maxLen_w=widgets.IntSlider(description='maxLen', value=10, min=1, max=10, step=1)
		pbox.append(widgets.HBox([self.minLen_w,self.maxLen_w]))

		self.minGR_w=widgets.FloatSlider(description='minGR', value=1.2, min=1.1, max=20.0, step=0.2)
		pbox.append(self.minGR_w)

		self.top_w=widgets.IntSlider(description='top', value=1000, min=1, max=10000, step=1)
		pbox.append(self.top_w)

		box=widgets.VBox(pbox)
		return box


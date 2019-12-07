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

		self.iFile=None
		self.oPath=None
		self.oFile=None

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		traFile=self.traFile
		tid=self.traID_w.getValue()
		item=self.item_w.getValue()
		klass=self.class_w.getValue()
		oPath=self.oPath
		pType=self.type_w.value[0] # 0は先頭文字の(F,C,M)
		minSup=self.minSup_w.value
		maxSup=self.maxSup_w.value
		minLen=self.minLen_w.value
		maxLen=self.maxLen_w.value
		minPpr=self.minPpr_w.value
		top=self.top_w.value

		header="""
#################################
# mitemset_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		lib="""
import nysol.take as nt
import nysol.mcmd as nm
nm.setMsgFlg(True)
"""

		params="""
########### parameter設定
traFile="%s" # トランザクションファイル名
oPath="%s" # 出力ディレクトリ名
tid="%s" # トランザクションID項目
item="%s" # アイテム項目
klass="%s" # クラス項目
pType="%s" # パターンタイプ(F:頻出集合,C:飽和集合,M:極大集合)
minSup=%f # minimum support
maxSup=%f # maximum support
minLen=%d # minimum length of items
maxLen=%d # maximum length of items
minPpr=%f # minimum post-probability (klass指定時のみ有効)
top=%d # 抽出上位件数(supportの大きい順)
"""%(
		self.traFile,
		self.oPath,
		self.traID_w.getValue(),
		self.item_w.getValue(),
		self.class_w.getValue(),
		self.type_w.value[0],
		self.minSup_w.value,
		self.maxSup_w.value,
		self.minLen_w.value,
		self.maxLen_w.value,
		self.minPpr_w.value,
		self.top_w.value
)

		script="""
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
				p=minPpr,
				top=top).run()
"""

		# 出力系
		output="""
import pandas as pd

# ファイル出力された結果
# 頻出アイテム集合
patternCSV="%s/patterns.csv"
tid_patsCSV="%s/tid_pats.csv"

# パターン件数
outCount=len(open("%s/patterns.csv").readlines())
print(outCount)

pattern=pd.read_csv(patternCSV)
tid_pats=pd.read_csv(tid_patsCSV)
pattern
"""%(self.oPath,self.oPath,self.oPath)

		# script tabにセット
		script_w.value = header+lib+params+script

		# outputscript tabにセット
		output_w.value = output

		return True

	def setiFile(self,iFiles,propText):
		self.traFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText

		# parameter設定tabに反映
		self.traFile_w.value=self.traFile
		self.traFileTxt_w.value=self.propText

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.traFile)
		self.traID_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))
		self.class_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

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
		self.traFile_w =widgets.Text(description="トランザクション",value="",layout=Layout(width='99%'),disabled=True)
		self.traFileTxt_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.traFile_w)
		pbox.append(self.traFileTxt_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=True)
		pbox.append(self.oPath_w)

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
			"title":"クラス項目",
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

		self.minPpr_w=widgets.FloatSlider(description='minPpr', value=0.5, min=0.0, max=1.0, step=0.01)
		pbox.append(self.minPpr_w)

		self.top_w=widgets.IntSlider(description='top', value=1000, min=1, max=10000, step=1)
		pbox.append(self.top_w)

		box=widgets.VBox(pbox)
		return box


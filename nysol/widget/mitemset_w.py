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
	def __init__(self,iPath,oPath):
		self.version="0.10"
		self.date=datetime.now()

		clear_output() # jupyter上の出力領域のクリア
		self.iPath=os.path.abspath(os.path.expanduser(iPath))
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		os.makedirs(self.oPath, exist_ok=True)

	def exe_h(self,b):
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
from datetime import datetime
import nysol.take as nt
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
print("## START",datetime.now())
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
print("## END",datetime.now())
"""

		# 出力系
		output="""
import nysol.mining.dataset as ds

# ファイル出力された結果
# 頻出アイテム集合
patternCSV="%s/patterns.csv"
tid_patsCSV="%s/tid_pats.csv"

# パターン件数
outCount=len(open("%s/patterns.csv").readlines())
print(outCount)

# pid,size,count,total,support,lift,pattern
# 0,1,4550,20177,0.2255042871,1,生ビール（中）
# 1,1,3450,20177,0.1709867671,1,ご飯
pConfig={}
pConfig["type"]="table"
pConfig["names"]=["pid","size","count","total","support","lift","pattern"]
pConfig["convs"]=["id()","as('int64')","as('int64')","numeric()","numeric()","as('object')"]
pattern=ds.mkTable(pConfig,patternCSV)

# traID,pid
# 1,912
tConfig={}
tConfig["type"]="table"
tConfig["names"]=["traID","pid"]
tConfig["convs"]=["id()","as('object')"]
tid_pats=ds.mkTable(tConfig,tid_patsCSV)
"""%(self.oPath,self.oPath,self.oPath)

		# script tabにセット
		self.script_w.value = header+lib+params+script

		# outputscript tabにセット
		self.output_w.value = output

		# 出力path画面に移動
		self.tab.selected_index = 2

	def iFile_h(self,files):
		if len(files)==0:
			return
		# parameter設定tabに反映
		self.traFile=files[0] # ファイル名表示
		self.traFile_w.value=self.traFile
		self.traFileTxt_w.value=self.iFile_w.propText() # ファイル内容

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.fName_w.value)
		self.traID_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))
		self.class_w.addOptions(copy.copy(fldNames))

		# parameters画面に移動
		self.tab.selected_index = 1

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
			"actionHandler":None,
			"actionTitle":"選択"
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
		self.traFile_w =widgets.Text(description="トランザクション",value="",layout=Layout(width='99%'),disabled=True)
		self.traFileTxt_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.traFile_w)
		pbox.append(self.traFileTxt_w)

		# 出力パス名
		oName_w =widgets.Text(description="出力パス",value=self.oPath,layout=Layout(width='100%'),disabled=True)
		pbox.append(oName_w)

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
		self.tab.set_title(0, "トランザクション")
		self.tab.set_title(1, "アイテム集合列挙")
		self.tab.set_title(2, "基本スクリプト")
		self.tab.set_title(3, "出力系スクリプト")
		self.tab.set_title(4, "出力パスブラウザ")

		# メッセージ窓
		self.msg_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		box=widgets.VBox([buttons_w,self.msg_w,self.tab])
		return box


#!/usr/bin/env python
# coding: utf-8
import warnings
warnings.simplefilter("ignore")
#from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from ipywidgets import Button, Layout, Label
import os
import json
from datetime import datetime
from IPython.display import clear_output

from nysol.widget.fileBrowser_w import fileBrowser_w
from nysol.widget.selfield_w import selfield_w

####################################################################
class ctree_w(object):
	def __init__(self,iPath,oPath):
		self.version="0.10"
		self.date=datetime.now()

		clear_output() # jupyter上の出力領域のクリア
		self.iPath=os.path.abspath(os.path.expanduser(iPath))
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		os.makedirs(self.oPath, exist_ok=True)

	def exe_h(self,b):
		id_  = self.id_w.getValue(),
		y    = self.y_w.getValue(),
		nums = self.num_w.getValue(),
		cats = self.cat_w.getValue(),

		if len(nums[0])+len(cats[0])==0:
			self.msg_w.value = "##ERROR: 入力変数が一つも指定されていません。"
			return

		# dataset生成config
		config={}
		config["type"]="table"
		names=[]
		convs=[]
		if id_[0]!="":
			names.append(id_[0])
			convs.append("id()")
		for num in nums[0]:
			if num!="":
				names.append(num)
				convs.append("numeric()")
		for cat in cats[0]:
			if cat!="":
				names.append(cat)
				convs.append("dummy()")
		names.append(y[0])
		convs.append("category()")
		config["names"]=names
		config["convs"]=convs

		# model生成config
		modelConfig={}
		modelConfig["min_samples_leaf"]=self.minSamplesLeaf_w.value

		header="""
#################################
# ctree_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		lib="""
from datetime import datetime
import nysol.mining.dataset as ds
from nysol.mining.ctree import ctree
"""

		params="""
########### parameter設定
# 入力ファイル名
iFile="%s"
# データ辞書
config=%s
# 出力ディレクトリ名
oPath="%s"
# 出力変数名
y="%s"
"""%(
		self.iFile,
		config,
		self.oPath,
		self.y_w.getValue(),
)
		script="""
print("## START",datetime.now())
# CSVからpandasオブジェクトを生成する
# csvをpandas DataFrameに変換
dat=ds.mkTable(config,iFile)

# nullデータ行を削除して、x,yをセット
dat=dat.dropna()
dat_y=ds.cut(dat,[y])
dat_x=ds.cut(dat,[y],reverse=True)

# モデル構築
# 設定可能なパラメータは次のURLを参照のこと
# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
# リーフ最小サンプル数(0.0でCVによる最適値を探索する)
modelConfig=%s
model=ctree(dat_x,dat_y,modelConfig)
model.build()

# モデル視覚化&保存
model.visualize()
model.save(oPath)

# 予測&評価&保存
pred=model.predict(dat_x)
pred.evaluate(dat_y)
pred.save(oPath)

print("## END",datetime.now())
"""%(modelConfig)

		# 出力系
		output="""
# ファイル出力されたチャート
from IPython.display import Image, display_png
display_png(Image("%s")) # confusion_matrix
display_png(Image("%s")) # ROC曲線
display_png(Image("%s")) # 決定木(画像)

# データセット(pandas.DataFrame)
dat

# 決定木モデル(sklearn.tree.DecisionTreeClassifier)
# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
model.model

pred.y_true # y (list)
pred.y_pred # y予測値 (list)
pred.values # モデル評価
pred.charts # モデル評価(チャート)

"""%(
		"%s/confusion_matrix.png"%self.oPath,
		"%s/roc_chart.png"%self.oPath,
		"%s/tree.png"%self.oPath
)

		# script tabにセット
		self.script_w.value = header+lib+params+script

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
		fldNames=self.getHeader(self.iFile)
		self.id_w.addOptions(fldNames)
		self.y_w.addOptions(fldNames)
		self.num_w.addOptions(fldNames)
		self.cat_w.addOptions(fldNames)

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

		# ボタン系
		exeButton_w=widgets.Button(description="実行")
		exeButton_w.style.button_color = 'lightgreen'
		exeButton_w.on_click(self.exe_h)
		buttons_w=widgets.HBox([exeButton_w])

		# parameters
		pbox=[]

		# 入力ファイル名とファイル内容
		self.fName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='99%'),disabled=True)
		self.fText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.fName_w)
		pbox.append(self.fText_w)

		# 出力パス名
		oName_w =widgets.Text(description="出力パス",value=self.oPath,layout=Layout(width='100%'),disabled=True)
		pbox.append(oName_w)

		# id 項目
		config={
			"options":[],
			"title":"id項目(指定しなくても良い)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":False,
			"message":None
		}
		self.id_w=selfield_w(config)
		config={}
	
		# 数値変数 項目
		config={
			"options":[],
			"title":"数値変数(複数選択可)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":True,
			"message":None
		}
		self.num_w=selfield_w(config)

		# cat変数 項目
		config={
			"options":[],
			"title":"カテゴリ変数(複数選択可)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":True,
			"message":None
		}
		self.cat_w=selfield_w(config)

		# y 項目
		config={
			"options":[],
			"title":"出力変数",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.y_w=selfield_w(config)
		pbox.append(widgets.HBox([self.id_w.widget(),self.y_w.widget()]))
		pbox.append(widgets.HBox([self.num_w.widget(),self.cat_w.widget()]))

		# 各種しきい値
		self.minSamplesLeaf_w=widgets.FloatSlider(description='枝刈度', value=0.0, min=0.0, max=0.5, step=0.01, disabled=False, orientation='horizontal')
		label=widgets.Textarea(rows=3,disabled=True,layout=Layout(width="65%"),
    value=
"""枝刈度にはリーフの最小サンプル数(min_samples_leaf)を利用する。
値は、全サンプル数に対する割合で指定する(min_samples_leaf=(0.0,0.5])。
0.0に設定すると、cross-validationでテスト誤差最小の枝刈度を自動選択する。
""")
		pbox.append(widgets.VBox([label, self.minSamplesLeaf_w]))
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
		self.tab = widgets.Tab()
		self.tab.children = children
		self.tab.set_title(0, "入力ファイル選択")
		self.tab.set_title(1, "決定木パラメータ")
		self.tab.set_title(2, "基本スクリプト")
		self.tab.set_title(3, "出力系スクリプト")
		#self.tab.set_title(2, "output")
		# メッセージ窓
		self.msg_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		box=widgets.VBox([buttons_w,self.msg_w,self.tab])
		return box


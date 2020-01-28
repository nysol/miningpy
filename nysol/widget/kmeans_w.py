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
class kmeans_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w):
		params={}
		params["iFile"]= self.iName_w.value
		params["oPath"]= self.oPath_w.value
		params["oDir"] = self.oDir_w.value

		if not wlib.iFileCheck(params["iFile"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oDir"],"出力dir名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		#params["_id"]  =self.id_w.getValue()
		params["x"]    =list(self.x_w.getValue())
		params["algo"] =self.algo_w.value
		params["k"]    =self.k_w.value

		#if params["_id"] in params["x"]:
		#	self.parent.msg_w.value="##ERROR: idと入力変数が重複指定されています"
		#	return False
		if not wlib.blankCheck(params["k"],"クラスタ数",self.parent.msg_w):
			return False

		header="""
#################################
# mitemset_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		script="""
import os
import csv
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from yellowbrick.cluster import InterclusterDistance
print("#### START")

########### parameter設定
iFile="{iFile}" # 入力CSVファイル名
x={x} # 入力変数
oPath="{oPath}" # 出力パス
oDir="{oDir}" # 出力ディレクトリ名
algo="{algo}" # クラスタリングアルゴリズム
k={k} # クラスタ数

print("## データセット作成中...")
# 出力ディレクトリを作成する
os.makedirs(oPath+"/"+oDir,exist_ok=True)

# CSVデータをpandas DataFrameに読み込む
df=pd.read_csv(iFile,dtype=str) # とりあえずは全項目str型として読み込む
ds=df.loc[:,x] # 入力変数のみ選択する
ds=ds.astype(float) # 全変数をfloat型に設定する

print("## クラスタリング{algo} 実行中...")
# kmeansモデルの設定と実行
model=KMeans(n_clusters=k)
pred=model.fit_predict(ds.values)

print("## 結果出力")
cluster=pd.DataFrame(pred) # 予測結果をDataFrameに
cluster.columns=["cluster"] # 項目名を設定
out=df.join(cluster) # 元のDataframeに結合する

visualizer = InterclusterDistance(model)
visualizer.fit(ds.values)
visualizer.show(outpath="{oPath}/{oDir}/interclusterDistance.png")
visualizer.show()

# CSVに出力
out.to_csv("{oPath}/{oDir}/predict.csv",index_label=None,encoding="utf-8")

print("#### END")
""".format(**params)

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
		#self.id_w.addOptions(copy.copy(fldNames))
		self.x_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	def widget(self):
		pbox=[]

		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="トランザクション",value="",layout=Layout(width='99%'),disabled=True)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oDir_w =widgets.Text(description="ディレクトリ名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oDir_w)

		# id 項目
		config_t={
			"options":[],
			"title":"サンプルID項目",
			"rows":5,
			"blank":True,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.id_w=selfield_w(config_t)

		# 入力変数項目
		config_i={
			"options":[],
			"title":"数値説明変数",
			"rows":5,
			#"blank":True,
			"width":300,
			"multiSelect":True,
			"message":None
		}
		self.x_w=selfield_w(config_i)

		pbox.append(widgets.HBox([self.x_w.widget()]))

		self.algo_w=widgets.RadioButtons(options=['k-means'],
				value='k-means', description='algorithm:', disabled=False)
		pbox.append(self.algo_w)

		self.k_w=widgets.BoundedIntText(description='クラスタ数',value=5,min=2,style={'description_width': 'initial'})
		#print("k",self.k_w.keys)
		pbox.append(self.k_w)

		box=widgets.VBox(pbox)
		return box


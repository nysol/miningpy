#!/usr/bin/env python
# coding: utf-8
import ipywidgets as widgets
import os
import copy
from datetime import datetime

from nysol.widget.fileBrowser_w import fileBrowser_w
from nysol.widget.selfield_w import selfield_w
import nysol.widget.lib as wlib

####################################################################
class rlasso_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent
		self.parent.deepOutput_w.disabled=False

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

		deepOutput=self.parent.deepOutput_w.value

		params={}
		params["iFile"]= self.iFile
		params["oPath"]= self.oPath
		params["oDir"] = self.oDir_w.value
		params["id_"]  = self.id_w.getValue()
		params["y"]    = self.y_w.getValue()
		params["nums"] = list(self.num_w.getValue())
		params["cats"] = list(self.cat_w.getValue())

		if params["oDir"]=="":
			self.parent.msg_w.value="##ERROR: 出力dirが入力されていません"
			return False

		if params["y"] in params["nums"] or params["y"] in params["cats"]:
			self.parent.msg_w.value="##ERROR: 入力変数に出力変数が含まれています:%s"%params["y"]
			return False

		if params["y"] in params["nums"] or params["y"] in params["cats"]:
			self.parent.msg_w.value="##ERROR: 入力変数に出力変数が含まれています:%s"%params["y"]
			return False

		script1=wlib.readSource("nysol.mining.rPredict","rPredict",deepOutput)
		script2=wlib.readSource("nysol.mining.rlasso","rlasso",deepOutput,["nysol.mining.rPredict"])
		script3=wlib.readSource("nysol.mining.csv2df")
		script4="""
print("#### START")
# 出力ディレクトリを作成する
os.makedirs("{oPath}"+"/"+"{oDir}",exist_ok=True)

# pandasデータを作成する
df,ds=csv2df("{iFile}", "{id_}", {nums}+["{y}"], [], {cats})

xNames=ds.columns.to_list()
xNames.remove("{y}")
y=pd.DataFrame(ds.loc[:,"{y}"])
x=ds.loc[:,xNames]

model=rlasso(x,y)

model.build()
#print("cv_minFunc",model.cv_minFun)
#print("cv_minX",model.cv_minX)
#print("score",model.score)
model.visualize()
model.save("{oPath}/{oDir}/model")

pred=model.predict(x)
pred.evaluate(y)
pred.save("{oPath}/{oDir}/pred")
print("#### END")
""".format(**params)

		script_w.value = script1+script2+script3+script4
		return True

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath


	def setiFile(self,iFiles,propText):
		self.iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText
		if self.iFile is None or not os.path.isfile(self.iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# parameter設定tabに反映
		self.fName_w.value=self.iFile
		self.fText_w.value=self.propText

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.iFile)
		self.id_w.addOptions(copy.copy(fldNames))
		self.y_w.addOptions(copy.copy(fldNames))
		self.num_w.addOptions(copy.copy(fldNames))
		self.cat_w.addOptions(copy.copy(fldNames))

	def widget(self):
		# parameters
		pbox=[]

		# 入力ファイル名とファイル内容
		self.fName_w =widgets.Text(description="入力ファイル",value="",layout=widgets.Layout(width='99%'),disabled=False)
		self.fText_w =widgets.Textarea(value="",rows=5,layout=widgets.Layout(width='99%'),disabled=True)
		pbox.append(self.fName_w)
		pbox.append(self.fText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=widgets.Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oDir_w =widgets.Text(description="出力dir名",value="",layout=widgets.Layout(width='100%'),disabled=False)
		pbox.append(self.oDir_w)

		# id 項目
		config_id={
			"options":[],
			"title":"サンプルID項目(指定しなくても良い)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":False,
			"message":None
		}
		self.id_w=selfield_w(config_id)
	
		# 数値変数 項目
		config_n={
			"options":[],
			"title":"数値説明変数(複数選択可)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":True,
			"message":None
		}
		self.num_w=selfield_w(config_n)

		# cat変数 項目
		config_c={
			"options":[],
			"title":"カテゴリ説明変数(複数選択可)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":True,
			"message":None
		}
		self.cat_w=selfield_w(config_c)

		# y 項目
		config_y={
			"options":[],
			"title":"目的変数",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.y_w=selfield_w(config_y)
		pbox.append(widgets.HBox([self.id_w.widget(),self.y_w.widget()]))
		pbox.append(widgets.HBox([self.num_w.widget(),self.cat_w.widget()]))

		# 各種しきい値
		label=widgets.Textarea(rows=3,disabled=True,layout=widgets.Layout(width="65%"),
    value=
"""
""")
		pbox.append(widgets.VBox([label]))

		box=widgets.VBox(pbox)
		return box


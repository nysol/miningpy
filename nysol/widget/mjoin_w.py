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
class mjoin_w(object):
	def __init__(self,iPath,mPath,oFile):
		self.version="0.10"
		self.date=datetime.now()

		clear_output() # jupyter上の出力領域のクリア
		self.iPath=os.path.abspath(os.path.expanduser(iPath))
		self.mPath=os.path.abspath(os.path.expanduser(mPath))
		self.oFile=os.path.abspath(os.path.expanduser(oFile))
		self.oPath=os.path.dirname(self.oFile)
		os.makedirs(self.oPath, exist_ok=True)

	def exe_h(self,b):
		iKey=self.iKey_w.getValue()
		mKey=self.mKey_w.getValue()
		field=self.field_w.getValue()
		iOuter=self.iOuter_w.value
		mOuter=self.mOuter_w.value
		
		if field=="":
			self.msg_w.value = "##ERROR: 「結合する項目」が選ばれていません。"
			return

		params=[]
		params.append("k='%s'"%(iKey))
		if mKey!="":
			params.append("K='%s'"%(mKey))
		params.append("m='%s'"%(self.mFile))
		params.append("f='%s'"%(field))
		if iOuter:
			params.append("n=True")
		if mOuter:
			params.append("N=True")
		params.append("i='%s'"%(self.iFile))
		params.append("o='%s'"%(self.oFile))

		header="""
#################################
# mjoin_w.pyの自動生成スクリプト
# version: %s
# 実行日時: %s
#################################
"""%(self.version,self.date)

		lib="""
import nysol.mcmd as nm
nm.setMsgFlg(True)
"""
		script="""
f=None
f<<=nm.mjoin(%s)
f.run(msg='on')
"""%(",".join(params))

		output="""
# ファイル出力された結果
oFile="%s"
"""%(self.oFile)

		# script tabにセット
		self.script_w.value = header+lib+script

		# outputscript tabにセット
		self.output_w.value = output

		# 出力path画面に移動
		self.tab.selected_index = 3

	def iFile_h(self,files):
		if len(files)==0:
			return
		# parameter設定tabに反映
		self.iFile=files[0] # ファイル名表示
		self.fName_w.value=self.iFile
		self.fText_w.value=self.iFile_w.propText() # ファイル内容

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.fName_w.value)
		self.iKey_w.addOptions(copy.copy(fldNames))

		# parameters画面に移動
		self.tab.selected_index = 1

	def mFile_h(self,files):
		if len(files)==0:
			return
		# parameter設定tabに反映
		self.mFile=files[0] # ファイル名表示
		self.mName_w.value=self.mFile
		self.mText_w.value=self.mFile_w.propText() # ファイル内容

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.mName_w.value)
		self.mKey_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

		# parameters画面に移動
		self.tab.selected_index = 2

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

		### mFileBox
		mf_config={
			"multiSelect":False,
			"property":True,
			"propertyRows":20,
			"actionHandler":self.mFile_h,
			"actionTitle":"選択"
	  }
		self.mFile_w=fileBrowser_w(self.mPath,mf_config)

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
		self.fName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='100%'),disabled=True)
		self.fText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.fName_w)
		pbox.append(self.fText_w)
		self.mName_w =widgets.Text(description="参照ファイル",value="",layout=Layout(width='100%'),disabled=True)
		self.mText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.mName_w)
		pbox.append(self.mText_w)

		# key 項目(入力)
		config_k={
			"options":[],
			"title":"入力key項目",
			"rows":5,
			"width":300,
			"blank":False,
			"multiSelect":False,
			"message":None
		}
		self.iKey_w=selfield_w(config_k)

		# key 項目(参照)
		config_K={
			"options":[],
			"title":"参照key項目(無選択=入力keyに同じ)",
			"rows":5,
			"width":300,
			"blank":True,
			"multiSelect":False,
			"message":None
		}
		self.mKey_w=selfield_w(config_K)


		# field 項目
		config_f={
			"options":[],
			"title":"結合する項目",
			"rows":5,
			"width":300,
			"multiSelect":True,
			"message":None
		}
		self.field_w=selfield_w(config_f)
		pbox.append(widgets.HBox([self.iKey_w.widget(),self.mKey_w.widget(),self.field_w.widget()]))

		# その他parameters
		self.iOuter_w=widgets.Checkbox(value=False, description='入力outer join', disabled=False)
		self.mOuter_w=widgets.Checkbox(value=False, description='参照outer join', disabled=False)
		subbox2=widgets.HBox([self.iOuter_w,self.mOuter_w])
		pbox.append(subbox2)

		paramBox=widgets.VBox(pbox)

		# スクリプト出力
		self.script_w =widgets.Textarea(value="",rows=15,layout=Layout(width='100%'),disabled=False)

		# 出力系スクリプト出力
		self.output_w =widgets.Textarea(value="",rows=15,layout=Layout(width='100%'),disabled=False)

		### tabコンテナ
		children=[]
		children.append(self.iFile_w.widget())
		children.append(self.mFile_w.widget())
		children.append(paramBox)
		children.append(self.script_w)
		children.append(self.output_w)
		children.append(self.oPath_w.widget())
		self.tab = widgets.Tab()
		self.tab.children = children
		self.tab.set_title(0, "入力ファイル選択")
		self.tab.set_title(1, "参照ファイル選択")
		self.tab.set_title(2, "結合")
		self.tab.set_title(3, "基本スクリプト")
		self.tab.set_title(4, "出力系スクリプト")
		self.tab.set_title(5, "出力パスブラウザ")

		# メッセージ窓
		self.msg_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		box=widgets.VBox([buttons_w,self.msg_w,self.tab])
		return box


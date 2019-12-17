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
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

		self.iFile=None
		self.oPath=None
		self.oFile=None

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		iKey=self.iKey_w.getValue()
		mKey=self.mKey_w.getValue()
		field=self.field_w.getValue()
		iOuter=self.iOuter_w.value
		mOuter=self.mOuter_w.value
		oFile=self.oFile_w.value
		if oFile=="":
			self.parent.msg_w.value="##ERROR: 出力ファイルが入力されていません"
			return False
		oFile=self.oPath+"/"+oFile
	
		if field=="":
			self.parent.msg_w.value = "##ERROR: 「結合する項目」が選ばれていません。"
			return False

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
		params.append("o='%s'"%(oFile))

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
print("#### START")
"""
		script="""
f=None
f<<=nm.mjoin(%s)
f.run(msg='on')
print("#### END")
"""%(",".join(params))

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
		self.iKey_w.addOptions(copy.copy(fldNames))

	def setmFile(self,iFiles,propText):
		self.mFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText

		# parameter設定tabに反映
		self.mName_w.value=self.mFile
		self.mText_w.value=self.propText # ファイル内容
		if self.mFile is None or not os.path.isfile(self.mFile):
			self.parent.msg_w.value = "##ERROR: 参照ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.mFile)
		self.mKey_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

	def widget(self):
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
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=True)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

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

		box=widgets.VBox(pbox)
		return box


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

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w):
		params={}
		params["iFile"]= self.iName_w.value
		params["mFile"]= self.mName_w.value
		params["oPath"]= self.oPath_w.value
		params["oFile"]= self.oFile_w.value

		if not wlib.iFileCheck(params["iFile"],self.parent.msg_w):
			return False
		if not wlib.iFileCheck(params["mFile"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oFile"],"出力ファイル名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		iKey=self.iKey_w.getValue()
		mKey=self.mKey_w.getValue()
		field=self.field_w.getValue()
		iOuter=self.iOuter_w.value
		mOuter=self.mOuter_w.value
	
		if not wlib.blankCheck(field,"結合する項目",self.parent.msg_w):
			return False

		par=[]
		par.append("k='%s'"%(iKey))
		if mKey!="":
			par.append("K='%s'"%(mKey))
		par.append("m='%s'"%(params["mFile"]))
		par.append("f='%s'"%(field))
		if iOuter:
			par.append("n=True")
		if mOuter:
			par.append("N=True")
		par.append("i='%s'"%(params["iFile"]))
		par.append("o='%s/%s'"%(params["oPath"],params["oFile"]))

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
"""%(",".join(par))

		script_w.value = header+lib+script
		return True

	def setiFile(self,iFiles,propText):
		# parameter設定tabに反映
		iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.iName_w.value=iFile
		self.iText_w.value=propText # ファイル内容
		if iFile is None or not os.path.isfile(iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(iFile)
		self.iKey_w.addOptions(copy.copy(fldNames))

	def setmFile(self,iFiles,propText):
		# parameter設定tabに反映
		mFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.mName_w.value=mFile
		self.mText_w.value=propText # ファイル内容
		if mFile is None or not os.path.isfile(mFile):
			self.parent.msg_w.value = "##ERROR: 参照ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(mFile)
		self.mKey_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

	def widget(self):
		pbox=[]

		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='100%'),disabled=True)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.mName_w =widgets.Text(description="参照ファイル",value="",layout=Layout(width='100%'),disabled=True)
		self.mText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.mName_w)
		pbox.append(self.mText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
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


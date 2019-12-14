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
class mselnum_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

		self.iFile=None
		self.oPath=None
		self.oFile=None

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		key=self.key_w.getValue()
		field=self.field_w.getValue()
		vFr=self.vFr_w.value
		vFrEq=self.vFrEq_w.value
		vTo=self.vTo_w.value
		vToEq=self.vToEq_w.value
		reverse=self.reverse_w.value
		oFile=self.oFile_w.value
		if oFile=="":
			self.parent.msg_w.value="##ERROR: 出力ファイルが入力されていません"
			return False
		oFile=self.oPath+"/"+oFile

		rFr="("
		rTo=")"
		if vFrEq:
			rFr="["
		if vToEq:
			rTo="]"
		range_="%s%s,%s%s"%(rFr,vFr,vTo,rTo)

		params=[]
		if key!="":
			params.append("k=\""+key+"\"")
		params.append("f=\""+field+"\"")
		params.append("c=\""+range_+"\"")
		if reverse:
			params.append("r=True")
		params.append("i=\""+self.iFile+"\"")
		params.append("o=\""+oFile+"\"")

		header="""
#################################
# mselnum_w.pyの自動生成スクリプト
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
f<<=nm.mselnum(%s)
f.run(msg='on')
"""%(",".join(params))

		output="""
# ファイル出力された結果
oFile="%s"
"""%(oFile)

		# script tabにセット
		script_w.value = header+lib+script

		# outputscript tabにセット
		output_w.value = output

		return True

	def setiFile(self,iFiles,propText):
		self.iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText
		if self.iFile is None or not os.path.isfile(self.iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# parameter設定tabに反映
		self.iName_w.value=self.iFile
		self.iText_w.value=self.propText # ファイル内容

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.iFile)
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

	def stats_h(self,b):
		field=self.field_w.getValue()
		self.parent.msg_w.value="\"%s\" 項目の統計量を計算中..."%(field)
		f=None
		f<<=nm.mcut(f=field,i=self.iFile)
		f<<=nm.msummary(f=field,c="min,median,mean,max")
		f<<=nm.writelist(header=True)
		rsl=f.run()
		#print(rsl)
		self.result_w.value=str(rsl)
		self.parent.msg_w.value="\"%s\" 項目の統計量を計算中...完了"%(field)

	def widget(self):

		# ボタン系
		#exeButton_w=widgets.Button(description="スクリプト生成")
		#exeButton_w.style.button_color = 'lightgreen'
		#exeButton_w.on_click(self.exe_h)
		#buttons_w=widgets.HBox([exeButton_w])

		pbox=[]
		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='100%'),disabled=False)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

		# key 項目
		config_k={
			"options":[],
			"title":"key単位選択の項目",
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
			"title":"item",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.field_w=selfield_w(config_f)
		pbox.append(widgets.HBox([self.field_w.widget(),self.key_w.widget()]))

		# 範囲
		self.vFr_w=widgets.Text(description="from:",value="",layout=Layout(width='300px'))
		self.vFrEq_w=widgets.Checkbox(value=True, description='以上', disabled=False)
		frBox=widgets.HBox([self.vFr_w,self.vFrEq_w])
		self.vTo_w=widgets.Text(description="to:",value="",layout=Layout(width='300px'))
		self.vToEq_w=widgets.Checkbox(value=True, description='以下', disabled=False)
		toBox=widgets.HBox([self.vTo_w,self.vToEq_w])
		pbox.append(frBox)
		pbox.append(toBox)

		# その他parameters
		self.reverse_w=widgets.Checkbox(value=False, description='条件反転', disabled=False)
		pbox.append(self.reverse_w)

		search_w=widgets.Button(description="項目統計")
		search_w.on_click(self.stats_h)
		self.result_w=widgets.Textarea(rows=4,disabled=True,layout=widgets.Layout(width='99%'))
		subbox1=widgets.VBox([search_w,self.result_w])
		pbox.append(subbox1)

		box=widgets.VBox(pbox)
		return box


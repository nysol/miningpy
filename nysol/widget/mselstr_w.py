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
class mselstr_w(object):
	def __init__(self,iPath,oFile):
		self.version="0.10"
		self.date=datetime.now()

		clear_output() # jupyter上の出力領域のクリア
		self.iPath=os.path.abspath(os.path.expanduser(iPath))
		self.oFile=os.path.abspath(os.path.expanduser(oFile))
		self.oPath=os.path.dirname(self.oFile)
		os.makedirs(self.oPath, exist_ok=True)

	def exe_h(self,b):
		_head=self.head_w.value
		_tail=self.tail_w.value
		reverse=self.reverse_w.value
		key=self.key_w.getValue()
		field=self.field_w.getValue()
		value=self.value_w.value
		
		if value=="":
			self.msg_w.value = "##ERROR: 「値」が入力されていません。"
			return

		if _head and _tail:
			sub=False
			head=False
			tail=False
		elif _head:
			sub=False
			head=True
			tail=False
		elif _tail:
			sub=False
			head=False
			tail=True
		else:
			sub=True
			head=False
			tail=False

		params=[]
		if key!="":
			params.append("k=\""+key+"\"")
		params.append("f=\""+field+"\"")
		params.append("v=\""+value+"\"")
		if reverse:
			params.append("r=True")
		if head:
			params.append("head=True")
		if tail:
			params.append("tail=True")
		if sub:
			params.append("sub=True")
		params.append("i=\""+self.iFile+"\"")
		params.append("o=\""+self.oFile+"\"")

		header="""
#################################
# mselstr_w.pyの自動生成スクリプト
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
f<<=nm.mselstr(%s)
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
		self.tab.selected_index = 2

	def iFile_h(self,files):
		if len(files)==0:
			return
		# parameter設定tabに反映
		self.iFile=files[0] # ファイル名表示
		self.fName_w.value=self.iFile
		self.fText_w.value=self.iFile_w.propText() # ファイル内容

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.fName_w.value)
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

		# parameters画面に移動
		self.tab.selected_index = 1

	def search_h(self,b):
		field=self.field_w.getValue()
		value=self.value_w.value
		_head=self.head_w.value
		_tail=self.tail_w.value
		reverse=self.reverse_w.value

		self.msg_w.value="\"%s\" 項目の値 \"%s\" を検索中..."%(field,value)

		if _head and _tail:
			sub=False
			head=False
			tail=False
		elif _head:
			sub=False
			head=True
			tail=False
		elif _tail:
			sub=False
			head=False
			tail=True
		else:
			sub=True
			head=False
			tail=False

		#print(field,sub,head,tail,value)
		f=None
		f<<=nm.mcut(f=field,i=self.iFile)
		if value!="":
			f<<=nm.mselstr(f=field,sub=sub,head=head,tail=tail,r=reverse,v=value)
		f<<=nm.muniq(k=field)
		rsl=f.run()
		self.result_w.options=[v[0] for v in rsl]
		self.msg_w.value="\"%s\" 項目の値 \"%s\" を検索中...完了"%(field,value)

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
		self.fName_w =widgets.Text(description="file name",value="",layout=Layout(width='100%'),disabled=True)
		self.fText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.fName_w)
		pbox.append(self.fText_w)

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

		# 値
		self.value_w=widgets.Text(description="値",value="",layout=Layout(width='300px'))
		search_w=widgets.Button(description="値のみで検索")
		search_w.on_click(self.search_h)
		self.result_w=widgets.Select(options=[],rows=14)
		subbox1=widgets.VBox([self.value_w,search_w,self.result_w])

		# その他parameters
		self.head_w=widgets.Checkbox(value=False, description='先頭一致', disabled=False)
		self.tail_w=widgets.Checkbox(value=False, description='末尾一致', disabled=False)
		self.reverse_w=widgets.Checkbox(value=False, description='条件反転', disabled=False)
		subbox2=widgets.VBox([self.head_w,self.tail_w,self.reverse_w])
		pbox.append(widgets.HBox([subbox1,subbox2]))

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
		self.tab.set_title(0, "入力ファイル選択")
		self.tab.set_title(1, "行選択")
		self.tab.set_title(2, "基本スクリプト")
		self.tab.set_title(3, "出力系スクリプト")
		self.tab.set_title(4, "出力パスブラウザ")

		# メッセージ窓
		self.msg_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		box=widgets.VBox([buttons_w,self.msg_w,self.tab])
		return box


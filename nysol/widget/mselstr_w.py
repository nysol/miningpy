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
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w):
		params={}
		params["iFile"]= self.iName_w.value
		params["oPath"]= self.oPath_w.value
		params["oFile"]= self.oFile_w.value

		if not wlib.iFileCheck(params["iFile"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oFile"],"出力ファイル名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		_head=self.head_w.value
		_tail=self.tail_w.value
		reverse=self.reverse_w.value
		key=self.key_w.getValue()
		field=self.field_w.getValue()
		value=self.value_w.value
		
		if value=="":
			self.parent.msg_w.value="##ERROR: 「値」が入力されていません。"
			return False

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

		par=[]
		if key!="":
			par.append("k=\""+key+"\"")
		par.append("f=\""+field+"\"")
		par.append("v=\""+value+"\"")
		if reverse:
			par.append("r=True")
		if head:
			par.append("head=True")
		if tail:
			par.append("tail=True")
		if sub:
			par.append("sub=True")
		par.append("i=\""+params["iFile"]+"\"")
		par.append("o=\""+params["oPath"]+"/"+params["oFile"]+"\"")

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
print("#### START")
"""
		script="""
f=None
f<<=nm.mselstr(%s)
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
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	def search_h(self,b):
		field=self.field_w.getValue()
		value=self.value_w.value
		_head=self.head_w.value
		_tail=self.tail_w.value
		reverse=self.reverse_w.value

		self.parent.msg_w.value="\"%s\" 項目の値 \"%s\" を検索中..."%(field,value)

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
		f<<=nm.mcut(f=field,i=self.iName_w.value)
		if value!="":
			f<<=nm.mselstr(f=field,sub=sub,head=head,tail=tail,r=reverse,v=value)
		f<<=nm.muniq(k=field)
		rsl=f.run()
		self.result_w.options=[v[0] for v in rsl]
		self.parent.msg_w.value="\"%s\" 項目の値 \"%s\" を検索中...完了"%(field,value)

	def widget(self):
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
			"title":"アイテム項目",
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

		box=widgets.VBox(pbox)
		return box


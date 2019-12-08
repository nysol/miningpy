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
class traclass_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

		self.iFile=None
		self.oPath=None
		self.oFile=None

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		params={}
		params["key"]=self.key_w.getValue()
		params["fld"]=self.field_w.getValue()
		params["val"]=self.value_w.value
		params["newName"]=self.newfld_w.value

		params["reverse"]=self.reverse_w.value
		params["reverse_r"]=not params["reverse"]
		oFile=self.oFile_w.value
		if oFile=="":
			self.parent.msg_w.value="##ERROR: 出力ファイルが入力されていません"
			return False
		params["oFile"]=self.oPath+"/"+oFile
		params["iFile"]=self.iFile
		
		if params["val"]=="":
			self.parent.msg_w.value="##ERROR: 「値」が入力されていません。"
			return False

		if params["newName"]=="":
			self.parent.msg_w.value="##ERROR: 「クラス名」が入力されていません。"
			return False

		_head=self.head_w.value
		_tail=self.tail_w.value
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
		params["sub"]=sub
		params["head"]=head
		params["tail"]=tail

		script="""
klass=None
klass<<=nm.mselstr(k='{key}',f='{fld}',v='{val}',r={reverse},head={head},tail={tail},sub={sub},i='{iFile}')
klass<<=nm.msetstr(v='1',a='{newName}')
klass<<=nm.mcut(f='{key},{newName}')
klass<<=nm.muniq(k='{key},{newName}')

f=None
f<<=nm.mjoin(k='{key}',m=klass,f='{newName}',n=True,i='{iFile}')
f<<=nm.mselstr(f='{fld}',v='{val}',r={reverse_r},head={head},tail={tail},sub={sub})
f<<=nm.mnullto(f='{newName}',v='0',o='{oFile}')
f.run()
""".format(**params)

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

		# parameter設定tabに反映
		self.iName_w.value=self.iFile
		self.iText_w.value=self.propText # ファイル内容
		if self.iFile is None or not os.path.isfile(self.iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.iFile)
		self.key_w.addOptions(copy.copy(fldNames))
		self.field_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

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
		f<<=nm.mcut(f=field,i=self.iFile)
		if value!="":
			f<<=nm.mselstr(f=field,sub=sub,head=head,tail=tail,r=reverse,v=value)
		f<<=nm.muniq(k=field)
		rsl=f.run()
		self.result_w.options=[v[0] for v in rsl]
		self.parent.msg_w.value="\"%s\" 項目の値 \"%s\" を検索中...完了"%(field,value)

	def widget(self):
		pbox=[]
		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="入力ファイル",value="",layout=Layout(width='100%'),disabled=True)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='100%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=True)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

		# key 項目
		config_k={
			"options":[],
			"title":"key単位選択の項目",
			"rows":5,
			"width":300,
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

		# 新項目名
		self.newfld_w=widgets.Text(description="出力項目名",value="",layout=Layout(width='300px'))
		newfldL_w=widgets.Label(value="指定しなければ集計対象項目名と同じ名前になる",disabled=True)
		pbox.append(widgets.HBox([self.newfld_w,newfldL_w]))

		# その他parameters
		self.head_w=widgets.Checkbox(value=False, description='先頭一致', disabled=False)
		self.tail_w=widgets.Checkbox(value=False, description='末尾一致', disabled=False)
		self.reverse_w=widgets.Checkbox(value=False, description='条件反転', disabled=False)
		subbox2=widgets.VBox([self.head_w,self.tail_w,self.reverse_w])
		pbox.append(widgets.HBox([subbox1,subbox2]))

		box=widgets.VBox(pbox)
		return box


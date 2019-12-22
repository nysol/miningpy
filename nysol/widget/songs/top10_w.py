#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from ipywidgets import Button, Layout, Label
import os
import json
import csv
import copy
from datetime import datetime
from IPython.display import clear_output

from nysol.widget.fileBrowser_w import fileBrowser_w
from nysol.widget.selfield_w import selfield_w
import nysol.widget.lib as wlib

####################################################################
class top10_w(object):
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
		params["title"]=self.titles_w.value

		script1=wlib.readSource("nysol.widget.songs.lib.top10")
		script2="""
import os
print("#### START")

oFile="{oPath}/{oFile}"
os.makedirs(oPath,exist_ok=True)
top10("{title}","{iFile}",oFile,10)

print("#### END")
""".format(**params)

		# script tabにセット
		script_w.value = script1+script2
		return True

	def setiFile(self,iFiles,propText):
		# parameter設定tabに反映
		iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.iName_w.value=iFile
		self.iText_w.value=propText # ファイル内容
		if iFile is None or not os.path.isfile(iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		titles=[]
		with open(iFile) as f:
			reader = csv.reader(f)
			for i,row in enumerate(reader):
				if i>0:
					titles.append(row[0])
		self.titles_w.options=titles

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

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

		self.titles_w=widgets.Select(options=[],description="歌詞の選択",rows=10,layout=Layout(width='100%'))
		pbox.append(self.titles_w)

		box=widgets.VBox(pbox)
		return box


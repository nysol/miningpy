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
class conv_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w):
		params={}
		params["iPaths"]=self.iNames_w.options
		params["oPath"]  = self.oPath_w.value
		params["oFile"]  = self.oFile_w.value

		if not wlib.iPathCheck(params["iPaths"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oFile"],"出力ファイル名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		script1=wlib.readSource("nysol.widget.songs.lib.conv","conv")
		script2="""
import os
print("#### START")

oPath="{oPath}"
os.makedirs(oPath,exist_ok=True)
conv({iPaths},"%s/{oFile}"%(oPath)) 

print("#### END")
""".format(**params)

		# script tabにセット
		script_w.value = script1+script2
		return True

	def setiFile(self,iFiles,propText):
		# parameter設定tabに反映
		fList=[]
		for iFile in iFiles:
			iFile=os.path.abspath(iFile)
			if iFile is None or not os.path.isdir(iFile):
				self.parent.msg_w.value = "##ERROR: 入力dirsの一つがディレクトリでないです: %s"%(iFile)
				return
			fList.append(os.path.abspath(iFile))
		self.iNames_w.options=fList

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	def widget(self):
		pbox=[]

		# ファイル名とファイル内容
		self.iNames_w=widgets.Select( options=[], rows=5, description='入力dirs:',layout=Layout(width='100%'), disabled=False)
		pbox.append(self.iNames_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oFile_w =widgets.Text(description="ファイル名",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oFile_w)

		box=widgets.VBox(pbox)
		return box


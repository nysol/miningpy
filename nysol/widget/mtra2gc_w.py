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
class mtra2gc_w(object):
	def __init__(self):
		self.version="0.10"
		self.date=datetime.now()

	def setParent(self,parent):
		self.parent=parent

	def exe(self,script_w,output_w):
		params={}
		params["traFile"]  = self.traFile
		params["tid"]      = self.traID_w.getValue()
		params["item"]     = self.item_w.getValue()
		params["oPath"]    = self.oPath
		params["oDir"]     = self.oDir_w.value
		params["minSup"]   = self.minSup_w.value
		params["sim"]      = self.edgeType_w.value
		params["nodeSup"]  = self.nodeSup_w.value
		if params["sim"]=="minConf":
			params["th"]  = self.minConf_w.value
			params["simName"]  = "C"
			params["simFld"]  = "confidence"
			params["undirect"]  = False
		else:
			params["th"]  = self.minPMI_w.value
			params["simName"]  = "P"
			params["simFld"]  = "PMI"
			params["undirect"]  = True

		if params["oDir"]=="":
			self.parent.msg_w.value="##ERROR: 出力dirが入力されていません"
			return False

		if params["tid"]==params["item"]:
			self.parent.msg_w.value="##ERROR: トランザクションIDとアイテム項目が同じ項目になってます"
			return False

		script="""
import os
import nysol.take as nt
import nysol.mcmd as nm
import nysol.view.mnetpie as nnpie
nm.setMsgFlg(True)

# 出力ディレクトリを作成する
op="{oPath}"+"/"+"{oDir}"
os.makedirs(op,exist_ok=True)

nt.mtra2gc(i="{traFile}",
				tid="{tid}",
				item="{item}",
				no=op+"/node.csv",
				eo=op+"/edge.csv",
				s={minSup},
				sim="{simName}",
				th={th},
				node_support={nodeSup}
				).run()

nnpie.mnetpie(ei=op+"/edge.csv",
				ni=op+"/node.csv",
				ef="node1,node2",
				nf="node",
				o=op+"/graph.html",
				nodeSizeFld="support",
				edgeWidthFld="{simFld}",
				undirect={undirect}
				)

""".format(**params)

		script_w.value = script
		return True

	def setiFile(self,iFiles,propText):
		self.traFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.propText=propText
		if self.traFile is None or not os.path.isfile(self.traFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# parameter設定tabに反映
		self.traFile_w.value=self.traFile
		self.traFileTxt_w.value=self.propText

		# フィールドリスト
		fldNames=wlib.getCSVheader(self.traFile)
		self.traID_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath=os.path.abspath(os.path.expanduser(oPath))
		self.oPath_w.value=self.oPath

	def widget(self):
		pbox=[]

		# ファイル名とファイル内容
		self.traFile_w =widgets.Text(description="トランザクション",value="",layout=Layout(width='99%'),disabled=True)
		self.traFileTxt_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.traFile_w)
		pbox.append(self.traFileTxt_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=True)
		pbox.append(self.oPath_w)
		self.oDir_w =widgets.Text(description="出力dir名",value="",layout=widgets.Layout(width='100%'),disabled=False)
		pbox.append(self.oDir_w)

		# traID 項目
		config_t={
			"options":[],
			"title":"トランザクションID",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.traID_w=selfield_w(config_t)

		# item 項目
		config_i={
			"options":[],
			"title":"アイテム項目",
			"rows":5,
			"width":300,
			"multiSelect":False,
			"message":None
		}
		self.item_w=selfield_w(config_i)

		pbox.append(widgets.HBox([self.traID_w.widget(),self.item_w.widget()]))

		# 各種しきい値
		self.minSup_w=widgets.FloatSlider(description='minSup', value=0.01, min=0.0, max=1.0, step=0.01)
		pbox.append(self.minSup_w)

		self.edgeType_w=widgets.RadioButtons(description='edge条件',options=['minConf', 'minPMI'])
		self.minConf_w=widgets.FloatSlider(description='minConf', value=0.01, min=0.0, max=1.0, step=0.01)
		self.minPMI_w=widgets.FloatSlider(description='minPMI', value=0.0, min=-1.0, max=1.0, step=0.01)
		pbox.append(widgets.HBox([self.edgeType_w,self.minConf_w,self.minPMI_w]))

		self.nodeSup_w=widgets.Checkbox( value=False, description='nodeにもminSupを適用する', disabled=False)
		pbox.append(self.nodeSup_w)

		box=widgets.VBox(pbox)
		return box


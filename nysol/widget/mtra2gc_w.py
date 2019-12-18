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

	def exe(self,script_w):
		params={}
		params["version"]  = self.version
		params["date"]     = self.date
		params["iFile"]    = self.iName_w.value
		params["oPath"]    = self.oPath_w.value
		params["oDir"]     = self.oDir_w.value

		if not wlib.iFileCheck(params["iFile"],self.parent.msg_w):
			return False
		if not wlib.blankCheck(params["oDir"],"出力dir名",self.parent.msg_w):
			return False
		if not wlib.oPathCheck(params["oPath"],self.parent.msg_w):
			return False

		params["tid"]      = self.traID_w.getValue()
		params["item"]     = self.item_w.getValue()
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

		if params["tid"]==params["item"]:
			self.parent.msg_w.value="##ERROR: トランザクションIDとアイテム項目が同じ項目になってます"
			return False

		script="""
import os
import nysol.take as nt
import nysol.mcmd as nm
import nysol.view.mnetpie as nnpie
nm.setMsgFlg(True)
print("#### START")

# 出力ディレクトリを作成する
op="{oPath}"+"/"+"{oDir}"
os.makedirs(op,exist_ok=True)

nt.mtra2gc(i="{iFile}",
				tid="{tid}",
				item="{item}",
				no=op+"/node.csv",
				eo=op+"/edge.csv",
				s={minSup},
				sim="{simName}",
				th={th},
				node_support={nodeSup}
				).run()

nm.mnormalize(f="support:_nv",c="range",i=op+"/node.csv").mcal(c="${{_nv}}*200",a="_nodeSize",o=op+"/node2.csv").run()

nnpie.mnetpie(ei=op+"/edge.csv",
				ni=op+"/node2.csv",
				ef="node1,node2",
				nf="node",
				o=op+"/graph.html",
				nodeSizeFld="_nodeSize",
				undirect={undirect}
				)
print("#### END")
""".format(**params)

		#os.system("fdp)
		"""
mgv(ei=op+"/edge.csv",ef="e1,e2",o=op+"/graph.dot")
"""

		#edgeWidthFld="{simFld}",

		script_w.value = script
		return True

	def setiFile(self,iFiles,propText):
		# parameter設定tabに反映
		iFile=os.path.abspath(os.path.expanduser(iFiles[0]))
		self.iName_w.value=iFile
		self.iText_w.value=propText
		if iFile is None or not os.path.isfile(iFile):
			self.parent.msg_w.value = "##ERROR: 入力ファイルが選ばれていません。"
			return

		# フィールドリスト
		fldNames=wlib.getCSVheader(iFile)
		self.traID_w.addOptions(copy.copy(fldNames))
		self.item_w.addOptions(copy.copy(fldNames))

	def setoPath(self,oPath):
		self.oPath_w.value=os.path.abspath(os.path.expanduser(oPath))

	def widget(self):
		pbox=[]

		# ファイル名とファイル内容
		self.iName_w =widgets.Text(description="トランザクション",value="",layout=Layout(width='99%'),disabled=False)
		self.iText_w =widgets.Textarea(value="",rows=5,layout=Layout(width='99%'),disabled=True)
		pbox.append(self.iName_w)
		pbox.append(self.iText_w)
		self.oPath_w =widgets.Text(description="出力パス",value="",layout=Layout(width='100%'),disabled=False)
		pbox.append(self.oPath_w)
		self.oDir_w =widgets.Text(description="出力dir名",value="",layout=widgets.Layout(width='100%'),disabled=False)
		pbox.append(self.oDir_w)

		# traID 項目
		config_t={
			"options":[],
			"title":"トランザクションID項目",
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

		self.nodeSup_w=widgets.Checkbox( value=True, description='nodeにもminSupを適用する', disabled=False)
		pbox.append(self.nodeSup_w)

		box=widgets.VBox(pbox)
		return box


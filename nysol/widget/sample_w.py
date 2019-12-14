#!/usr/bin/env python
# coding: utf-8

# ## インターラクティブクラスタリング

from __future__ import print_function
import os
import sys
import json
from datetime import datetime
import random
import numpy as np

import ipywidgets as widgets

####################################################################
class SampleList_w(object):
	def __init__(self,config={}):
		self.sampleList=[] # このwidgetに表示されるサンプル
		self.config = config
		# config default設定
		if "db" not in self.config:
			self.config["db"]=None
		if "message" not in self.config:
			self.config["message"]=None

		self.db=self.config["db"]
		self.message=self.config["message"]

	def refresh(self):
		options=[]
		for smp in self.sampleList:
			options.append(smp.title(24))
		self.sampleSel_w.options=options
		if not self.message is None:
			self.message("refresh",self)

	def summary_h(self,event):
		text=""
		if len(self.sampleSel_w.index)==1: # 表示するのは、ひとつのコメントを選んだ時のみ
			i=self.sampleSel_w.index[-1]
			text=self.sampleList[i].text()
		self.summary_w.value=text
		if not self.message is None:
			self.message("summary_h",self)

	def randomSelect_h(self,event):
		k=int(self.sizek_w.value)
		self.out_w.value="ランダムに %d 件抽出しています"%k
		self.sampleList=self.db.randomSelect(k)
		self.refresh()
		if not self.message is None:
			self.message("randomSelect_h",self)

	def rangeSelect_h(self,event):
		k=15
		k=int(self.sizek_w.value)
		fr=int(self.from_w.value)
		self.out_w.value="%d番目から%d件のサンプルを抽出しています"%(fr,k)
		self.sampleList=self.db.rangeSelect(fr,k)
		self.refresh()
		if not self.message is None:
			self.message("rangeSelect_h",self)

	def widget(self):
		# ボタン系
		self.sizek_w=widgets.Text(value="15",layout=widgets.Layout(width='40px'))
		shuffle_w=widgets.Button(description='シャッフル', disabled=False)
		shuffle_w.on_click(self.randomSelect_h)

		self.from_w=widgets.Text(value="0",layout=widgets.Layout(width='40px'))
		range_w=widgets.Button(description='範囲選択', disabled=False)
		range_w.on_click(self.rangeSelect_h)
		buttons = widgets.HBox([self.sizek_w,shuffle_w,self.from_w,range_w])

		# メッセージ窓
		self.out_w = widgets.Text(value="",layout=widgets.Layout(width='100%'),disabled=True)

		# サンプル一覧と内容
		self.sampleSel_w=widgets.SelectMultiple(options=[],rows=14, disabled=False, layout=widgets.Layout(width='70%'))
		self.sampleSel_w.observe(self.summary_h, names='value') # HANDLER
		self.summary_w=widgets.Textarea(value="",rows=10, disabled=True, layout=widgets.Layout(width='100%'))
		sampleBox = widgets.HBox([self.sampleSel_w, self.summary_w])

		box = widgets.VBox([self.out_w,buttons, sampleBox])
		return box


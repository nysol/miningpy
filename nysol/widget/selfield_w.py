#!/usr/bin/env python
# coding: utf-8

# ## インターラクティブクラスタリング

from __future__ import print_function
import os
import sys

import ipywidgets as widgets

####################################################################
class selfield_w(object):
	def __init__(self,config={}):
		self.config = config
		# config default設定
		if "options" not in self.config:
			self.config["options"]=["choose"]
		if "title" not in self.config:
			self.config["title"]="fields"
		if "rows" not in self.config:
			self.config["rows"]=5
		if "width" not in self.config:
			self.config["width"]=200
		if "blank" not in self.config:
			self.config["blank"]=False
		if "multiSelect" not in self.config:
			self.config["multiSelect"]=False
		if "message" not in self.config:
			self.config["message"]=None

		self.message=self.config["message"]

	def addOptions(self,options):
		if self.config["blank"]:
			options=[""]+options
		self.fList_w.options=options

	def getValue(self):
		return self.fList_w.value

	def change_h(self,event):
		if not self.message is None:
			self.message("change_h",self)

	def widget(self):
		rows=self.config["rows"]
		width=self.config["width"]
		title=self.config["title"]
		options=self.config["options"]

		title_w=widgets.Text(value=title,disabled=True, layout=widgets.Layout(width="%dpx"%width))
		if self.config["multiSelect"]:
			self.fList_w=widgets.SelectMultiple(options=options,rows=rows, layout=widgets.Layout(width="%dpx"%width))
		else:
			self.fList_w=widgets.Select(options=options,rows=rows, layout=widgets.Layout(width="%dpx"%width))
		self.fList_w.observe(self.change_h, names='value') # HANDLER

		box = widgets.VBox([title_w,self.fList_w], layout=widgets.Layout(width="%dpx"%(width+10)))
		return box


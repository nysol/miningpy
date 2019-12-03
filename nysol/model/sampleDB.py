#!/usr/bin/env python
# coding: utf-8

# ## インターラクティブクラスタリング

from __future__ import print_function
import os
import sys
import json
from datetime import datetime
import random

####################################################################
class SampleDB(object):
	def __init__(self):
		self.sampleList=[]
		self._i=0

	def __iter__(self):
		return self

	def __next__(self):
		if self._i==len(self.sampleList)-1:
			raise StopIteration()
		self._i += 1
		return self.sampleList[self._i]

	def __len__(self):
		return len(self.sampleList)

	def add(self,sample):
		self.sampleList.append(sample)

	def randomSelect(self,k=15):
		sel=[]
		if len(self.sampleList)>0:
			sel=random.sample(self.sampleList, k)
		return sel

	def rangeSelect(self,fr=0,k=15):
		sel=[]
		size=len(self.sampleList)
		if size>0 and fr<size:
			sel=self.sampleList[fr:fr+k]
		return sel


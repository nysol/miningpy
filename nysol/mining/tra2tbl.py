#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
warnings.simplefilter('ignore')

import os
import sys
import numpy as np
import pickle
import json
import csv
import re
import pandas as pd
import nysol.mcmd as nm

def tra2tbl(iFile,oFile,tidFld,itemFld,null=0,dummy=True,aggFld=None,aggStat=None,klassFld=None):
	klass=None
	if klassFld is not None:
		klass<<=nm.mcut(f=tidFld+","+klassFld,i=iFile)
		klass<<=nm.muniq(k=tidFld)

	f=None
	# aggFldが指定されていればセル項目を集計
	if aggFld is not None:
		f<<=nm.mcut(f=tidFld+","+itemFld+","+aggFld, i=iFile)
		f<<=nm.mstats(k=tidFld,f="%s:_cell"%(aggFld), c=aggStat)

	# aggFldが指定されていなければカウント
	else:
		f<<=nm.mcut(f=tidFld+","+itemFld, i=iFile)

		# アイテムが出現したかどうか
		if dummy:
			f<<=nm.muniq(k=tidFld+","+itemFld)
			f<<=nm.msetstr(v=1, a="_cell")

		# アイテムが何件出現したかどうか
		else:
			f<<=nm.mcount(k=tidFld+","+itemFld, a="_cell")

	# 横展開
	f<<=nm.m2cross(k=tidFld,s=itemFld,f="_cell")

	# クラス項目が指定されていれば結合する
	if klassFld is not None:
		f<<=nm.mjoin(k=tidFld,m=klass,f=klassFld)

	# null値を一斉に置換する
	f<<=nm.mnullto(f="*",v=null,o=oFile)
	f.run(msg="on")

if __name__ == '__main__':
	iFile="/Users/hamuro/dm/DATA/yakiniku/yakiniku_new.csv"
	oFile="./xxtbl1"
	tra2tbl(iFile,oFile,"traID","商品名",klassFld="支払方法")
	oFile="./xxtbl2"
	tra2tbl(iFile,oFile,"traID","商品名",dummy=False,klassFld="支払方法")

	oFile="./xxtbl3"
	tra2tbl(iFile,oFile,"traID","商品名",aggFld="金額",aggStat="sum")

	oFile="./xxtbl4"
	tra2tbl(iFile,oFile,"traID","分類",aggFld="金額",aggStat="sum")


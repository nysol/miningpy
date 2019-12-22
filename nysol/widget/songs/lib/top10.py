#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys 
from datetime import datetime

from glob import glob
import re
import numpy as np
import json
import csv
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer

def top10(title,iCSV,oFile,k=10):
	dforg=pd.read_csv(iCSV)
	df=dforg.set_index('id')
	# 対象歌詞の選択
	target=df.loc["%s"%(title)]
	# 距離計算
	dist=np.sum((df.values-target.values)**2,axis=1)

	# 距離最小の上位10のindexを取得
	top=[]
	for i in range(10):
		am=np.argmin(dist)
		top.append(int(am))
		dist[am]=100.0

	sel=dforg.iloc[top,:]
	sel.to_csv(oFile,index=False)

if __name__ == '__main__':
	iCSV="xxc/table_tfidf.csv"
	oFile="xxe"
	top=5
	top10("やさしい気持ちで_Superfly",iCSV,oFile,top)


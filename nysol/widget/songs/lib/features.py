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
from sklearn.feature_extraction.text import TfidfTransformer

def features(iJson,oPath,minFreq):
	oTotalFreq="%s/toatlFreq.csv"%oPath
	oFreq="%s/table_freq.csv"%oPath
	oTFIDF="%s/table_tfidf.csv"%oPath

	with open(iJson) as f:
		songs=json.load(f)
	print(songs[0].keys())
	# dict_keys(['title', 'singer', 'writer', 'composer', 'phrases', 'wordFreq'])

	wordTotal={}
	for song in songs:
		for key,val in song["wordFreq"].items():
			if key not in wordTotal:
				wordTotal[key]=0
			wordTotal[key]+=1

	# minFreq以上のwordを選択し、件数逆順に並べ替え
	wordTotal={key:val for key,val in wordTotal.items() if val>=minFreq}
	wordSorted = sorted(wordTotal.items(), key=lambda x:x[1],reverse=True)

	# wordと列番号の相互変換表
	word2num={wf[0]:i for i,wf in enumerate(wordSorted)} # {'*': 0, 'する': 1, 'いる': 2, '涙': 3, ...
	num2word={i:wf[0] for i,wf in enumerate(wordSorted)} # {0: '*', 1: 'する', 2: 'いる', 3: '涙', ...

	# word-frequency表の出力
	with open(oTotalFreq, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["word","frequency"])
		for line in wordSorted:
			writer.writerow(line)

	# 歌詞別にword頻度表を作成する
	tbl=[]
	id_=[]
	for song in songs:
		id_.append("%s_%s"%(song["title"],song["singer"]))
		row=[0]*len(word2num) # 表の一行(0初期化)
		for key,val in song["wordFreq"].items():
			if key in word2num:
				row[word2num[key]]=val
		tbl.append(row)

	# 参考: https://scikit-learn.org/stable/modules/feature_extraction.html#common-vectorizer-usage
	transformer = TfidfTransformer(smooth_idf=False)
	tfidf = transformer.fit_transform(tbl)
	tfidf = tfidf.toarray()
	#print(tbl[:1])
	#print(tfidf[:1])

	# 歌詞別頻度表出力
	with open(oFreq, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["id"]+list(word2num.keys()))
		for i,line in enumerate(tbl):
			writer.writerow([id_[i]]+line)

	# 歌詞別TFIDF表出力
	with open(oTFIDF, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["id"]+list(word2num.keys()))
		print("xxxxxx1")
		for i,line in enumerate(tfidf):
			line=[float(v) for v in line]
			writer.writerow([id_[i]]+line)

if __name__ == '__main__':
	iJson="xxb"
	oPath="xxc"
	minFreq=5

	os.makedirs(oPath,exist_ok=True)
	features(iJson,oPath,minFreq)


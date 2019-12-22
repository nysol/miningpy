#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime
from glob import glob

import numpy as np
import json
debug="on"

def conv(iPaths,oFile):
	# iFiles
	#覚醒
	#
	#歌手　Superfly
	#作詞　越智志帆
	#作曲　越智志帆
	#
	#現る黒い空
	#鼓動は雷鳴を繰り返す

	iFiles=[]
	for iPath in iPaths:
		iFiles+=glob("%s/*"%iPath)

	songs=[]
	total=len(iFiles)
	for i,iFile in enumerate(iFiles):
		if i % 10 == 0:
			print("%d/%d %s"%(i,total,iFile))
		with open(iFile) as f:
			doc=f.read()
			doc=doc.split("\n")
		title,kasyu,sakushi,sakkyoku=None,None,None,None
		title=doc[0]
		kashi=[]
		for j,line in enumerate(doc):
			if j<6 and re.search("^アーティスト　",line):
				kasyu=line.replace("アーティスト　","")
			if j<6 and re.search("^唄　",line):
				kasyu=line.replace("唄　","")
			if j<6 and re.search("^歌手　",line):
				kasyu=line.replace("歌手　","")
			if j<6 and re.search("^作詞　",line):
				sakushi=line.replace("作詞　","")
			if j<6 and re.search("^作曲　",line):
				sakkyoku=line.replace("作曲　","")
			if j>6 and line!="":
				line=re.sub("\(.+\)","",line)
				line = re.sub("\u3000","",line)
				kashi.append(line)

		#print("タイトル:",title,"歌手:",kasyu,"作詞:",sakushi,"作曲:",sakkyoku)
		songs.append({"title":title,"singer":kasyu,"writer":sakushi,"composer":sakkyoku,"phrases":kashi})

	# JSONに保存
	songs_dump=json.dumps(songs, ensure_ascii=False, indent=2)
	with open(oFile,"bw") as f:
		f.write(songs_dump.encode("utf-8"))

if __name__ == '__main__':
	sf=os.path.expanduser("~/songs/DATA/Superfly")
	sz=os.path.expanduser("~/songs/DATA/サザンオールスターズ")
	conv([sf,sz],"./xxa")


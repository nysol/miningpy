#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys 
from datetime import datetime

from glob import glob
import re
import numpy as np
import json
import MeCab

def parse_mecab(text):
	# 'この内容に気が付いた筆者さんは偉いと思う。多くの女性が自分でも理由が分からずイライラしてしまう原因をこうして気付い>て理解してくれるだけで、救われた気がするんじゃないかな。ただ男性が外で働いて大変な思いをしていることは事実。奥さんも「自分だけが家のことを押しつけられて大変」「家事育児は二人のことなんだから、休日や仕事から帰ってきた後は手伝ってくれるのが当たり前！」と思い込まず、お互いの大変さを思いやる気持ちといたわり合う姿勢をずっと持ち続けることが大事ですよね。'
	#jumanpp = Juman()
	text=text.replace("\u3000","")
	text=text.replace("　","")
	mt = MeCab.Tagger("mecabrc")
	res = mt.parseToNode(text)
	words=[]
	hinsi=[]
	i=0
	while res:
	#		print (res.surface)
		arr = res.feature.split(",")
		#i+=1
		#print(arr)
		#if i>60:
		# exit()
		# ['BOS/EOS', '*', '*', '*', '*', '*', '*', '*', '*']
		# ['名詞', '数', '*', '*', '*', '*', '３', 'サン', 'サン']
		# ['名詞', '数', '*', '*', '*', '*', '７', 'ナナ', 'ナナ']
		# ['名詞', '接尾', '助数詞', '*', '*', '*', '年', 'ネン', 'ネン']
		# ['動詞', '自立', '*', '*', '一段', '連用形', '生きる', 'イキ', 'イキ']
		# ['助詞', '接続助詞', '*', '*', '*', '*', 'て', 'テ', 'テ']
		# ['動詞', '非自立', '*', '*', 'カ変・クル', '連用形', 'くる', 'キ', 'キ']
		# ['助動詞', '*', '*', '*', '特殊・タ', '基本形', 'た', 'タ', 'タ']
		# ['名詞', '非自立', '副詞可能', '*', '*', '*', '中', 'ナカ', 'ナカ']
		# ['助詞', '格助詞', '一般', '*', '*', '*', 'で', 'デ', 'デ']
		# ['記号', '一般', '*', '*', '*', '*', '・', '・', '・']
		words.append(arr[6])
		hinsi.append(arr[0])
		res = res.next

	#words=[s for s in words if s != '*']
	return words,hinsi

def parsing_count(iJson,oJson,targetKlass=["名詞","形容詞","動詞"]):
	doc=None
	with open(iJson,"r") as f:
		doc=json.load(f)

	newSongs=[]
	total=len(doc)
	for i,song in enumerate(doc):
		if i % 10 == 0:
			print("%d/%d %s"%(i,total,song["title"]))
		wordFreq={}
		for text in song["phrases"]:
			wrd,cls=parse_mecab(text)
			for j in range(len(cls)):
				if not cls[j] in targetKlass:
					continue
				if not wrd[j] in wordFreq:
					wordFreq[wrd[j]]=0
				wordFreq[wrd[j]]+=1
		song["wordFreq"]=wordFreq
		newSongs.append(song)

	# JSONに保存
	songs_dump=json.dumps(newSongs, ensure_ascii=False, indent=2)
	with open(oJson,"bw") as f:
		f.write(songs_dump.encode("utf-8"))

if __name__ == '__main__':
	parsing_count("xxa","xxb")

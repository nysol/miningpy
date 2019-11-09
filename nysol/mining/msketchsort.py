#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

import nysol.mcmd as nm
import nysol.util as nu
import nysol.util.margs as margs
import nysol.util.mtemp as mtemp
from nysol.mining import extcore as extMining


class msketchsort(object):

	helpMSG="""
---------------------------------
msketchsort.py version #{$version}
---------------------------------
概要) スケッチソートを利用した全ベクトルペアの距離計算
特徴) データに含まれる全ベクトル間の距離を高速に計算できる。
      窓を指定することで比較するベクトルの範囲を限定することができる。

書式) #{$cmd} e= tid= [dist=] [th=] [mr=] [wf=] [ws=] [dist=C|H] i= [o=] [--help]

e=    : ベクトルの各要素となる項目名【必須】ex) e=val1,val2,val3,val4
tid=  : ベクトルを識別するための項目名(i=上の項目名)【必須】
dist= : ベクトル間の距離計算の方法。(省略時は C が指定される)
        C (cosine distance): コサイン距離 (th=0-2)
        H (Haming distance): ハミング距離 (th=1- )
th=   : dist=で指定された距離計算について、ここで指定された値以下のペアを出力する。省略時は0.01が設定される。
mr=   : ペアを逃す確率を指定 (missing ratio) False Negative。省略時は0.00001が設定される。
wf=   : ウィンドウ項目。ex) 日付
ws=   : ウィンドウサイズの上限(0以上の整数)【0で制限なし,default:0】
        wfで指定した窓に含まれる全ペアを窓をずらしながら計算する。
i=    : 入力ファイル
o=    : 出力ファイル
seed= : 乱数の種(1以上の整数,default:1)
-uc   : データ点を0を中心に移動させない


例1: input1.csv
tid,val1,val2,val3,val4,val5
0,4,9,1,8,7
1,2,6,3,4,10
2,3,10,1,7,4
3,2,8,1,3,10
4,4,7,2,3,10
5,8,4,3,1,9
6,6,7,5,1,9
7,5,4,2,6,7
8,3,10,1,5,9
9,9,1,8,7,3
10,5,2,3,10,9
11,4,9,1,8,7

$ msketchsort.py i=input1.csv tid=tid e=val1,val2,val3,val4,val5 o=out1.csv
SketchSort version 0.0.8
Written by Yasuo Tabei

deciding parameters such that the missing edge ratio is no more than 1e-05
decided parameters:
hamming distance threshold: 1
number of blocks: 4
number of chunks: 14
.
.
.

$ more out1.csv
distance,tid,tid2
5.96046e-08,0,11



例2: input2.csv
eCode,tgdate,term,val1,val2,val3,val4,val5
1990,20100120,0,4,9,1,8,7
2499,20100120,0,2,6,3,4,10
2784,20100120,0,3,10,1,7,4
3109,20100120,0,2,8,1,3,10
3114,20100120,0,4,7,2,3,10
6364,20100120,0,8,4,3,1,9
8154,20100120,0,6,7,5,1,9
8703,20100120,0,5,4,2,6,7
9959,20100120,0,3,10,1,5,9
1990,20100121,1,9,1,8,7,3
2499,20100121,1,5,2,3,10,9
2784,20100121,1,4,9,1,8,7
3594,20100122,2,4,9,1,8,7


$ msketchsort.py i=input2.csv tid=eCode,tgdate e=val1,val2,val3,val4,val5 th=0.05 wf=term ws=1 o=out2.csv
SketchSort version 0.0.8
Written by Yasuo Tabei

deciding parameters such that the missing edge ratio is no more than 1e-05
decided parameters:
hamming distance threshold: 1
number of blocks: 4
number of chunks: 14
.
.
.

$ more out2.csv
distance,eCode,tgdate,eCode2,tgdate2
0,1990,20100120,2784,20100121
0,2784,20100121,3594,20100122

"""

	verInfo="version=0.1"

	paramter = {	
		"e":"str",
		"tid":"fld", # "str"
		"dist":"str",
		"th":"float",
		"mr":"float",
		"wf":"fld",
		"ws":"int",
		"i":"file",
		"o":"file",
		"T":"str",
		"seed":"int",
		"uc":"bool"
	}


	paramcond = {	
		"hissu": ["tid","i","e"]
	}	


	def help():
		print(msketchsort.helpMSG) 

	def ver():
		print(msketchsort.verInfo)

	def __param_check_set(self , kwd):

		# 存在チェック
		for k,v in kwd.items():
			if not k in msketchsort.paramter	:
				raise( Exception("KeyError: {} in {} ".format(k,self.__class__.__name__) ) )

		self.msgoff = True
		self.oFile  = kwd["o"] if "o" in kwd else None
		self.iFile  = kwd["i"] if "i" in kwd else None
		self.elem   = kwd["e"] if "e" in kwd else None
		self.tidH   = kwd["tid"].split(",") if "tid"   in kwd else None
		self.tid    = kwd["tid"] if "tid" in kwd else None
		self.dist   = kwd["dist"] if "dist" in kwd else "C"
		self.th     = float(kwd["th"]) if "th" in kwd else 0.01
		self.mr     = float(kwd["mr"]) if "mr" in kwd else 0.00001
		self.wfH   = kwd["wf"].split(",") if "wf" in kwd else None
		self.wf    = kwd["wf"] if "wf" in kwd else None
		self.ws    = int(kwd["ws"]) if "ws" in kwd else 0
		self.seed  = int(kwd["seed"]) if "seed" in kwd else 1
		self.uc    = kwd["uc"] if "uc" in kwd else False

		import time
		self.pt = int(time.time())


		if self.dist=="H" and self.th <1.0:
			raise( Exception("The range of th= is different in {} ".format(k,self.__class__.__name__) ) )

		self.workf = nu.Mtemp()

	def __cmdline(self):
		cmdline = self.__class__.__name__
		for k,v in self.args.items():
			if type(v) is bool :
				if v == True :
					cmdline += " -" + str(k)
			else:
				cmdline += " " + str(k) + "=" + str(k)
		return cmdline 

	def __init__(self,**kwd):
		#パラメータチェック
		self.args = kwd
		self.__param_check_set(kwd)



	# ============
	# entry point
	def run(self,**kw_args):

		os.environ['KG_ScpVerboseLevel'] = "2"
		if "msg" in kw_args:
			if kw_args["msg"] == "on":
				os.environ['KG_ScpVerboseLevel'] = "4"

		ln="#{@pt}line"

		# make the line number
		ln = "{}line".format(self.pt)

		xxmap = self.workf.file()
		sdata = self.workf.file()

		# convert the data for sketchport
		# mkdata
		xx1 =  nm.mnumber(S=0,a=ln,q=True,i=self.iFile)
		if self.wfH :
			xx2  = nm.mcut(f=self.wfH+self.tidH+[self.elem],i=xx1)
		else:
			self.wfH = ["{}wf".format(self.pt)]
			xx2  =   nm.msetstr(v=0,a=self.wfH,i=xx1)
			xx2  <<= nm.mcut(f=self.wfH+self.tidH+[self.elem])

		fmap = nm.mcut(f=[ln]+self.tidH,i=xx1,o=xxmap)
		xx2  <<= nm.mcut(f=self.wfH+[self.elem],nfno=True) 
		xx2 <<= nm.cmd("tr ',' ' '")
		xx2 <<= nm.mwrite(o=sdata)
		nm.runs([fmap,xx2])

		# do sort
		outf  = self.workf.file()
		para = {}
		if self.dist=="C" :
			para["cosdist"] = self.th
		elif self.dist=="H" :
			para["hamdist"] = self.th

		if not self.uc :
			para["centering"] = True 
			
		para["auto"] = True 
		para["windowsize"] = self.ws
		para["seed"] = self.seed
		para["i"] = sdata
		para["o"] = outf
		status = extMining.sketchsort(para)		
		if status: 
			raise Exception("#ERROR# checking sketchsort messages")

		tmp=[]
		for val in self.tidH :
	 	  tmp.append("{}:{}2".format(val,val))
		tid2=",".join(tmp)

		f = nm.mread(i=outf) 
		f <<= nm.cmd("tr ' ' ',' ")
		f <<= nm.mcut(nfni=True,f="0:eline1,1:eline2,2:distance")
		f <<= nm.mfsort(f="eline*")
	  # 行番号に対応するtidを取得
		f <<= nm.mjoin(k="eline1",K="{}line".format(self.pt),f=self.tid,m=xxmap)
		f <<= nm.mjoin(k="eline2",K="{}line".format(self.pt),f=tid2,m=xxmap)
		f <<= nm.msortf(f="eline1%n,eline2%n")
		f <<= nm.mcut(r=True,f="eline1,eline2")
		f <<= nm.msortf(f=self.tid)
		f <<= nm.mfldname(q=True,o=self.oFile)
		f.run()
		nu.mmsg.endLog(self.__cmdline())

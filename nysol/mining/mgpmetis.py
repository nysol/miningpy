#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

import nysol.mcmd as nm
import nysol.util as nu
import nysol.util.margs as margs
from nysol.util.mtemp import Mtemp
from nysol.util.mrecount import mrecount

from nysol.mining import extcore as extMining


class mgpmetis(object):

	helpMSG="""
----------------------------
mgpmetis.rb version #{$version}
----------------------------
概要) METISを利用したグラフ分割(クラスタリング)
特徴) 1) 節点数をできるだけ同じようにして、枝のカット数を最小化するように分割する。
      2) 節点と枝に重みを与えることも可能。
      3) 一つの節点が複数のクラスタに属することはない(ハードクラスタリング)。
      4) 内部ではgpmetisコマンドをコールしている。
用法) mgpmetis.rb kway= [ptype=rb|kway] ei= [ef=] [ew=] [ni=] [nf=] [nw=] [o=]
                  [balance=] [ncuts=] [dat=] [map=] [-noexe] [--help]

  ファイル関連
  ei=      : 枝ファイル名(節点ペア)【必須】
  ef=      : 枝ファイル上の節点ペア項目名(2項目のみ)【デフォルト:"node1,node2"】
  ew=      : 枝ファイル上の重み項目名(1項目のみ)【オプション:省略時は全ての枝の重みを1と見なす】
           : 重みは整数で指定しなければならない。
  ni=      : 節点ファイル名【オプション*注1】
  nf=      : 節点ファイル上の節点項目名(1項目のみ)【デフォルト:"node"】
  nw=      : 節点ファイル上の重み項目名(複数項目指定可)【オプション:省略時は全ての重みを1と見なす】
           : 重みは整数で指定しなければならない。
  o=       : 出力ファイル名【オプション:defaultは標準出力】

  動作の制御関連
  kway=    : 分割数【必須】
  ptype=   : 分割アルゴリズム【デフォルト:kway】
  balance= : 分割アンバランスファクタ【デフォルト: ptype=rbの時は1.001、ptype=kwayの時は1.03】
  ncuts=   : 分割フェーズで、初期値を変えて試行する回数【オプション:default=1】
  seed=    : 乱数の種(0以上の整数)【オプション:default=-1(時間依存)】

  gpmetis用のデータ生成
  dat=     : 指定されたファイルにgpmetisコマンド用のデータを出力する。
  map=     : 指定されたファイルにgpmetisコマンド用の節点番号とi=上の節点名のマッピングデータを出力する。
  -noexe   : 内部でgpmetisを実行しない。dat=,map=の出力だけが必要な場合に指定する。

  その他
	--help   : ヘルプの表示

  注1：節点ファイルは、孤立節点(一つの節点からのみ構成される部分グラフ)がある場合、
       もしくは節点の重みを与えたいときのみ指定すればよい。
  注2：節点もしくは枝の重みを与えない時は、内部的に全ての重みを1として計算する。

必要なソフトウェア)
  gpmetis(metis-5.1.0)
  インストールは以下のURLより行う。
  http://glaros.dtc.umn.edu/gkhome/metis/metis/download

入力データ)
  節点ペアのCSVファイル(ファイル名はei=にて指定)
	例:
    node1,node2,weight
    a,b,1
    a,c,2
    a,e,1
    b,c,2
    b,d,1
    c,d,2
    c,e,3
    d,f,2
    d,g,5
    e,f,2
    f,g,6


出力データ)
  節点とクラスタ番号のCSVデータ(ファイル名はo=にて指定)
    node,cluster
    a,2
    b,1
    c,2
    d,0
    e,0
    f,0
    g,1

# Copyright(c) NYSOL 2012- All Rights Reserved.

"""

	verInfo="version=0.1"

	paramter = {	
		"ei":"str",
		"ef":"fld", # "str"
		"ew":"str",
		"ni":"str",
		"nf":"fld",
		"nw":"str",
		"o":"file",
		"kway":"int",
		"ptype":"str",
		"balance":"float",
		"ncuts":"int",
		"dat":"file",
		"map":"str",
		"seed":"int",
		"verbose":"bool",
		"noexe":"bool"
	}
	paramcond = {	
		"hissu": ["kway","ei"]
	}	

	def help():
		print(mgpmetis.helpMSG) 

	def ver():
		print(mgpmetis.verInfo)

	def __param_check_set(self , kwd):

		# 存在チェック
		for k,v in kwd.items():
			if not k in mgpmetis.paramter	:
				raise( Exception("KeyError: {} in {} ".format(k,self.__class__.__name__) ) )

		self.msgoff = True


		self.kway   = int(kwd["kway"])
		self.oFile  = kwd["o"] if "o" in kwd else None
		self.eFile  = kwd["ei"]
		self.nFile  = kwd["ni"] if "ni" in kwd else None
		self.dFile  = kwd["dat"] if "dat" in kwd else None
		self.mFile  = kwd["map"] if "map" in kwd else None

		if "ef" in kwd :
			ef0 = kwd["ef"].split(",")
			self.ef1 = ef0[0]
			self.ef2 = ef0[1] 
		else:
			self.ef1 = "node1"
			self.ef2 = "node2" 
			
		self.ew  = kwd["ew"] if "ew" in kwd else None
		self.nf  = kwd["nf"] if "nf" in kwd else None
		self.nw  = kwd["nw"] if "nw" in kwd else None
		self.ncon=0
		if self.nw :
			self.ncon = len(self.nw.split(","))


		# ---- other paramters
		self.ptype = kwd["ptype"] if "ptype" in kwd else "kway" 
		self.ncuts = int(kwd["ncuts"]) if "ncuts" in kwd else 1 
		self.balance = float(kwd["balance"]) if "balance" in kwd else None
		self.ufactor = None
		if self.balance :
			if self.balance < 1.0 :
				raise( Exception("balance expect range (> 1.0)" ) )
			self.ufactor = int((self.balance-1.0)*1000)
		else:
			if self.ptype=="kway":
				self.ufactor=30
			else:
				self.ufactor=1

		self.seed  = int(kwd["seed"]) if "seed" in kwd else -1
		self.noexe = kwd["noexe"] if "noexe" in kwd else False
		self.verbose = kwd["verbose"] if "verbose" in kwd else False
			
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

		os.environ["KG_VerboseLevel"] = "2"
		if "msg" in kw_args:
			if kw_args["msg"] == "on":
				os.environ['KG_ScpVerboseLevel'] = "3"


		temp=Mtemp()
		xxedge = temp.file()
		xxnode = temp.file()
		xxnam2num = temp.file()
		xxnum2nam = temp.file()
		xxebase   = temp.file()
		xxbody    = temp.file()

		e1=None
		if self.ew :
			e1 <<= nm.mcut(f="%s:__node1,%s:__node2,%s:__weight"%(self.ef1,self.ef2,self.ew),i=self.eFile)
		else:
			e1 <<= nm.mcut(f="%s:__node1,%s:__node2"%(self.ef1,self.ef2),i=self.eFile)

		e1 <<= nm.muniq(k="__node1,__node2")


		e2 = nm.mfldname(i=e1,f="__node2:__node1,__node1:__node2")

		fe =None
		fe <<= nm.muniq(k="__node1,__node2",i=[e1,e2],o=xxedge)
		fe.run()
		
		# cleaning the node data (remove duplicate nodes)
		fn=None
		if self.nFile :
			if self.nw :
				fn <<= nm.mcut(f="%s:__node,%s"%(self.nf,self.nw),i=self.nFile)
			else:
				fn <<= nm.mcut(f="%s:__node"%(self.nf),i=self.nFile)

			fn <<= nm.muniq(k="__node",o=xxnode)

		else:
			xxen1 = nm.mcut(f="__node1:__node",i=xxedge)
			xxen2 = nm.mcut(f="__node2:__node",i=xxedge)
			fn <<= nm.muniq(k="__node",o=xxnode,i=[xxen1,xxen2])

		fn.run()


		# 節点名<=>節点番号変換表の作成
		fmap = None
		fmap <<= nm.mcut(f="__node" , i=xxnode)
		fmap <<= nm.mnumber(a="__num",S=1,q=True,o=xxnam2num)
		fmap <<= nm.msortf(f="__num",o=xxnum2nam)
		fmap.run()

		# 節点ファイルが指定された場合は枝ファイルとの整合性チェック
		if self.nFile :
			ncheck =   nm.mcut(f="__node1:__node" , i=xxedge)
			ncheck <<= nm.mcommon(k="__node" , m=xxnam2num,r=True)
			nmatch = ncheck.run()
			if len(nmatch) > 0 :
				raise Exception("#ERROR# the node named '%s' in the edge file doesn't exist in the node file."%(nmatch[0][0]))


		# metisのグラフファイルフォーマット
		# 先頭行n m [fmt] [ncon]
		# n: 節点数、m:枝数、ncon: 節点weightの数
		# 1xx: 節点サイズ有り (not used, meaning always "0")
		# x1x: 節点weight有り
		# xx1: 枝がweightを有り
		# s w_1 w_2 ... w_ncon v_1 e_1 v_2 e_2 ... v_k e_k
		# s: 節点サイズ  (節点サイズは利用不可)
		# w_x: 節点weight
		# v_x: 接続のある節点番号(行番号)
		# e_x: 枝weight

		# --------------------
		# generate edge data using the integer numbered nodes
		#fnnum = None
		fnnum = nm.mcut(f="__num:__node_n1",i=xxnam2num) # {xxnnum}

		fenum = None
		fenum <<= nm.mjoin(k="__node1", K="__node", f="__num:__node_n1", m=xxnam2num , i=xxedge)
		fenum <<= nm.mjoin(k="__node2", K="__node", f="__num:__node_n2", m=xxnam2num)
		fenum <<= nm.msortf(f="__node_n1") #{xxenum}



		febase = None
		febase <<= nm.mnjoin(k="__node_n1",m=fenum,i=fnnum,n=True)
		febase <<= nm.msortf(f="__node_n1%n,__node_n2%n",o=xxebase) #{xxebase}"
		febase.run()
		
		fbody = None
		if not self.ew :
			fbody <<= nm.mcut(f="__node_n1,__node_n2", i=xxebase)
			fbody <<= nm.mtra(k="__node_n1",f="__node_n2" ,q=True )
			fbody <<= nm.mcut(f="__node_n2", nfno=True, o=xxbody)

		# if ew= is specified, merge the weight data into the edge data.
		else:
			febody = None
			febody <<= nm.mcut(f="__node_n1,__node_n2:__v", i=xxebase)
			febody <<= nm.mnumber(S=0,I=2,a="__seq" ,q=True)
		
			fwbody = None
			fwbody <<= nm.mcut(f="__node_n1,__weight:__v",i=xxebase)
			fwbody <<= nm.mnumber(S=1,I=2,a="__seq" ,q=True)

			fbody <<= nm.msortf(f="__seq%n",i=[febody,fwbody])
			fbody <<= nm.mtra(k="__node_n1" ,f="__v" ,q=True )
			fbody <<= nm.mcut(f="__v" ,nfno=True,o=xxbody)

		fbody.run()
		# xxbody
		# 2 7 3 8 5 9
		# 1 7 3 10 5 11 7 12
		# 1 8 2 10 4 13 7 14

		# --------------------
		# generate node data using integer number
		if self.nFile and self.nw :
			# xxnode
			# __node,v1,v2
			# a,1,1
			# b,1,1
			# c,1,1
			xxnbody = temp.file()
			xxnbody1 = temp.file()
			fnbody = None
			fnbody <<= nm.mjoin(k="__node", f="__num", i=xxnode ,m=xxnam2num)
			fnbody <<= nm.msortf(f="__num%n")
			fnbody <<= nm.mcut(f=self.nw,nfno=True)
			fnbody <<= nm.cmd("tr ',' ' ' ") # tricky!!
			fnbody <<= nm.mwrite(o=xxnbody)
			fnbody.run()
			# xxnbody
			# 1 1
			# 1 1
			# 1 1
			# paste the node weight with edge body
			fnbody1 = None
			fnbody1 <<= nm.mpaste(nfn=True,m=xxbody , i=xxnbody)
			fnbody1 <<= nm.cmd("tr ',' ' ' ") 
			fnbody1 <<= nm.mwrite(o=xxnbody1)
			fnbody1.run()
			os.system("mv %s %s"%(xxnbody1,xxbody))

		# xxbody
		# 1 1 2 7 3 8 5 9
		# 1 1 1 7 3 10 5 11 7 12
		# 1 1 1 8 2 10 4 13 7 14


		eSize=mrecount(i=xxedge)
		eSize/=2
		nSize=mrecount(i=xxnode)
		nwFlag = 1 if self.nw else 0
		ewFlag = 1 if self.ew else 0
		
		fmt="0%d%d"%(nwFlag,ewFlag)

		xxhead = temp.file()
		xxgraph= temp.file()
				
		os.system("echo '%d %d %s %d' > %s"%(nSize,eSize,fmt,self.ncon,xxhead))
		os.system("cat  %s %s > %s"%(xxhead,xxbody,xxgraph))

		if self.mFile :
			nm.mfldname(f="__num:num,__node:node",i=xxnum2nam,o=self.mFile).run()
			
		if self.dFile :
			os.system("cp %s %s"%(xxgraph,self.dFile))
			
		if not self.noexe:
			if self.verbose :
				os.system("gpmetis -seed=%d -ptype=%s -ncuts=%d -ufactor=%d %s %d"%(self.seed,self.ptype,self.ncuts,self.ufactor,xxgraph,self.kway))
			else:
				os.system("gpmetis -seed=%d -ptype=%s -ncuts=%d -ufactor=%d %s %d  > /dev/null"%(self.seed,self.ptype,self.ncuts,self.ufactor,xxgraph,self.kway))
			import glob
			if len(glob.glob(xxgraph+".part.*")) == 0:
				raise Exception("#ERROR# command `gpmetis' didn't output any results")

			# 節点名を数字から元に戻す
			# #{xxgraph}.part.#{kway}
			# 1
			# 0
			# 1
			fo = None	
			fo <<= nm.mcut(f="0:cluster", nfni=True,i=xxgraph+".part."+str(self.kway))
			fo <<= nm.mnumber(S=1,a="__num",q=True)
			fo <<= nm.mjoin(k="__num",f="__node",m= xxnum2nam)
			fo <<= nm.msortf(f="__node,cluster")
			if self.nf :
				fo <<= nm.mcut(f="__node:%s,cluster"%(self.nf),o=self.oFile)
			else:
				fo <<= nm.mcut(f="__node:node,cluster",o=self.oFile)
			fo.run()

		nu.mmsg.endLog(self.__cmdline())

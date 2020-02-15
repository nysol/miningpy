#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

import nysol.mcmd as nm
import nysol.util as nu
import nysol.util.margs as margs
from nysol.util.mtemp import Mtemp

from nysol.util.mmkdir import mkDir
from nysol.util.mparallel import meach as meach

from nysol.util.mrecount import mrecount


class mgnfeatures(object):

	helpMSG="""
----------------------------
#{CMD} version #{$version}
----------------------------
概要) ノードの特徴量を計算
特徴) 以下のノードの特徴量を出力
  degree      : 各ノードの次数
	cc          : クラスタ係数
  components  : 連結成分 (連結成分をクラスタとする)
  betweenness : 媒介中心性 (ある点が他の点間の最短経路に位置する程度)
  closeness   : 近接中心性 (他の点への最短経路の合計の逆数)
  page_rank   : 各ノードの重要度をpage_rankで計算

書式) #{CMD} I=|(ei= [ni=]) ef= [nf=] [ew=] [mode=] O= [-directed] [-normalize] [T=] [-verbose] [--help]
  I=     : 入力パス
         : パス中の枝ファイルは.edge拡張子が前提
         : パス中の点ファイルは.node拡張子が前提
  ei=    : 枝データファイル(I=とは一緒に指定できない)
  ef=    : 枝データ上の2つの節点項目名
  ni=    : 節点データファイル(I=とは一緒に指定できない)
  nf=    : 節点データ上の節点項目名(省略時は"node")
  ew=    : 枝ファイル上の重み項目名【省略時は全ての枝の重みを1と見なす】
  mode=  : in|out|all (-directedを指定した場合のみ有向。省略時は"all"。詳しくは詳細)を参照)
  O=     : 出力パス
  -directed  : 有向グラフ
  -normalize : 基準化

  その他
  T= : ワークディレクトリ(default:/tmp)
  -verbose : show the END messages of MCMD and R used in this command
  --help : ヘルプの表示

必要なソフトウェア)
  1) R
  2) igraph package for R

詳細)
1.オプション一覧
             | mode        | 重み |    基準化
---------------------------------------------------------------------
 degree      |in,out,all   | 無し | n-1で割る
 cc          | 無し        | 有り | 無し
 components  | 無し        | 無し | 無し
 betweenness | 無し        | 有り | 2B/(n^2-3n+2) [B:raw betweenness]
 closeness   |in,out,all   | 有り | n-1で割る
 page_rank   | 無し        | 有り | 無し
-------------------------------------------------------------------- 
modeは-directedを指定された場合に有効になる。
in:入枝が対象, out:出枝が対象, all: 両方対象を意味する

2. ccは-directedが指定されていても無視される。
3. componentsは-directedが指定された場合には強連結を求める。
4. pageRankは"prpack"を利用。

入力データ)
２つの節点からなる枝データ

入力データ)
節点ペアのCSVファイル(ファイル名はei=にて指定)
例)
$ cat data/dat1.edge
n1,n2
a,b
a,c
a,d
a,e
a,f
a,g
b,c
b,d
b,e
b,f
c,h
d,g
e,f

$ mgnfeatures.rb ei=data/dat1.edge ef=n1,n2 O=rsl01
$ cat rsl01/dat1.csv
node,degree,components,betweenness,closeness,page_rank
a,6,1,8.5,0.125,0.216364844231035
b,5,1,4,0.111111111111111,0.181335882714211
c,3,1,6,0.0909090909090909,0.126673483636635
d,3,1,0.5,0.0833333333333333,0.11508233404895
e,3,1,0,0.0833333333333333,0.111947143712761
f,3,1,0,0.0833333333333333,0.111947143712761
g,2,1,0,0.0769230769230769,0.0820083475799325
h,1,1,0,0.0588235294117647,0.0546408203637134

# Copyright(c) NYSOL 2014- All Rights Reserved.

"""

	verInfo="version=0.1"

	paramter = {	
		"I":"str",
		"ei":"str", # "str"
		"ef":"fld",
		"ni":"str",
		"nf":"fld",
		"ew":"fld",
		"mode":"str",
		"O":"str",
		"T":"str",
		"directed":"bool",
		"normalize":"bool",
		"verbose":"bool"
	}


	paramcond = {	
		"hissu": ["ef"]
	}	


	def help():
		print(mgnfeatures.helpMSG) 

	def ver():
		print(mgnfeatures.verInfo)

	def __param_check_set(self , kwd):

		# 存在チェック
		for k,v in kwd.items():
			if not k in mgnfeatures.paramter	:
				raise( Exception("KeyError: {} in {} ".format(k,self.__class__.__name__) ) )

		self.msgoff = True
		self.iPath  = kwd["I"] if "I" in kwd else None
		self.oPath  = kwd["O"] if "O" in kwd else None

		if not "ef" in kwd:
			raise Exception("ef= is necessary")

		ef0 = kwd["ef"].split(",")
		self.ef1 = ef0[0]
		self.ef2 = ef0[1] 


		if self.iPath :
			import glob
			self.edgeFiles = glob.glob(self.iPath+"/*.edge")
			
		else:

			self.edgeFiles = kwd["ei"].split() if "ei" in kwd else None

			if self.edgeFiles == None or len(self.edgeFiles)==0 :
				raise Exception("#ERROR# ei= or I= is mandatory")


		self.ew = kwd["ew"] if "ew" in kwd else None
		self.ni = kwd["ni"] if "ni" in kwd else None
		self.nf = kwd["nf"] if "nf" in kwd else None
			
		self.mode = kwd["mode"] if "mode" in kwd else "all"
			
		if self.mode!="all" and self.mode!="in" and self.mode!="out" : 
			raise Exception("#ERROR# mode= can specify all|in|out")


		self.directed = kwd["directed"] if "directed" in kwd else False
		self.norm = kwd["normalize"]    if "normalize" in kwd else False
		self.verbose = kwd["verbose"]  if "verbose" in kwd else False

		self.MP  = int(kwd["mp"]) if "mp" in kwd else 4

		mkDir(self.oPath) 


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


	def genRscript(self,directed,norm,mode,eFile,wFile,ew,nodeSize,oFile,scpFile):
		dir = "TRUE" if directed else "FALSE"
		normalize = "TRUE" if norm else "FALSE"

		r_proc = '''
library(igraph)
#### reading edge file
g=read.graph("{eFile}",format="edgelist",directed="{dir}",n="{nodeSize}")
# reading weight file
w=read.csv("{wFile}")
E(g)$weight=as.list(w$"{ew}")

####
deg=degree(g,mode="{mode}",normalized="{normalize}")
### ew=がnullの場合はweight=1として扱っているので以下で問題ない
cc=transitivity(g,type="weight")
cls=components(g,mode="strong")

# -normalizeと-directedは一緒に指定できないため以下の処理を行う
if ("{dir}"=="TRUE") {{
	norm2 = "FALSE"
	betweenness=betweenness(g,directed="{dir}",weight=E(g)$weight,normalized=norm2)
}} else {{
	norm2 = "{normalize}"
	betweenness=betweenness(g,directed="{dir}",weight=E(g)$weight,normalized=norm2)
}}

closeness=closeness(g,weight=E(g)$weight,mode="{mode}",normalized="{normalize}")
pgrank=page.rank(g,weight=E(g)$weight,directed="{dir}")$vector

dat=data.frame(
  degree=deg,
	cc=cc,
  components=cls$membership,
	betweenness=betweenness,
	closeness=closeness,
	page_rank=pgrank
)
write.csv(dat,file="{oFile}",quote=FALSE,row.names=FALSE)

		'''.format(
			eFile = eFile,dir = dir,nodeSize = nodeSize ,wFile=wFile,
			ew=ew,mode=mode,normalize = normalize,oFile = oFile
		)

		with open(scpFile,"w") as fpw:
			fpw.write(r_proc)




	####
	# converting original graph file with text to one with integer
	# output #{numFile} and #{mapFile}, then return the number of nodes of the graph
	#
	# ei    ni   xxnum   xxmap
	# v1,v2 v            node%1,flag%0,num
	# E,J   A     0 3    A,0,0	
	# E,A   B     0 4    B,0,1
	# J,D   C     0 6    D,0,2
	# J,A   D =>  1 5    E,0,3
	# J,H   E     2 4    F,0,4
	# D,H   F     2 5    H,0,5
	# D,F   G     2 6    J,0,6
	# H,F   H     3 6    C,1,7
	# A,F   I     4 5    G,1,8
	# B,H   J     5 6    I,1,9	
	#
	# return value is 10 (nodes)
	# "flag" on xxmap: 0:nodes in "ei", 1:nodes only in "ni".
	def g2pair(self,ni,nf,ei,ef1,ef2,ew,numFile,mapFile,weightFile):

		inobj = []
		inobj.append(nm.mcut(f="%s:node"%(ef1),i=ei ).msetstr(a="flag",v=0))
		inobj.append(nm.mcut(f="%s:node"%(ef2),i=ei ).msetstr(a="flag",v=0))
		if nf :
			inobj.append(nm.mcut(f="%s:node"%(nf),i=ni ).msetstr(a="flag",v=1))

		f   = nm.mbest(i=inobj,k="node",s="flag",fr=0,size=1 )
		# isolated nodes are set to the end of position in mapping file.
		# S= must start from 0 (but inside R vertex number will be added one)
		f <<= nm.mnumber(s="flag,node",a="num",S=0,o=mapFile)
		f.run()

		f = None 
		f <<= nm.mcut(f=[ef1,ef2] , i=ei)
		f <<= nm.mjoin( k=ef1 , K="node" , m=mapFile ,f="num:num1")
		f <<= nm.mjoin( k=ef2 , K="node" , m=mapFile ,f="num:num2")
		f <<= nm.mcut(f="num1,num2")
		f <<= nm.mfsort(f="num1,num2")
		f <<= nm.msortf(f="num1%n,num2%n",nfno=True)
		f <<= nm.cmd("tr ',' ' ' " )
		f <<= nm.mwrite(o=numFile)
		f.run()

		nodeSize=mrecount(i=mapFile)

		if ew:
			nm.mcut(f=ew,i=ei,o=weightFile).run()
		else:
			ew="weight"
			nm.msetstr(v=1,a=ew,i=ei).mcut(f=ew,o=weightFile).run()

		return nodeSize

	def runmain(self,edgeFile):

		import re

		baseName = re.sub('\.edge$',"",edgeFile)
		name = re.sub('^.*\/',"",baseName)

		if self.ni :
			nodeFile=self.ni
		else :
			nodeFile=re.sub('\.edge$',".node",edgeFile)

		# convert the original graph to one igraph can handle
		temp=Mtemp()
		xxnum = temp.file()
		xxmap = temp.file()
		xxout = temp.file()
		xxscp = temp.file()
		xxweight=temp.file()


		nodeSize=self.g2pair(
			nodeFile,self.nf,edgeFile,self.ef1,self.ef2,self.ew,xxnum,xxmap,xxweight
		)

		# generate R script, and run
		self.genRscript(
			self.directed,self.norm,self.mode,
			xxnum, xxweight, self.ew,nodeSize, xxout, xxscp
		)
		
		if self.verbose :
			os.system("R --vanilla -q < %s"%(xxscp))
		else:
			os.system("R --vanilla -q --slave < %s 2>/dev/null "%(xxscp))

		f = None
		f <<= nm.mnumber(q=True,S=0,a="num",i=xxout)
		f <<= nm.mjoin(k="num",f="node",m=xxmap )
		outf = self.oPath + "/" +name + ".csv"
		if self.nf :
			f <<= nm.mcut(f="node:%s,degree,cc,components,betweenness,closeness,page_rank"%(self.nf),o=outf) 
		else:
			f <<= nm.mcut(f="node,degree,cc,components,betweenness,closeness,page_rank",o=outf) 

		f.run()

	# ============
	# entry point
	def run(self,**kw_args):

		os.environ['KG_ScpVerboseLevel'] = "2"
		if "msg" in kw_args:
			if kw_args["msg"] == "on":
				os.environ['KG_ScpVerboseLevel'] = "4"

		meach(self.runmain,self.edgeFiles,mpCount=self.MP)


		nu.mmsg.endLog(self.__cmdline())

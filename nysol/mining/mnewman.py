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


class mnewman(object):

	helpMSG="""
----------------------------
#{CMD} version #{$version}
----------------------------
概要) newman クラスタリング
特徴) 1) modularityの最適化を用いたクラスタリングが実施できる。
      2) 辺の媒介中心性を利用したグラフ分割によるクラスタリングが実施できる。
書式) #{CMD} ei= ef= ni= [nf=] [ew=] [al=]  o= [-directed]

  ei=   : 枝データファイル
  ef=   : 枝データ上の2つの節点項目名
  ni=   : 節点データファイル
  nf=   : 節点データ上の節点項目名
  ew=   : 枝ファイル上の重み項目名【省略時は全ての枝の重みを1と見なす】
  al=   : クラスタリングアルゴリズム。省略時はmoが選択される。
          mo:(modularity optimization) modularityを最適化するための貪欲法によるクラスタリング
              無向グラフでのみ指定可能。igraphのcluster_fast_greedyを利用
          eb:(edge betweenness) 辺の媒介中心性を計算し最もそれが高い辺を取り除くことでグラフを分割する。
              分割数はmodurarityが最大となるように決定される。igraphのcluster_edge_betweennessを利用
  -directed : 有向グラフ
  o=     : クラスタ

  その他
  T= : ワークディレクトリ(default:/tmp)
  -verbose : show the END messages of MCMD and R used in this command
  --help : ヘルプの表示

必要なソフトウェア)
	1) R
	2) igraph package for R

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

$ cat data/dat.node
node
a
b
c
d
e
f
g

${CMD} ei=data/dat1.edge ef=n1,n2 al=mo o=rsl01
#END# mnewman.rb ei=./data/dat1.edge ef=n1,n2 al=mo o=rsl01; 2016/01/24 01:54:25

$ cat rsl01
node,cls
a,2
b,1
c,3
d,2
e,1
f,1
g,2
h,3

# Copyright(c) NYSOL 2012- All Rights Reserved.
"""

	verInfo="version=0.1"


	paramter = {	
		"ei":"str",
		"ef":"str",
		"ni":"str",
		"nf":"str",
		"o":"str",
		"ew":"str",
		"al":"str",
		"T":"str",
		"directed":"bool",
		"verbose":"bool"
	}

	paramcond = {	
		"hissu": ["ei","ef"]
	}	

	def help():
		print(mnewman.helpMSG) 

	def ver():
		print(mnewman.verInfo)

	def __param_check_set(self , kwd):

		# 存在チェック
		for k,v in kwd.items():
			if not k in mnewman.paramter	:
				raise( Exception("KeyError: {} in {} ".format(k,self.__class__.__name__) ) )

		self.msgoff = True

		self.oFile  = kwd["o"] if "o" in kwd else None

		self.ei  = kwd["ei"] 
		ef0 = kwd["ef"].split(",")
		self.ef1 = ef0[0]
		self.ef2 = ef0[1] 

		self.ni = kwd["ni"] if "ni" in kwd else None
		self.nf = kwd["nf"] if "nf" in kwd else None

		self.ew = kwd["ew"] if "ew" in kwd else None
		self.al = kwd["al"] if "al" in kwd else "mo"
		self.verbose  = kwd["verbose"]  if "verbose" in kwd else False
		self.directed = kwd["directed"]  if "directed" in kwd else False

		if not (self.al == "mo" or self.al == "eb") :
			raise( Exception("#ERROR# al= can specify mo|eb" ) )


	def __cmdline(self):
		cmdline = self.__class__.__name__
		for k,v in self.args.items():
			if type(v) is bool :
				if v == True :
					cmdline += " -" + str(k)
			else:
				cmdline += " " + str(k) + "=" + str(v)
		return cmdline 

	def __init__(self,**kwd):
		#パラメータチェック
		self.args = kwd
		self.__param_check_set(kwd)



	####
	# generating the R script for graph features
	# pars: parameters for each graph feature
	def genRscript(self,directed,eFile,wFile,ew,nodeSize,al,oFile,oInfo,scpFile):

		dir = "TRUE" if directed else "FALSE"

		if al=="mo":
			if directed:
				raise(Exception("#ERROR# can't use -directed option with al=\"mo\" " ))

			r_proc_mo = '''
library(igraph)
# reading edge file
g=read.graph("{eFile}",format="edgelist",directed={dir},n={nodeSize})
# reading weight file
w=read.csv("{wFile}")
E(g)$weight=as.list(w$"{ew}")
# do clustering
nc=cluster_fast_greedy(g,weight=E(g)$weight,merges=T,modularity=T,membership=T)

# 置換
ms=cbind(membership(nc))
# Community sizes:
cs=sizes(nc)

# modularity:
mq=modularity(nc)

dat=data.frame( cls=ms )
colnames(dat)=c("cls")

info=data.frame(cs, mq)
colnames(info)=c("cls","size","modurarityQ")

write.csv(dat,file="{oFile}",quote=FALSE,row.names=FALSE)
write.csv(info,file="{oInfo}",quote=FALSE,row.names=FALSE)
			'''.format( 
				eFile=eFile,dir=dir,wFile=wFile,ew=ew,
				nodeSize=nodeSize,oFile=oFile,oInfo=oInfo
			)

			with open(scpFile,"w") as fpw:
				fpw.write(r_proc_mo)
			
		else: # eb (edge betweenness)

			r_proc_eb = '''
library(igraph)
# reading edge file
g=read.graph("{eFile}",format="edgelist",directed={dir},n={nodeSize})
# reading weight file
w=read.csv("{wFile}")
E(g)$weight=as.list(w$"{ew}")
# do clustering
nc=cluster_edge_betweenness(g,weights=E(g)$weight,directed={dir},bridges=T,merges=T,modularity=T,edge.betweenness=T,membership=T)

# 置換
ms=cbind(membership(nc))
# Community sizes:
cs=sizes(nc)

# modularity:
mq=modularity(nc)

dat=data.frame( cls=ms )
colnames(dat)=c("cls")

info=data.frame(cs, mq)
colnames(info)=c("cls","size","modurarityQ")

write.csv(dat,file="{oFile}",quote=FALSE,row.names=FALSE)
write.csv(info,file="{oInfo}",quote=FALSE,row.names=FALSE)
			'''.format( 
				eFile=eFile,dir=dir,wFile=wFile,ew=ew,
				nodeSize=nodeSize,oFile=oFile,oInfo=oInfo
			)
			with open(scpFile,"w") as fpw:
				fpw.write(r_proc_eb)
		
		


	def g2pair(self,ni,nf,ei,ef1,ef2,ew,numFile,mapFile,weightFile):
		#MCMD::msgLog("converting graph files into a pair of numbered nodes ...")
		#wf=MCMD::Mtemp.new
		#wf1=wf.file
		#wf2=wf.file
		#wf3=wf.file
		
		allinObj =[]		
		
		
		wf1 = nm.mcut(f="%s:node"%(ef1),i=ei ).msetstr(v=0,a="flag")
		wf2 = nm.mcut(f="%s:node"%(ef2),i=ei ).msetstr(v=0,a="flag")


		f = None
		if nf:
			f <<= nm.mcut(i=[wf1,wf2,nm.mcut(f=nf+":node",i=ni).msetstr(v=1,a="flag")],f="node,flag")
			f <<= nm.mbest(k="node" , s="flag" , fr=0 ,size=1)
		else:
			f <<= nm.mcut(i=[wf1,wf2],f="node,flag")
			f <<= nm.muniq(k="node")
	
		f <<= nm.mnumber(s="flag,node",a="num",S=0,o=mapFile)

		f.run()
						
		f = None
		f <<= nm.mcut(f=[ef1,ef2],i=ei)
		f <<= nm.mjoin(k=ef1 , K="node",m=mapFile , f="num:num1")
		f <<= nm.mjoin(k=ef2 , K="node",m=mapFile , f="num:num2")
		f <<= nm.mcut(f="num1,num2")
		f <<= nm.mfsort(f="num1,num2")
		f <<= nm.msortf(f="num1%n,num2%n",nfno=True) 
		f <<= nm.cmd("tr ',' ' ' ")
		f <<= nm.mwrite(o=numFile)
		f.run()


		if ew :
				nm.mcut(f=ew,i=ei,o=weightFile).run()
		else:
			ew="weight"
			nm.msetstr(v=1 , a=ew ,i=ei).mcut(f=ew,o=weightFile).run()

		nodeSize=mrecount(i=mapFile)
		return nodeSize


	def convOrg(self,xxmap,xxout,ofile):

		xx1 = nm.mnumber(q=True,S=0,a="num",i=xxout)

		f =   nm.mjoin(k="num",f="cls",m=xx1,i=xxmap) 
		f <<= nm.mcut(f="node,cls", o=ofile)
		f.run()



	# ============
	# entry point
	def run(self,**kw_args):
	
		os.environ['KG_ScpVerboseLevel'] = "2"
		if "msg" in kw_args:
			if kw_args["msg"] == "on":
				os.environ['KG_ScpVerboseLevel'] = "4"

		# convert the original graph to one igraph can handle
		temp=Mtemp()
		xxnum = temp.file()
		xxmap = temp.file()
		xxwei = temp.file()
		xxout = temp.file()
		xxifo = temp.file()
		xxscp = temp.file()


		nodeSize=self.g2pair(self.ni,self.nf,self.ei,self.ef1,self.ef2,self.ew,xxnum,xxmap,xxwei)

		self.genRscript(self.directed,xxnum,xxwei,self.ew,nodeSize,self.al,xxout,xxifo,xxscp)

		if self.verbose :
			os.system("R --vanilla -q < %s"%(xxscp))
		else:
			os.system("R --vanilla -q --slave < %s 2>/dev/null "%(xxscp))
			
		# 元のデータに戻して出力
		self.convOrg(xxmap,xxout,self.oFile)

		nu.mmsg.endLog(self.__cmdline())


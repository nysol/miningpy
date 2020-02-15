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


class mgfeatures(object):

	helpMSG="""
----------------------------
#{CMD} version #{$version}
----------------------------
summary) calculation graph features by igraph
feature) output the following graph features
  node_size        : number of nodes
  edge_size        : number of edges
  degree0_node_size : number of nodes with 0 degree
  mean_degree      : mean of degree
  median_degree    : median of degree
  min_degree       : min of degree
  max_degree       : max of degree
  graph_density    : graph density
  transitivity     : so called clustering coefficient
  average_shortest_path    : mean of shortest path length for all pair of edges
  diameter         : max of shortest path length for all pair of edges

format) #{CMD} I=|(ei= [ni=]) ef= [nf=] O=|o= [log=] [T=] [--help]
args=MCMD::Margs.new(ARGV,"I=,ei=,ef=,ni=,nf=,o=,O=,diameter=,graph_density=,log=,-verbose","ef=,O=")
 I=     : path name of input files
         : file extention of edge file must be ".edge" in this path
         : file extention of node file must be ".node" in this path
  ei=    : input file name of edge (cannot be specified with I=)
  ef=    : field name of edge (two nodes)
  ni=    : input file name of nodes (cannot be specified with I=)
         : if omitted, only edge file is used
  nf=    : field name of node
  -directed : assume a directed graph
  O=     : output path

  ## parameter for each feature (see igraph manual in detail)
  diameter=unconnected=[TRUE|FALSE],directed=[TRUE|FALSE]
  graph_density=loops=[FALSE|TRUE]
  average_shortest_path=unconnected=[TRUE|FALSE],directed=[TRUE|FALSE]

  ## others
  mp=      : Number of processes for parallel processing
  T=       : working directory (default:/tmp)
  -mcmdenv : show the END messages of MCMD
  --help   : show help

required software)
  1) R
  2) igraph package for R

example)
$ cat data/dat1.edge
v1,v2
E,J
E,A
J,D
J,A
J,H
D,H
D,F
H,F
A,F
B,H
$ cat data/dat1.node
v
A
B
C
D
E
F
G
H
I
J
$ #{CMD} I=data O=data/result1 ef=v1,v2 nf=v O=result
#MSG# converting graph files into a pair of numbered nodes ...; 2015/10/20 14:57:26
#END# ../bin/mgfeatrues.rb I=./data O=result1 ef=v1,v2 nf=v; 2015/10/20 14:57:27
$ cat data/dat1.csv
id,node_size,edge_size,degree0_node_size,mean_degree,median_degree,min_degree,max_degree,graph_density,transitivity,average_shortest_path,diameter
dat1,10,10,3,2,2.5,0,4,0.222222222222222,0.409090909090909,1.61904761904762,3

# without specifying nf= (node file isn't used)
$ #{CMD} I=data O=data/result1 ef=v1,v2 O=result
#MSG# converting graph files into a pair of numbered nodes ...; 2015/10/20 14:57:26
#END# ../bin/mgfeatrues.rb I=./data O=result1 ef=v1,v2 nf=v; 2015/10/20 14:57:27
$ cat data/dat1.csv
id,node_size,edge_size,degree0_node_size,mean_degree,median_degree,min_degree,max_degree,graph_density,transitivity,average_shortest_path,diameter
dat1,10,10,0,2.85714285714286,3,1,4,0.476190476190476,0.409090909090909,1.61904761904762,3

# Copyright(c) NYSOL 2012- All Rights Reserved.

"""

	verInfo="version=0.1"

	paramter = {	
		"I":"directory",
		"O":"directory",
		"ei":"str",
		"ef":"str",
		"ni":"str",
		"nf":"str",
		"diameter":"str",
		"graph_density":"str",
		"average_shortest_path":"str",
		"mp":"int",
		"directed":"bool",
		"verbose":"bool"
	}
	paramcond = {	
		"hissu": ["ef","O"]
	}	

	def help():
		print(mgfeatures.helpMSG) 

	def ver():
		print(mgfeatures.verInfo)

	def __param_check_set(self , kwd):

		# 存在チェック
		for k,v in kwd.items():
			if not k in mgfeatures.paramter	:
				raise( Exception("KeyError: {} in {} ".format(k,self.__class__.__name__) ) )

		self.msgoff = True

		self.iPath  = kwd["I"] if "I" in kwd else None
		self.oPath  = kwd["O"] if "O" in kwd else None

		ef0 = kwd["ef"].split(",")
		self.ef1 = ef0[0]
		self.ef2 = ef0[1] 

		if self.iPath :
			import glob
			self.edgeFiles = glob.glob(self.iPath+"/*.edge")
			if len(self.edgeFiles) == 0 :
				raise Exception("#ERROR# no edge file is found matching with %s/*.edge"%(iPath))
		else:
			if not "ei" in kwd :
				raise Exception("#ERROR# ei= or I= is mandatory")
				
		self.ni = kwd["ni"] if "ni" in kwd else None
		self.nf = kwd["nf"] if "nf" in kwd else None

		self.directed = kwd["directed"] if "directed" in kwd else False
		self.verbose = kwd["verbose"]  if "verbose" in kwd else False

		self.MP  = int(kwd["mp"]) if "mp" in kwd else 4

		self.pars={}
		if "diameter" in kwd  :
			self.pars["diameter"] = "," + kwd["diameter"]
		else:
			self.pars["diameter"] = ""
			
		if "graph_density" in kwd  :
			self.pars["graph_density"] = "," + kwd["graph_density"]
		else:
			self.pars["graph_density"] = ""

		if "average_shortest_path" in kwd  :
			self.pars["average_shortest_path"] = "," + kwd["average_shortest_path"]
		else:
			self.pars["average_shortest_path"] = ""			

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



	####
	# generating the R script for graph features
	# pars: parameters for each graph feature
	def genRscript(self,directed,pars,eFile,nodeSize,oFile,scpFile):
		
		dir="TRUE" if directed else "FALSE"

		r_proc = '''
library(igraph)
## reading edge file
g=read.graph("{eFile}",format="edgelist",directed={dir},n={nodeSize})

####
deg=degree(g)
node_size=vcount(g)
edge_size=ecount(g)
mean_degree=mean(deg)
median_degree=median(deg)
min_degree=min(deg)
max_degree=max(deg)
degree0_node_size=length(deg[deg==0])
graph_density=graph.density(g {graph_density})
average_shortest_path=average.path.length(g {average_shortest_path})

#### diameter
diameter=diameter(g {diameter})
transitivity=transitivity(g)

dat=data.frame(
	node_size=node_size,
	edge_size=edge_size,
	degree0_node_size=degree0_node_size,
	mean_degree=mean_degree,
	median_degree=median_degree,
	min_degree=min_degree,
	max_degree=max_degree,
	graph_density=graph_density,
	transitivity=transitivity,
	average_shortest_path=average_shortest_path,
	diameter=diameter
)
write.csv(dat,file="{oFile}",quote=FALSE,row.names=FALSE)

		'''.format(
			eFile = eFile ,dir = dir,nodeSize = nodeSize ,
			graph_density = pars["graph_density"],
			average_shortest_path = pars["average_shortest_path"],
			diameter = pars["diameter"],oFile = oFile
		)
		with open(scpFile,"w") as fpw:
			fpw.write(r_proc)



	# return value is 10 (nodes)
	# "flag" on xxmap: 0:nodes in "ei", 1:nodes only in "ni".
	def g2pair(self,ni,nf,ei,ef1,ef2,numFile,mapFile):
		#MCMD::msgLog("converting graph files into a pair of numbered nodes ...")
		#wf=MCMD::Mtemp.new
		#wf1=wf.file
		#wf2=wf.file
		#wf3=wf.file
		
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
		#f << "mfsort f=num1,num2 |"
		f <<= nm.msortf(f="num1%n,num2%n",nfno=True)
		f <<= nm.cmd("tr ',' ' ' " )
		f <<= nm.mwrite(o=numFile)
		f.run()

		nodeSize=mrecount(i=mapFile)

		return nodeSize

	def runmain(self,edgeFile):
		import re

		baseName = re.sub('\.edge$',"",edgeFile)
		name = re.sub('^.*\/',"",baseName)
		nodeFile=re.sub('\.edge$',".node",edgeFile)

		# convert the original graph to one igraph can handle
		temp=Mtemp()
		xxnum = temp.file()
		xxmap = temp.file()
		xxout = temp.file()
		xxscp = temp.file()

		nodeSize=self.g2pair(nodeFile,self.nf,edgeFile,self.ef1,self.ef2,xxnum,xxmap)

		# generate R script, and run
		self.genRscript(self.directed,self.pars,xxnum, nodeSize, xxout, xxscp)
		if self.verbose :
			os.system("R --vanilla -q < %s"%(xxscp))
		else:
			os.system("R --vanilla -q --slave < %s 2>/dev/null "%(xxscp))

		nm.msetstr(v=name , a="id",i=xxout).mcut(x=True,f="0L,0-1L",o=self.oPath+"/"+name+".csv").run()


	# ============
	# entry point
	def run(self,**kw_args):
	
		os.environ['KG_ScpVerboseLevel'] = "2"
		if "msg" in kw_args:
			if kw_args["msg"] == "on":
				os.environ['KG_ScpVerboseLevel'] = "4"


		meach(self.runmain,self.edgeFiles,mpCount=self.MP)


		nu.mmsg.endLog(self.__cmdline())


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import nysol.util.margs as margs
import nysol.mining.mspade as mm
from nysol.util.mmkdir import mkDir

helpMSG="""
概要) 
内容) 
書式) mspade.py i= sid= item= time= O= [c=] [class=] [minSup=|minSupProb=] [maxSize=] 
                [maxLen=] [minGap=] [maxGap=] [maxWin=] 
                [topk=] [minSize=] [minLen=] [maxSup=] [minPprob=] 
                [oPats=] [oStats=] [oOccs=] [-maximal] [-(-)help]

	tid=>sid,item,time,cls
  i parameter
    i= 必須
    sid= 必須　
    item= 必須 
    time= 必須 
		class=
    csid= 
    c=

  e parameter
    minSup=
    minSupProb=
    maxSize= デフォルト:3 
    maxLen=
    minGap=
    maxGap=
    maxWin=
  o parameter
    -maximal
    topk=
    minSize=
    minLen=
    maxSup=
    minPprob=
    O= 必須

  その他
    -help : ヘルプの表示(2)

備考)


# Copyright(c) NYSOL 2012- All Rights Reserved.
		"""

#    oPats=
#    oStats=
#    oOccs=


paraList=[
	["i=","c=","sid=","item=","time=","class=","csid="] ,# ipara
	["minSup=","minSupProb=","maxSize=","maxLen=","minGap=","maxGap=","maxWin="] ,# epara
	["-maximal","O=","topk=","minSize=","minLen=","maxSup=","minPprob="] # opara
]
paraType={
	"i=":"str",
	"c=":"str",
	"sid=":"str",
	"item=":"str",
	"time=":"str",
	"class=":"str",
	"csid=":"str",
	"minSup=":"int",
	"minSupProb=":"float",
	"maxSize=":"int",
	"maxLen=":"int",
	"minGap=":"int",
	"maxGap=":"int",
	"maxWin=":"int",
	"-maximal":"bool",
	"topk=":"int",
	"minSize=":"int",
	"minLen=":"int",
	"maxSup=":"int",
	"minPprob=":"float",
	"oPats=":"str",
	"oStats=":"str",
	"oOccs=":"str",
	"O=":"str"
}


paraconvList={
	"i=":"iFile",
	"c=":"cFile",
	"class=":"cNames",
	"-maximal":"maximal"
}

if "-help" in sys.argv or "--help" in sys.argv:
	print(helpMSG)
	exit()

flat =[]
for para in paraList:
	flat.extend(para)	

#args=margs.Margs(sys.argv,",".join(flat),"i=,sid=,item=,time=,maxSize=,O=")
args=margs.Margs(sys.argv,",".join(flat),"i=,sid=,item=,time=,O=")

##make パラメータ


#ipara
iParams={}
for p in paraList[0] :
	val = None
	if paraType[p] == "int":
		val = args.int(p)	
	elif paraType[p] == "str":
		val = args.str(p)	
	elif paraType[p] == "fldstr":
		if args.str(p) != None:
			val = args.str(p).split(",")
	elif paraType[p] == "float":
		val = args.float(p)	
	elif paraType[p] == "bool":
		val = args.bool(p)	

	if p in paraconvList :
		iParams[paraconvList[p]] = val
	else:
		iParams[re.sub(r'=$',"",p)] = val

eParams={}
for p in paraList[1] :
	val = None
	if paraType[p] == "int":
		val = args.int(p)	
	elif paraType[p] == "str":
		val = args.str(p)	
	elif paraType[p] == "fldstr":
		val = args.str(p).split(",")
	elif paraType[p] == "float":
		val = args.float(p)	
	elif paraType[p] == "bool":
		val = args.bool(p)	

	if p in paraconvList :
		eParams[paraconvList[p]] = val
	else:
		eParams[re.sub(r'=$',"",p)] = val
		
	if not "maxSize=" in eParams or eParams["maxSize="] ==None:
		eParams["maxSize="]=3

oParams={}
for p in paraList[2] :
	val = None
	if paraType[p] == "int":
		val = args.int(p)	
	elif paraType[p] == "str":
		val = args.str(p)	
	elif paraType[p] == "fldstr":
		val = args.str(p).split(",")
	elif paraType[p] == "float":
		val = args.float(p)	
	elif paraType[p] == "bool":
		val = args.bool(p)	

		
	if p in paraconvList :
		oParams[paraconvList[p]] = val
	else:
		if p == "O=":
			# Oは　oPats= oStats= oOccs=に分割
			# pattern.csv、stat.csv、occurence.csv
			mkDir(val) 
			valD = re.sub(r'/$',"",val)
			oParams["oPats"]= "%s/%s"%(valD,"pattern.csv")
			oParams["oStats"]= "%s/%s"%(valD,"stat.csv")
			oParams["oOccs"]= "%s/%s"%(valD,"occurence.csv")
		else:
			oParams[re.sub(r'=$',"",p)] = val


spade=mm.Spade(iParams,eParams,oParams)


rules=spade.run()



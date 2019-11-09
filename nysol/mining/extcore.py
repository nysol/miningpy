#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nysol.mining import _sketchsortlib as lib_sketchsort


       
def _kwd2list(args, kw_args,paraConf,extpara=None):
	def tostr(val):
		if isinstance(val,list):
			newlist=[]
			for cval in val:
				newlist.append(str(cval))
			if len(newlist) != 0 :
				return ",".join(newlist)
			else:
				return None
		else:
			return str(val)

	if len(args)>1:
		raise Exception("args zero or one ")

	if len(args)==1 and not isinstance(args[0],dict) :
		raise Exception("args is not dict")

	# dict Merge		
	if len(args)==1:
		kw_args.update(args[0])

	# 可能パラメータ設定
	enablePara = set([])
	for v in paraConf.values():
		for vv in v:
			enablePara.add(vv[0])

	# 可能パラメータCHECK
	for k in kw_args.keys():
		if not k in enablePara:
			raise Exception("Unknown parameter")

	newargs=[]
	if "saki" in paraConf:
		for paraInfo in paraConf["saki"]:
			if paraInfo[0] in kw_args:
				newargs.append(tostr(kw_args[paraInfo[0]]))
			elif paraInfo[1] == 1:
				raise Exception("not find necceary parameter")
				
	if "opt" in paraConf:
		for paraInfo in paraConf["opt"]:
			if paraInfo[0] in kw_args:
				newargs.append(tostr(paraInfo[1]))
				newargs.append(tostr(kw_args[paraInfo[0]]))

	if "opts" in paraConf:
		for paraInfo in paraConf["opts"]:

			if paraInfo[0] in kw_args:

				newargs.append(tostr(paraInfo[1]))

				if isinstance(kw_args[paraInfo[0]],list):
					if len(kw_args[paraInfo[0]])!=paraInfo[2] :
						raise Exception("not valid parameter")
					for val in kw_args[paraInfo[0]]:
						newargs.append(tostr(val))

				elif isinstance(kw_args[paraInfo[0]],str):
					optsub = kw_args[paraInfo[0]].split(",") 
					if len(optsub)!=paraInfo[2] :
						raise Exception("not valid parameter")
					for val in optsub:
						newargs.append(tostr(val))
				
				else:
					raise Exception("not valid parameter")


	if "addkw" in paraConf:
		for paraInfo in paraConf["addkw"]:

			if paraInfo[0] in kw_args:

				if isinstance(kw_args[paraInfo[0]],list):

					if len(kw_args[paraInfo[0]])==1:
						newargs.append( tostr(paraInfo[1]) )
					elif len(kw_args[paraInfo[0]])==2:
						newargs.append( tostr(paraInfo[1])+tostr(kw_args[paraInfo[0]][1]))
					else:
						raise Exception("not valid parameter")

					newargs.append(tostr(kw_args[paraInfo[0]][0]))


				elif isinstance(kw_args[paraInfo[0]],str):
					optsub = kw_args[paraInfo[0]].split(",") 
					if len(optsub)==1:
						newargs.append(tostr(paraInfo[1]) )
					elif len(optsub)==2:
						newargs.append(tostr(paraInfo[1])+tostr(optsub[1]) )
					else:
						raise Exception("not valid parameter")

					newargs.append(tostr(optsub[0]))
				
				else:
					raise Exception("not valid parameter")

	if "optB" in paraConf:
		for paraInfo in paraConf["optB"]:
			if paraInfo[0] in kw_args:
				if kw_args[paraInfo[0]]:
					 newargs.append(tostr(paraInfo[1]))


	if "optato" in paraConf:
		for paraInfo in paraConf["optato"]:
			if paraInfo[0] in kw_args:
				newargs.append(tostr(paraInfo[1]))
				newargs.append(tostr(kw_args[paraInfo[0]]))

	if "ato" in paraConf:
		for paraInfo in paraConf["ato"]:
			if paraInfo[0] in kw_args:
				newargs.append(tostr(kw_args[paraInfo[0]]))
			elif paraInfo[1] == 1:
				raise Exception("not find necceary parameter")



	if isinstance(extpara,dict) and "ext" in paraConf:
		for paraInfo in paraConf["ext"]:
			if paraInfo[0] in kw_args:
				extpara[paraInfo[1]] = tostr(kw_args[paraInfo[0]])
	
	return newargs
       
def sketchsort(*args,**kw_args):

	"""
       -hamdist [maximum hamming distance]
       (default: 1)
       -numblocks [the number of blocks]
       (default: 4)
       -cosdist [maximum cosine distance]
       (default: 0.01)
       -numchunks [the number of chunks]
       (default: 3)
       -missingratio 
       (default: 0.0001)
       -windowsize
       (default: 0)
       -seed      
       
				この二つtrue false
       -centering
       -auto 

	"""

	paraLIST={
		"ato":[("i",1),("o",1)],
		"opt":[("hamdist","-hamdist"),("numblocks","-numblocks"),("cosdist","-cosdist"),
					("numchunks","-numchunks"),("missingratio","-missingratio"),
					("windowsize","-windowsize"),("seed","-seed")],
		"optB":[("centering","-centering"),("auto","-auto")]
	}


 ##e= tid= [dist=] [th=] [mr=] [wf=] [ws=] [dist=C|H] i= [o=] [--help]

	kwd = _kwd2list(args,kw_args,paraLIST)
	return lib_sketchsort.sketchsort_run(kwd)
         

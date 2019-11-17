#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import nysol.util.margs as margs
import nysol.mining.mcarm as mmc
from nysol.util.mmkdir import mkDir


# entry point
argv=sys.argv
if not ( len(argv)==2 or len(argv)==3 ):
	print("m2bonsai.py ")
	print("%s 設定ファイル(yaml|json)"%argv[0])
	exit()

# configファイルの読み込み
#import importlib
#configFile=os.path.expanduser(argv[1])
#sys.path.append(os.path.dirname(configFile))
#config=importlib.import_module(os.path.basename(configFile).replace(".py",""))

configFile=os.path.expanduser(argv[1])

if len(argv) > 2:
	if argv[2] == "-usingJSON" :
		import json
		with open(configFile, 'r') as rp:
			config = json.load(rp)
	else:
		import yaml
		with open(configFile, 'r') as rp:
			config = yaml.load(rp)

else:
	import yaml
	with open(configFile, 'r') as rp:
		config = yaml.load(rp)


mco = mmc.mcarm(config)	
mco.run()


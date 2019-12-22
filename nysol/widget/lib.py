#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from datetime import datetime
import os
import re
import importlib

def csv2pd3(csvFile,top):
	"""import pandas as pd
pd.set_option('display.max_columns', 100)
df = pd.read_csv("{csvFile}",nrows={top}, encoding="utf-8")
df
"""

class csv2pd2(object):
	"""import pandas as pd
pd.set_option('display.max_columns', 100)
df = pd.read_csv("{csvFile}",nrows={top}, encoding="utf-8")
df
"""
	def __init__(self,csvFile,top=50):
		self.csvFile=csvFile
		self.top=top

	def run(self):
		para={"csvFile":"./xxa" , "top":10}
		print(self.__doc__.format(**para))


class csv2pivot(object):
	def __init__(self,csvFile):
		self._version="0.10"
		self._date=datetime.now()

		self.params={"csvFile":csvFile}

	def script(self):
		scp="""### 自動生成スクリプト
import pandas as pd
from pivottablejs import pivot_ui
# csvをpandas DataFrameに変換(nrowsで変換する行数を指定している)
df = pd.read_csv("{csvFile}", encoding="utf-8")
pivot_ui(df)
""".format(**self.params)
		return scp

class csv2pd(object):
	def __init__(self,csvFile,top=50):
		self._version="0.10"
		self._date=datetime.now()

		self.params={"csvFile":csvFile,"top":top}

	def script(self):
		scp="""### 自動生成スクリプト
import pandas as pd
# jupyter上に表示する際に省略せずに表示する最大列数を設定する
pd.set_option('display.max_columns', 100)
# csvをpandas DataFrameに変換(nrowsで変換する行数を指定している)
df = pd.read_csv("{csvFile}",nrows={top}, encoding="utf-8")
df # 表示
""".format(**self.params)
		return scp

	def run(self):
		scp=self.script()
		exec(scp)

def getFileAttribute(fName):
	ct=datetime.fromtimestamp(os.path.getctime(fName))
	size=os.path.getsize(fName)
	#at=datetime.fromtimestamp(os.path.getatime(fName))
	#mt=datetime.fromtimestamp(os.path.getmtime(fName))
	text=[]
	text.append("file name: "+fName)
	text.append("作成日時: "+str(ct)+"  サイズ: "+str(size))

	return "\n".join(text)

def sampleTXT(txtFile,top=50):
	if top<=0:
		return ""
	text=""
	try:
		with open(txtFile, 'r') as f:
			for i in range(top):
				line=f.readline()
				if not line:
					break
				text+=line
	except:
		pass
	return text

def getCSVheader(csvFile):
	dat = pd.read_csv(csvFile,nrows=1,dtype=str)
	dat=dat.columns.tolist()
	dat=[re.sub("%.*","",v) for v in dat]
	return dat
	"""
	flds=None
	try:
		with open(csvFile, 'r', encoding="utf_8") as f:
			reader = csv.reader(f)
			for row in reader:
				flds=row
				break
	except:
		pass
	return flds
"""

# lib: "nysol.mining.ctree"
def readSource(lib,func=None,deepOutput=True,skip=None):
	script=""
	if deepOutput:
		mod = importlib.import_module(lib)
		with open(mod.__file__) as f:
			while True:
				line = f.readline()
				if not line:
					break
				if skip is not None:
					match=False
					for word in skip:
						if word in line:
							match=True
							break
					if match:
						continue
				if re.search(r"if *__name__ *== *[\"']__main__[\"']:.*",line) is not None:
					break
				script+=line

		#script=re.sub("if *__name__ *== *[\"']__main__[\"']:.*","",script,flags=(re.MULTILINE | re.DOTALL))
	else:
		script="from %s import %s\n"%(lib,func)
	return script

def iFileCheck(iFile,msg):
	if iFile is None:
		msg.value = "##ERROR: 入力ファイルが指定されていません。"
		return False
	if not os.path.isfile(iFile):
		msg.value = "##ERROR: 入力にはテキストファイルを指定して下さい。"
		return False
	return True

def iPathCheck(iPath,msg):
	if type(iPath)==str:
		iPaths=[iPath]
	elif type(iPath)==list or type(iPath)==tuple:
		iPaths=iPath
	else:
		return False
	for path in iPaths:
		if not os.path.isdir(path):
			msg.value = "##ERROR: ディレクトリでない入力が指定されています: %s"%(path)
			return False
	return True
	
def oPathCheck(oPath,msg):
	if oPath is None:
		msg.value = "##ERROR: 出力パスが指定されていません。"
		return False
	if os.path.isfile(oPath):
		msg.value = "##ERROR: 出力dir名と同名のファイルが既に存在します。"
		return False
	#if not os.path.isdir(oPath):
	#	msg_w_value = "##ERROR: 出力dirにはディレクトリを指定して下さい。"
	#	return False
	return True

def blankCheck(var,title,msg):
	if var is None or var=="":
		msg.value = "##ERROR: %sが指定されていません。"%title
		return False
	return True

if __name__=='__main__':

	obj=csv2pd("./xxa",top=10)
	print(obj.script())
	obj.run()

	source=readSource("nysol.mining.ctree")
	print(source)

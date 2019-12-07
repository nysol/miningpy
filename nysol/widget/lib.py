#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from datetime import datetime
import os
import re

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

def sampleFormatter(fName):
	script=None
	if fName[-4:]==".csv":
		gen=csv2pd(fName,50)
	return gen.script()

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

if __name__=='__main__':
	obj=csv2pd("./xxa",top=10)
	print(obj.script())
	obj.run()


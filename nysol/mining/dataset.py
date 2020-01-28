#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
from pprint import pprint
import nysol.mcmd as nm
from nysol.util.mtemp import Mtemp
import nysol.util.mheader as mheader
import numpy as np
import pandas as pd
import time

def show(df):
	className=df.__class__.__name__
	if className!="DataFrame":
		raise BaseException("##ERROR: unknown data type: %s (line %d)"%(keyword,lineNo))

	print("#####",className)
	print("## data(top 5 lines):")
	print(df[:5])
	print("## len(df):",len(df))
	print("## df.dtypes:")
	print(df.dtypes)
	print("## df.isnull().sum():")
	print(df.isnull().sum())

def load_config(configFile):
	with open(configFile,"r") as fpr:
		text=fpr.readlines()
	#print(text)

	config=[]
	data=None
	lineNo=0
	for line in text:
		lineNo+=1
		line=line.strip()
		#print("####",line)
		if line=="" or line[0]=="#":
			continue

		if re.match(r'^.*{$',line):
			keyword=line[:-1].strip()
			if keyword in ["table","transaction","sequence"]:
				data={}
				data["type"]=keyword
				data["names"]=[]
				data["convs"]=[]
			else:
				raise BaseException("##ERROR: unknown data type: %s (line %d)"%(keyword,lineNo))
		elif line=="}":
			config.append(data)
		else:
			split=line.split(":")
			split=[s.strip() for s in split]

			if len(split)!=2:
				raise BaseException("syntax error in %s (line %d)"%(line,lineNo))
			else:
				data["names"].append(split[0])
				data["convs"].append(split[1])

	if len(config)==1:
		config=config[0]
	#pprint(config)
	return config

def conv_id(data,name):
	return data.set_index(name)
def conv_numeric(data,name,dtype=float):
	return data.astype({name: dtype})
def conv_category(data,name):
	return data.astype({name: "category"})
def conv_class(data,name):
	return data.astype({name: "category"})
def conv_as(data,name,dtype):
	return data.astype({name: dtype})
def conv_dummy(data,name,drop_first=True,dummy_na=False,dtype=float):
	return pd.get_dummies(data,columns=[name],
			drop_first=drop_first, dummy_na=dummy_na, dtype=dtype)

def mkTable(config,source):
	if config.__class__.__name__=="str":
		config=load_config(config)

	if ("type" not in config) or (config["type"]!="table"):
		raise BaseException("##ERROR: bad config, seems not for table class")

	#config["vars"]=[
	#		["Sex"     ,"dummy",{"drop_first":True,"dummy_na":False,"dtype":float}],
	#		["Length"  ,"numeric",{}],
	#		["Diameter","numeric",{}],
	#              :
	names=[var[0] for var in config["vars"]]
	if type(source)==str:
		dat = pd.read_csv(source,dtype=str) # 一旦strとして読み込み
		csv_names=dat.columns.to_list() # 項目名に%が含まれていればそれ以降削除
		csv_names=[re.sub("%.*$","",v) for v in csv_names] ## mcmd csv出力対策: %nなどの除去
		dat.columns=csv_names
		# check names
		for name in  names:
			if name not in csv_names:
				raise BaseException("##ERROR: field name not found in csv data: %s"%name)
		data=dat.loc[:,names]

	elif type(source) in [list,np.ndarray]:
		if len(source)==0:
			raise BaseException("##ERROR: empty data found in list data source")
		data=pd.DataFrame(source, columns=names)

	# 型毎に変数をまとめる(pandasで一つずつ変数を変換していては遅いため)
	eachConv={}
	for i,var in enumerate(config["vars"]):
		if len(var)!=3:
			raise BaseException("##ERROR: sintax error in config['vars'] : %s"%(var))
		name =var[0]
		type_=var[1] # numeric,category,dummy,...
		param=var[2] # {"drop_first":True,...}
		#print("var",i,var)
		if type_ not in ["id","numeric","category","class","dummy"]:
			raise BaseException("##ERROR: unknown variable type : (%s,%s)"%(name,type_))
		if type_ not in eachConv:
			eachConv[type_]=[]
		eachConv[type_].append([name,param])

	for key,vars_ in eachConv.items():
		#print("kv",key,vars_)
		if key=="id":
			for var in vars_:
				name=var[0]
				data=data.set_index(name)
				break # 複数指定していても先頭のみ対応、後は無視
		elif key=="numeric":
			dtypes={}
			for var in vars_:
				name=var[0]
				dtypes[name]=float
			data=data.astype(dtypes)
		elif key=="category":
			dtypes={}
			for var in vars_:
				name=var[0]
				dtypes[name]="category"
			data=data.astype(dtypes)
		elif key=="class":
			dtypes={}
			for var in vars_:
				name=var[0]
				dtypes[name]="category"
			data=data.astype(dtypes)
		if key=="dummy":
			#print("var",var)
			for var in vars_: # dummyは1項目ずつ
				name=var[0]
				param=var[1]
				data=pd.get_dummies(data,columns=[name],**param)

	'''
	for i,conv in enumerate(convs):
		# configのconv文字列の内容を型に応じたメソッド名を変更してそのまま実行する
		if re.match(r"^id\(",conv):
			data=eval(conv.replace("id(","conv_id(data,'%s'"%(names[i])))
		elif re.match(r"^numeric\(",conv):
			data=eval(conv.replace("numeric(","conv_numeric(data,'%s',"%(names[i])))
		elif re.match(r"^category\(",conv):
			data=eval(conv.replace("category(","conv_category(data,'%s',"%(names[i])))
		elif re.match(r"^class\(",conv):
			data=eval(conv.replace("class(","conv_class(data,'%s',"%(names[i])))
		elif re.match(r"^dummy\(",conv):
			data=eval(conv.replace("dummy(","conv_dummy(data,'%s',"%(names[i])))
		elif re.match(r"^as\(",conv):
			data=eval(conv.replace("as(","conv_as(data,'%s',"%(names[i])))
		else: # no conversion (as("object")含む)
			pass
	'''
	#print("time:",i,len(convs),time.time()-st)
	#print(data)
	return data

def tra2tbl(tra,idName,itemName,dtype="float16"):
	num2str=tra[itemName].cat.categories.to_list()
	str2num={v:i for i,v in enumerate(num2str)}
	#print(num2str)
	#print(str2num)
	data=[]
	ids=[]
	for key,items in tra.groupby([idName]):
		# print(key)
		# 100
		# print(items.__class__.__name__)
		# DataFrame
		# print(items)
		# id item
		# 0  100    b
		# 1  100    f
		# 2  100    h
		# 3  100    i
		line=[0]*(len(str2num)+1)
		for index,row in items.iterrows():
			line[str2num[row[itemName]]]=1
		line[-1]=key
		data.append(line)

	config={}
	config["type"]="table"
	config["names"]=[itemName+"_"+s for s in num2str]+[idName]
	config["convs"]=["numeric(dtype='%s')"%(dtype)]*len(str2num)+["id()"]
	tbl=mkTable(config,data)
	return tbl

def cut(df,flds,reverse=False):
	if reverse:
		rev_flds=[]
		for fld in df.columns.to_list():
			if not fld in flds:
				rev_flds.append(fld)
		flds=rev_flds
	return df.loc[:,flds]

def join(tableList):
	concat=[]
	for tbl in tableList[1:]:
		concat.append(tbl)
	joinedTBL=tableList[0].join(concat)
	return joinedTBL

if __name__ == '__main__':
	with open("xxa.csv","w") as f:
		f.write("""a%n0,b
10,abc
20,def
""")
	config={}
	config["type"]="table"
	config["names"]=["a","b"]
	config["convs"]=["as('int64')","as('object')"]
	dat=mkTable(config,"xxa.csv")
	show(dat)

	configFile="config/crx_tra.dsc"
	tra=mkTable(configFile,"data/crx_tra1.csv")

	show(tra)
	tratbl=tra2tbl(tra,"id","item")
	show(tratbl)

	configFile="config/crx2.dsc"
	tbl=mkTable(configFile,"data/crx2.csv")
	show(tbl)
	cls=cut(tbl,["class"])
	show(cls)
	oth=cut(tbl,["class"],reverse=True)
	show(oth)

	data=[
			[1,"a",1.2],
			[2,"b",1.3]
			]
	config={}
	config["type"]="table"
	config["names"]=["key","商品","金額"]
	config["convs"]=["id()","category()","numeric()"]
	smalltbl=mkTable(config,data)
	show(smalltbl)

	jtbl=join([tbl,tratbl])
	show(jtbl)


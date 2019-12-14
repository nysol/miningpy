#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
warnings.simplefilter('ignore')

import os
import sys
import numpy as np
import pickle
import json
import re
import pandas as pd

def csv2df(iFile,idFld,numFlds,catFlds,dmyFlds):
	# とりあえずstrとして全読み込み
	df = pd.read_csv(iFile,dtype=str)
	df = df.dropna() # NA行は省く
	# 引数から変数名一覧を作成
	names=[idFld]+numFlds+catFlds+dmyFlds
	# 利用する項目のみ選択する
	ds=df.loc[:,names]

	# 各変数の型に従って型変換
	if idFld is not None: # id項目はindexにする
		ds=ds.set_index(idFld)
	for name in numFlds:
		ds=ds.astype({name: float})
	for name in catFlds:
		ds=ds.astype({name: "category"})
	if len(dmyFlds)>0:
		ds=pd.get_dummies(ds,columns=dmyFlds, drop_first=True, dummy_na=False, dtype=float)

	return df,ds # オリジナルと型設定後の両方を返す

if __name__ == '__main__':
	iFile="/Users/hamuro/nysol/miningpy/nysol/mining/data/crx2.csv"
	df,ds=csv2pd(iFile,"id",["n1","n2","n3","n4"],["class"],["d1","d2","d3","i1","i2"])
	print(ds)


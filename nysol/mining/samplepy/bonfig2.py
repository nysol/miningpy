
dataset={
	##### サンプルID (iFile,traFile,seqFile共通)
	"idFld":"id",
	"iFile":{

		##### 基本データセット
		## ファイル名
		"name":"yakir.csv",
		## カテゴリ項目名
		#cFlds:["d1","d2","d3"]
		"cFlds":["タン","カルビ","性別"],
		## 数値項目名
		#nFlds:["n1","n2","n3","n4"]
		"nFlds":["年令"],
		## アイテム項目名
		# i1: 14 alphabets : aa, c, cc, d, e, ff, i, j, k, m, q, r, w, x
		# i2:  9 alphabets : bb, dd, ff, h, j, n, o, v, z
		#"iFlds":["i1","i2"],
		#"iSize":[2,3],
		## 目的変数項目名
		"yFld":"売上",
		## 目的変数タイプ(r:regression,c:classification
		"yType":"r"
	},

	# tra1: 9 alphabets : a b c d e f g h i
	# tra2: 9 alphabets : a b c d e f g h i
	"traFiles":[
		#{
		#	"name":"data/crx_tra1.csv",
		#	"iSize":3,
		#},
		#{
		#	"name":"data/crx_tra2.csv",
		#	"iSize":4,
		#}
	],

	"seqFiles":[
		#{
		#	"name":"data/crx2_seq1.csv",
		#	"fields":"id,time,item",
		#	"iSize":2,
		#},
		#{
		#	"name":"data/crx2_seq2.csv",
		#	"fields":"id,time,item",
		#	"iSize":3,
		#}
	]

}

'''
seqFiles=[
	{
		"fName":"seq1.csv",
		"indexSize":2,
		"seqType":"str",
		"ordered":False,
		"minGap":10,
		"minWin":100
	}
]
'''

dTree={
	"max_depth":3
}

rTree={
	"max_depth":3
}

oPath="result1"


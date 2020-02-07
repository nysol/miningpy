
dataset={
	##### サンプルID (tblFile,traFile,seqFile共通)
	"idFld":"id",
	"tblFile":{

		##### 基本データセット
		## ファイル名
		"name":"data/crx2.csv",
		## カテゴリ項目名
		#cFlds:["d1","d2","d3"]
		"cFlds":["d1"],
		## 数値項目名
		#nFlds:["n1","n2","n3","n4"]
		"nFlds":["n1"],
		## アイテム項目名
		# i1: 14 alphabets : aa, c, cc, d, e, ff, i, j, k, m, q, r, w, x
		# i2:  9 alphabets : bb, dd, ff, h, j, n, o, v, z
		"iFlds":["i1","i2"],
		"iSize":[2,3],
		## 目的変数項目名
		"yFld":"class",
		## 目的変数タイプ(r:regression,c:classification
		"yType":"c"
	},

	# tra1: 9 alphabets : a b c d e f g h i
	# tra2: 9 alphabets : a b c d e f g h i
	"traFiles":[
		{
			"name":"data/crx_tra1.csv",
			"key":"id",
			"item":"item",
			"iSize":3,
		},
		{
			"name":"data/crx_tra2.csv",
			"key":"id",
			"item":"item",
			"iSize":4,
		}
	],

	"seqFiles":[
		{
			"name":"data/crx2_seq1.csv",
			"fields":"id,time,item",
			"iSize":2,
			"eParams":{
				"minSup":2,        # 最小サポート(件数)
				"minSupProb":None, # 最小サポート(確率) minSupがNoneでなければminSup優先
				"maxSize":4,       # パターンを構成する総アイテム数の上限
				"maxLen":3,        # パターンを構成する総エレメント数の上限
				"minGap":None,     # エレメント間最小ギャップ長
				"maxGap":None,     # エレメント間最大ギャップ長
				"maxWin":None      # 全体のマッチ幅最大長
			},
			"oParams":{
				"maximal":False,     # 極大パターンのみ選択
				"topk":20,           # 上位ルール
				"minSize":None,      # maxSizeの最小版
				"minLen":None,       # maxLenの最小版
				"maxSup":None,       # minSupの最大版
				"minPprob":None,      # 最小事後確率
			}
		},
		{
			"name":"data/crx2_seq2.csv",
			"fields":"id,time,item",
			"iSize":3,
			"eParams":{
				"minSup":2,        # 最小サポート(件数)
				"minSupProb":None, # 最小サポート(確率) minSupがNoneでなければminSup優先
				"maxSize":4,       # パターンを構成する総アイテム数の上限
				"maxLen":3,        # パターンを構成する総エレメント数の上限
				"minGap":None,     # エレメント間最小ギャップ長
				"maxGap":None,     # エレメント間最大ギャップ長
				"maxWin":None      # 全体のマッチ幅最大長
			},
			"oParams":{
				"maximal":False,     # 極大パターンのみ選択
				"topk":20,           # 上位ルール
				"minSize":None,      # maxSizeの最小版
				"minLen":None,       # maxLenの最小版
				"maxSup":None,       # minSupの最大版
				"minPprob":None,      # 最小事後確率
			}
		}
	]
}


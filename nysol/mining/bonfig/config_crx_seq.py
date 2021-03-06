
dataset={
	##### サンプルID (tblFile,traFile,seqFile共通)
	"idFld":"id",
	"tblFile":{

		##### 基本データセット
		## ファイル名
		"name":"data/crx2.csv",
		## 目的変数項目名
		"yFld":"class",
		## 目的変数タイプ(r:regression,c:classification
		"yType":"c"
	},

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
				"maxWin":4         # 全体のマッチ幅最大長
			},
			"oParams":{
				"maximal":False,     # 極大パターンのみ選択
				"topk":20,           # 上位ルール
				"minSize":None,      # maxSizeの最小版
				"minLen":None,       # maxLenの最小版
				"maxSup":None,       # minSupの最大版
				"minPprob":0.7,      # 最小事後確率
				"oPats":"xxoutPats",   # パターン出力ファイル(Noneで出力しない)
				"oStats":"xxoutStats", # 統計量出力ファイル(Noneで出力しない)
				"oOccs":"xxoutOccs"    # 出現出力ファイル(Noneで出力しない)
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
				"maxWin":4         # 全体のマッチ幅最大長
			},
			"oParams":{
				"maximal":False,     # 極大パターンのみ選択
				"topk":20,           # 上位ルール
				"minSize":None,      # maxSizeの最小版
				"minLen":None,       # maxLenの最小版
				"maxSup":None,       # minSupの最大版
				"minPprob":0.7,      # 最小事後確率
				"oPats":"xxoutPats",   # パターン出力ファイル(Noneで出力しない)
				"oStats":"xxoutStats", # 統計量出力ファイル(Noneで出力しない)
				"oOccs":"xxoutOccs"    # 出現出力ファイル(Noneで出力しない)
			}
		}
	]
}


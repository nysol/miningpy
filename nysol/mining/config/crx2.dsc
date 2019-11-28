# tableデータ生成用configファイル

table {
	id : id()
	n1 : numeric()
	n2 : numeric()
	n3 : numeric()
	n4 : numeric()
	d1 : dummy(dummy_na=True,drop_first=True,dtype=np.float16)
	d2 : dummy()
	d3 : dummy()
	i1 : dummy()
	i2 : dummy()
	class : class()
}


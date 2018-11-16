d = {"one":1, "two":2, "three":3}
print(d.get("on333"))

# get默认值是None，可以设置
print(d.get("one", 100))
print(d.get("one333", 100))

#体会以下代码跟上面代码的区别
print(d["one"])
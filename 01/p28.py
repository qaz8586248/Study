from __future__ import print_function
import re
content = '333STR1666STR299'
regex = r'([A-Z]+(\d))'
if __name__ == '__main__':
    print(re.match(regex, content)) ##content的开头不符合正则，所以结果为None。 ##只会找一个匹配，match[0]是regex所代表的整个字符串，match[1]是第一个()中的内容，match[2]是第二对()中的内容。
    match = re.search(regex, content)
    print('\nre.search() return value: ' + str(type(match)))
    print(match.group(0), match.group(1), match.group(2))
    result1 = re.findall(regex, content)
    print('\nre.findall() return value: ' + str(type(result1)))
    print(result1)
    for m in result1:
        print(m[0], m[1])

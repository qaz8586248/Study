#获取文件夹下的文件大小，不考虑还有子目录的情况
import os

all_files=os.listdir(os.curdir)
listfile={}

for each_file in all_files:
    if os.path.isfile(each_file):
        listfile[each_file]=os.path.getsize(each_file)

for k,v in listfile.items():
    print(k,'-----',v)
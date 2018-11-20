#递归查询目录下的所有文件，包括子目录下的文件
import os

all_files=os.listdir(os.curdir)
listfile=[]


def kkk(mulu):
    for i in mulu:
        if os.path.isfile(i):
            listfile.append(i)
    for k in mulu:
        if os.path.isdir(k):
            os.chdir(k)
            mulu_1=os.getcwd()
            all_files_1=os.listdir(mulu_1)
            kkk(all_files_1)

kkk(all_files)
print(listfile)





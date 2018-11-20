import logging

def log(func):
    def wrapper(*args,**kwargs):
        print(func.__name__)
        logging.error("wocuole")
        return func(*args,**kwargs)
    return wrapper

@log
def sss():
    print("shuishen")

sss()
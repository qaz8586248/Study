# 子类扩充父类功能的案例
# 人由工作的函数， 老师也由工作的函数，但老师的工作需要讲课
class Person():
    name = "NoName"
    age = 18
    __score = 0  # 考试成绩是秘密，只要自己知道
    _petname = "sec"  # 小名，是保护的，子类可以用，但不能公用

    def sleep(self):
        print("Sleeping ... ...")

    def work(self):
      #  self.name = 'haha'
        print("make some money{0}".format(self.name))

# 父类写在括号内
class Teacher(Person):
    teacher_id = "9527"
    name = "DaNa"

    def make_test(self):
        print("attention")

    def work(self):
        # 扩充父类的功能只需要调用父类相应的函数
        # Person.work(self)
        # 扩充父类的另一种方法
        # super代表得到父类
        self.name = 'gege'
        super().work()
        self.make_test()
        print(self.name)


t = Teacher()
t.work()
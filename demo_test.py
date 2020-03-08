'''
 AUTH:RODDY
 DATE:2020/3/1
 TIME:14:44
 FILE:demo_test.py
 '''

'''244369101@qq.com
vimtkpuxbbcfbgjd'''

'''

'''
import smtplib
from email.mime.text import MIMEText
#连接smpt服务
smtp = smtplib.SMTP_SSL(host='smtp.qq.com',port=465)
smtp.login(user='244369101@qq.com',password='vimtkpuxbbcfbgjd')
#第二步构建一个邮件
cont='content'
msg=MIMEText(cont,_charset='utf8')
#主题
msg['Subject']='测试邮件'
#发件人
msg['From']='244369101@qq.com'
#收件人
msg['To']='244369101@qq.com'
#第三步发送邮件
smtp.send_message(msg,from_addr='244369101@qq.com',to_addrs=['244369101@qq.com','15172314560@139.com'])
#




#
# class A():
#     def __init__(self):
#         self.a='A is a'
#         self.b='A is b'
#     def add(self):
#         print(self.a,self.b)
# class B(A):
#     def __init__(self):
#         #super().__init__()
#         self.a='B is a '
#     def acc(self):
#         print(self.a,self.b)
# b=B()
# b.acc()

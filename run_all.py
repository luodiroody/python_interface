'''
 AUTH:RODDY
 DATE:2020/2/29
 TIME:16:02
 FILE:run_withdraw.py
 '''
import unittest
import os
from libray.HTMLTestRunnerNew import HTMLTestRunner
from common.dirpath import TESTCASEPATH,REPORTPATH
from common.handlemail import sendemai

suit = unittest.TestSuite()

load= unittest.TestLoader()

suit.addTest(load.discover(TESTCASEPATH))

runner = HTMLTestRunner(stream=open(os.path.join(REPORTPATH,'result.html'),'wb'),
                        title=u'测试报告',
                        description='前程贷相关接口',
                        tester='roody')
runner.run(suit)
sendemai('result.htnl','测试报告')

'''
 AUTH:RODDY
 DATE:2020/2/29
 TIME:21:01
 FILE:testcase_add.py
 '''
import unittest
import os
import jsonpath
from decimal import Decimal
from libray.ddt import ddt,data
from common.readexcel import ReadExcel
from common.config import conf
from common.dirpath import DATAPATH
from common.handlrequst import SendRequest
from common.handlereplace import ReplaceData
from common.handlemysql import Connet
from common.handlelog import log
@ddt
class TestCaseAdd(unittest.TestCase):
    readexcel=ReadExcel(filename=os.path.join(DATAPATH,conf.get('workbook','name')),
                        sheetname=conf.get('workbook','sheet05'))
    cases=readexcel.read_excel()
    send = SendRequest()
    headers = eval(conf.get('env','headers'))
    base_url=conf.get('env','url')
    connet=Connet()
    sql='select leave_amount from futureloan.member WHERE  mobile_phone = {}'.format(conf.get('env','phone'))
    replacedata = ReplaceData()
    @data(*cases)
    def testcase_add(self,case):
        # case_id  title  method  url  data  expected  result  chk_sql interface
        row =case['case_id']+1
        method= case['method']
        url = self.base_url+case['url']
        data = case['data']
        data=eval(self.replacedata.replacedata(data))
        expected=eval(case['expected'])
        chk_sql=case['chk_sql']
        if chk_sql :
            sql_data_start=self.connet.select_data(sql=self.sql)
            leave_amount_start=sql_data_start['leave_amount']
        res_info=self.send.sendrequest(method=method,url=url,headers=self.headers,json=data)
        res_info=res_info.json()
        if case['interface'] == 'login':
            print(res_info)
            ReplaceData.member_id=jsonpath.jsonpath(res_info,'$..id')[0]
            token = jsonpath.jsonpath(res_info,'$..token')[0]
            token_type = jsonpath.jsonpath(res_info,'$..token_type')[0]
            self.headers['Authorization']='{} {}'.format(token_type,token)
        try :
            print('实际结果:{}'.format(res_info))
            print('期望结果:{}'.format(expected))
            if chk_sql :
                sql_data_end=self.connet.select_data(sql=self.sql)
                leave_amount_end=sql_data_end['leave_amount']
                #self.assertEqual(Decimal(str(data['amount'])),(leave_amount_start-leave_amount_end))
            self.assertEqual(expected['code'],res_info['code'])
            self.assertEqual(expected['msg'],res_info['msg'])
            self.readexcel.write_excel(row=row,column=8,value='pass')
            log.info('{}用例测试通过'.format(case['title']))
        except AssertionError as e :
            self.readexcel.write_excel(row=row,column=8,value='fail')
            log.error('{}用例测试不通过'.format(case['title']))
            log.exception(e)
            raise  e
if __name__ =='__main__':
    unittest.main()
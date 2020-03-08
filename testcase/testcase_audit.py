'''
 AUTH:RODDY
 DATE:2020/2/29
 TIME:21:55
 FILE:testcase_audit.py
 '''
import unittest
import os
import jsonpath
from common.readexcel import ReadExcel
from libray.ddt import ddt,data
from common.config import conf
from common.dirpath import DATAPATH
from common.handlrequst import SendRequest
from common.handlereplace import ReplaceData
from common.handlelog import log

@ddt
class TestCaseAudit(unittest.TestCase):
    readexcel=ReadExcel(filename=os.path.join(DATAPATH,conf.get('workbook','name')),
                        sheetname=conf.get('workbook','sheet06'))
    cases=readexcel.read_excel()
    replacedata = ReplaceData()
    send =SendRequest()
    headers_admin = eval(conf.get('env','headers'))
    def setUp(self):
        '''每次执行用例前新增项目'''
        #普通用户登录
        login_api = 'http://api.lemonban.com/futureloan/member/login'
        headers=eval(conf.get('env','headers'))
        login_data ={'mobile_phone':conf.getint('soso','phone'), 'pwd':conf.get('soso','pwd')
        }
        login_res=self.send.sendrequest(method='post',url=login_api,headers=headers,json=login_data)
        login_resp=login_res.json()
        token = jsonpath.jsonpath(login_resp,'$..token')[0]
        token_type = jsonpath.jsonpath(login_resp,'$..token_type')[0]
        headers['Authorization']='{} {}'.format(token_type,token)
        member_id=jsonpath.jsonpath(login_resp,'$..id')[0]
        #普通用户添加项目
        add_api = 'http://api.lemonban.com/futureloan/loan/add'
        add_data ={"member_id":member_id,"title":"添加001","amount":6300.00,"loan_rate":"12.0","loan_term":12,"loan_date_type":1,"bidding_days":1}
        add_res=self.send.sendrequest(method='post',url=add_api,headers=headers,json=add_data)
        add_resp=add_res.json()
        ReplaceData.loan_id=jsonpath.jsonpath(add_resp,'$..id')[0]
    def tearDown(self):
        '''清除类变量'''
        del ReplaceData.loan_id

    @data(*cases)
    def testcase_audit(self,case):
        # case_id  title  method  url  data  expected  result  chk_sql interface
        #注意请求头每次执行用例后,会被重新赋值所以需要在登录后将请求头保存在另外的类变量
        #各用例模块取名最好单独化,特别是在类变量,避免相互影响
        send_audit =SendRequest()
        title =case['title']
        row=case['case_id']
        method=case['method']
        url=conf.get('env','url')+case['url']
        chk_sql =case['chk_sql']
        data = case['data']
        data=eval(self.replacedata.replacedata(data))
        expected=eval(case['expected'])
        chk_sql=case['chk_sql']
        if chk_sql :
            sql_data_start=self.connet.select_data(sql=self.sql)
            leave_amount_start=sql_data_start['leave_amount']
        res_info=send_audit.sendrequest(method=method,url=url,headers=self.headers_admin,json=data)
        res_info=res_info.json()
        if case['interface'] == 'login':
            print('审核账号登录:',res_info)
            ReplaceData.member_id=jsonpath.jsonpath(res_info,'$..id')[0]
            token = jsonpath.jsonpath(res_info,'$..token')[0]
            token_type = jsonpath.jsonpath(res_info,'$..token_type')[0]
            self.headers_admin['Authorization']='{} {}'.format(token_type,token)
        #审核状态不在待审核状态的ID,重新审核一次
        if case['case_id']==4:
             print('第二次审核开始')
             print('审核数据:',data)
             res_info=send_audit.sendrequest(method=method,url=url,headers=self.headers_admin,json=data)
             res_info=res_info.json()
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

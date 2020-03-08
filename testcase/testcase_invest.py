'''
 AUTH:RODDY
 DATE:2020/3/1
 TIME:14:49
 FILE:testcase_invest.py
 '''
import  unittest
import jsonpath
import os
from libray.ddt import ddt,data
from common.readexcel import ReadExcel
from common.config import conf
from common.handlrequst import SendRequest
from common.handlereplace import ReplaceData
from common.handlelog import log
from common.dirpath import DATAPATH
@ddt
class TestCaseInvest(unittest.TestCase):
    readexcel=ReadExcel(filename=os.path.join(DATAPATH,conf.get('workbook','name')),
                                              sheetname=conf.get('workbook','sheet07'))
    cases=readexcel.read_excel()
    send=SendRequest()
    replacedata = ReplaceData()
    headers_admin = eval(conf.get('env','headers'))
    @classmethod
    def setUpClass(cls):
        #登录并创建项目
        #普通用户登录
        login_api = 'http://api.lemonban.com/futureloan/member/login'
        headers=eval(conf.get('env','headers'))
        login_data ={'mobile_phone':conf.getint('soso','phone'), 'pwd':conf.get('soso','pwd')}
        login_res=cls.send.sendrequest(method='post',url=login_api,headers=headers,json=login_data)
        login_resp=login_res.json()
        token = jsonpath.jsonpath(login_resp,'$..token')[0]
        token_type = jsonpath.jsonpath(login_resp,'$..token_type')[0]
        headers['Authorization']='{} {}'.format(token_type,token)
        member_id=jsonpath.jsonpath(login_resp,'$..id')[0]
        #普通用户添加项目
        add_api = 'http://api.lemonban.com/futureloan/loan/add'
        add_data ={"member_id":member_id,"title":"添加001","amount":6300.00,"loan_rate":"12.0","loan_term":12,"loan_date_type":1,"bidding_days":1}
        add_res=cls.send.sendrequest(method='post',url=add_api,headers=headers,json=add_data)
        add_resp=add_res.json()
        ReplaceData.loan_id=jsonpath.jsonpath(add_resp,'$..id')[0]
    @classmethod
    def tearDownClass(cls):
        '''清除类变量'''
        del ReplaceData.loan_id

    @data(*cases)
    def test_invest(self,case):
        #登录
        title =case['title']
        row=case['case_id']
        method=case['method']
        url=conf.get('env','url')+case['url']
        chk_sql =case['chk_sql']
        data = case['data']
        data=eval(self.replacedata.replacedata(data))
        expected=eval(case['expected'])
        #chk_sql=case['chk_sql']
        if  case['case_id'] ==2 :
            send_audit =SendRequest()
            print('不审批,进行投资')
            print(title,url,data)
            res_info=send_audit.sendrequest(method=method,url=url,headers=self.headers_admin,json=data)
            res_info=res_info.json()
        elif case['case_id'] == 3:
            send_audit =SendRequest()
            print('审批:投资------先审批,再投资')
            audit_data='{"loan_id":#loan_id#,"approved_or_not":"true"}'
            audit_url='http://api.lemonban.com/futureloan//loan/audit'
            audit_data=eval(self.replacedata.replacedata(audit_data))
            res_audit=send_audit.sendrequest(method='PATCH',url=audit_url,headers=self.headers_admin,json=audit_data)
            print('审批数据:',audit_data)
            print('审批结果:',res_audit.json())
            print(title,url,data)
            res_info=send_audit.sendrequest(method=method,url=url,headers=self.headers_admin,json=data)
            res_info=res_info.json()
        else:
            send_audit =SendRequest()
            print('投资或登录------')
            print(title,url,data)
            res_info=send_audit.sendrequest(method=method,url=url,headers=self.headers_admin,json=data)
            res_info=res_info.json()
        if case['interface'] == 'login':
            print('审核账号登录:',res_info)
            ReplaceData.member_id=jsonpath.jsonpath(res_info,'$..id')[0]
            token = jsonpath.jsonpath(res_info,'$..token')[0]
            token_type = jsonpath.jsonpath(res_info,'$..token_type')[0]
            self.headers_admin['Authorization']='{} {}'.format(token_type,token)
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

if __name__ =='__main':
    unittest.main()

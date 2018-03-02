#/usr/bin/python
# coding=utf8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time
import sys,os
from django.core.wsgi import get_wsgi_application
sys.path.extend(['smcsystem',])
os.environ.setdefault("DJANGO_SETTINGS_MODULE","smcsystem.settings")
application = get_wsgi_application()
from smcsystem import settings

now=time.localtime()

nowtime=str(now[0])+'/'+str(now[1])+'/'+str(now[2])

#sender = 'jumpserver@bitnei.cn'
#receiver = 'sunyang@bitnei.cn'
#receiver = 'sunyang@transilink.com'
#smtpserver = 'smtp.exmail.qq.com'
#username = 'jumpserver@bitnei.cn'
#password = 'Lgxy@z9w5'

sender = settings.SENDER
receiver = settings.RECEIVER
smtpserver = settings.SMTPSERVER
username = settings.USERNAME
password = settings.PASSWORD

msg = MIMEMultipart('alternative')


def run(objs,surplus,message):
    msg['Subject'] = u"%s %s"%(nowtime,message)
    head_list = ['平台名称','故障开始时间','故障结束时间','提交人','故障级别','处理情况','处理信息']
    str_list = ['<tr style="background-color: #dedede;border-color: #666666;border-style: solid;border-width: 1px;">']
    str_list.append('<th scope="col" style="width:100px">%s</th>'%head_list[0])
    str_list.append('<th scope="col" style="width:120px">%s</th>'%head_list[1])
    str_list.append('<th scope="col" style="width:120px">%s</th>'%head_list[2])
    str_list.append('<th scope="col" style="width:80px">%s</th>'%head_list[3])
    str_list.append('<th scope="col" style="width:90px">%s</th>'%head_list[4])
    str_list.append('<th scope="col" style="width:90px">%s</th>'%head_list[5])
    str_list.append('<th scope="col" style="width:800px">%s</th>'%head_list[6])
    str_list.append('</tr>')

    for obj in surplus:
        str_list.append('<tr>')
        str_list.append('<th>%s</th>'%obj.xmname)
        str_list.append('<td>%s</td>'%obj.start_time)
        str_list.append('<td>%s</td>'%obj.end_time)
        str_list.append('<td>%s</td>'%obj.username)
        str_list.append('<td>%s</td>'%obj.get_level_display())
        str_list.append('<td style="background-color: yellow">%s</td>'%obj.get_end_display())
        str_list.append('<td>%s</td>'%obj.text)                                                                                                      
        str_list.append('</tr>')  
    
    for obj in objs:
        str_list.append('<tr>')
        str_list.append('<th>%s</th>'%obj.xmname)
        str_list.append('<td>%s</td>'%obj.start_time)
        str_list.append('<td>%s</td>'%obj.end_time)
        str_list.append('<td>%s</td>'%obj.username)
        if obj.get_level_display() == '一级故障':
            str_list.append('<td style="background-color: red">%s</td>'%obj.get_level_display()) 
        else:
            str_list.append('<td>%s</td>'%obj.get_level_display())
        str_list.append('<td>%s</td>'%obj.get_end_display())
        str_list.append('<td>%s</td>'%obj.text)
        str_list.append('</tr>')
    if not objs and not surplus:
        str_list.append('<tr>')                                                                                                                      
        str_list.append('<th>无故障</th>')                                                                                                    
        str_list.append('<td>无故障</td>')                                                                                                
        str_list.append('<td>无故障</td>')                                                                                                  
        str_list.append('<td>无故障</td>')                                                                                                  
        str_list.append('<td>无故障</td>')                                                                                       
        str_list.append('<td>无故障</td>')                                                        
        str_list.append('<td>无故障</td>')                                                                                                      
        str_list.append('</tr>')
    print(str_list)
    html = """ 
    <html lang="zh"> 
    <head>
    <style>
    body {
            font: normal 11px auto "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
            color: #4f6b72;
            background: #E6EAE9;
    }
    
    a {
            color: #c75f3e;
    }
    
    #mytable {
            padding: 0;
            margin: 0;
    }
    
    caption {
            padding: 0 0 5px 0;
            width: 700px;
            font: italic 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
            text-align: right;
    }
    
    th {
            font: bold 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
            color: #4f6b72;
            border-right: 1px solid #C1DAD7;
            border-bottom: 1px solid #C1DAD7;
            border-top: 1px solid #C1DAD7;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-align: left;
            padding: 6px 6px 6px 12px;
            background: #CAE8EA url(images/bg_header.jpg) no-repeat;
    }
    
    th.nobg {
            border-top: 0;
            border-left: 0;
            border-right: 1px solid #C1DAD7;
            background: none;
    }
    
    td {
            border-right: 1px solid #C1DAD7;
            border-bottom: 1px solid #C1DAD7;
            background: #fff;
            padding: 6px 6px 6px 12px;
            color: #4f6b72;
    }
    
    
    td.alt {
            background: #F5FAFA;
            color: #797268;
    }
    
    th.spec {
            border-left: 1px solid #C1DAD7;
            border-top: 0;
            background: #fff url(images/bullet1.gif) no-repeat;
            font: bold 10px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
    }
    
    th.specalt {
            border-left: 1px solid #C1DAD7;
            border-top: 0;
            background: #f5fafa url(images/bullet2.gif) no-repeat;
            font: bold 10px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
            color: #797268;
    }
        </style>
    </head> 
    <body> 
    <div>
    <h1 align="center" style="font-size:36px;">%s</h1> 
    </div>
    <table id="mytable" border="1" cellspacing="0" summary="The technical specifications of the Apple PowerMac G5 series"> 
    %s 
    </table> 
    </body> 
    </html> 
    """%(nowtime,'\n'.join(str_list))

    try:
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
        smtp = smtplib.SMTP()
        smtp.connect('smtp.exmail.qq.com',25)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
        return True
    except:
        return False


from django.shortcuts import render, HttpResponse,redirect
import json
from filing import auth
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from filing import models
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe
from django.db.models import Q
import time

# 登陆装饰器
def login_auth(func):
    def inner(request, *args, **kwargs):
        obj = models.UserInfo.objects.filter(user=request.session.get('user'),token_session=request.session.get('token')).first()
        if obj:
            print(obj.token_session)
            token = obj.token_session
        else:
            token = "99999"
        status = request.session.exists(token)
        if not status:
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return inner

@login_auth
def index(request):
    wl_host_num = models.Host.objects.filter(type=1).count()
    vm_host_num = models.Host.objects.filter(type=2).count()
    code_host_num = models.Code.objects.all().count()
    group_host_num = models.Group.objects.all().count()
    up_d = models.Host.objects.filter(status=1).count()
    down_d = models.Host.objects.filter(status=2).count()
    sw_d = models.Host.objects.filter(type__in=[3,4,5]).count()
    vm_d = models.Host.objects.filter(type=6).count()
    wl_host_num = wl_host_num + vm_d
    return render(request, 'index.html',{'wl_host_num':wl_host_num,'vm_host_num':vm_host_num,'code_host_num':code_host_num,
                                         'group_host_num':group_host_num,"up_d":up_d,"down_d":down_d,'sw_d':sw_d,'vm_d':vm_d})


class Host_api(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Host_api, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @auth.apiauth
    def get(self, request):
        # 发送在线的主机
        salt_id = models.Host.objects.filter(salt_id__isnull=False,status=1, type__in=[1, 2]).values('salt_id')
        print(salt_id)
        return HttpResponse(json.dumps(list(salt_id)))

    @auth.apiauth
    def put(self, request):
        '''用来更新数据库'''
        json_data = request.GET.get('data')
        messages = ""
        # salt抓取过来的数据
        result = self.data_handle(json.loads(json_data))
        self.data_handle_last(json.loads(json_data))
        host_ip = json.loads(json_data).split("|")[0]
        result["status"] = 1
        # 数据库里的host数据
        source_host_dic = models.Host.objects.filter(ip=host_ip).values()[0]
        cn_dic = {'system': '系统版本', 'brand': '品牌', 'mem_use': '内存已用', 'ip': 'ip地址', 'disk_use': '磁盘已用',
                  'kernel': '系统内核', 'cpu_model': 'cpu型号', 'disk_capacity': '磁盘总量', 'mem': '内存大小', 'type': '主机性质',
                  'cpu_num': 'cpu数', 'sn': 'sn号', 'status': '状态', 'id': 'ID', 'hostname': '主机名', 'disk_num': '磁盘个数',
                  'salt_id':"salt配置id","all_ip":"所有ip"}
        print(cn_dic, "---------------------------sss")
        # 判断salt取过来的数值和数据库里的是否有不同
        for k, v in result.items():
            if k in source_host_dic:
                if k not in ["disk_use", "mem_use"] and source_host_dic[k] != str(v):
                    messages += u" - %s: %s 更新为 %s!" % (cn_dic[k], source_host_dic[k], v)
        if messages:
            models.Log.objects.create(host_ip_id=source_host_dic["id"], level="warning", message=u"更新%s" % messages)
        else:
            models.Log.objects.create(host_ip_id=source_host_dic["id"], level="info", message=u"连接成功,没有更新项!")
        models.Host.objects.filter(ip=host_ip).update(**result)
        return HttpResponse(json.dumps({'data': 'ok put'}))

    @auth.apiauth
    def post(self, request):
        '''用来添加数据'''
        print('----------post----', request.POST.get('data'))
        json_data = request.POST.get('data')

        result = self.data_handle(json.loads(json_data))
        self.data_handle_last(json.loads(json_data))
        host_ip = json.loads(json_data).split("|")[0]
        print(result)
        result["ip"] = host_ip
        result["status"] = 1
        obj = models.Host.objects.filter(ip=host_ip)
        if obj:
            # 这里是已经 设置为下线的 物理机和虚拟机
            print(host_ip, '-----------------------------------------11111')
            obj.update(salt_id=result["salt_id"],status="1")
            return HttpResponse(json.dumps({'data': 'error ip exist!'}))

        models.Host.objects.create(**result)
        source_host_dic = models.Host.objects.filter(ip=host_ip).values("id")[0]
        models.Log.objects.create(host_ip_id=source_host_dic["id"], level="info", message=u"添加成功")
        return HttpResponse(json.dumps({'data': 'ok post'}))

    @auth.apiauth
    def delete(self, request):
        '''用设置salt 报警和，不在salt里面的服务器 下线操作'''
        print("----------------delete", request.GET)
        data = request.GET.get('data')
        err = request.GET.get('err')
        # 设置下线
        if data:
            salt_id = json.loads(data)
            models.Host.objects.filter(salt_id=salt_id).update(status="2")
            host_id = models.Host.objects.filter(salt_id=salt_id).values("id")[0]['id']
            models.Log.objects.create(host_ip_id=host_id, level="warning", message=u"设置为下线状态")
            return HttpResponse(json.dumps({'data': 'ok delete'}))
        # salt链接失败
        if err:
            err_ip = json.loads(err)
            host_id = models.Host.objects.filter(salt_id=err_ip).values("id")
            if host_id:
                models.Log.objects.create(host_ip_id=host_id[0]['id'], level="error", message=u"salt 连接失败,导致更新失败.")
            return HttpResponse(json.dumps({'data': 'ok err'}))
        return HttpResponse(json.dumps({'data': 'no data'}))

    def data_handle(self, data):
        self.data_list = data.split("|")
        data_dic = {"hostname": self.data_list[1], "cpu_num": self.data_list[2], "cpu_model": self.data_list[3],
                    "disk_num": self.data_list[4],
                    "disk_capacity": self.data_list[5], "disk_use": self.data_list[6], "mem": self.data_list[7],
                    "mem_use": self.data_list[8],
                    "brand": self.data_list[9], "type": self.data_list[10], "sn": self.data_list[11],
                    "system": self.data_list[12], "kernel": self.data_list[13],"salt_id":self.data_list[14],
                    "all_ip":self.data_list[15].strip("\n")}
        return data_dic

    def data_handle_last(self, data):
        self.data_list = data.split("|")
        data_dic = {"salt_id":self.data_list[14],"ip_info":self.data_list[16].strip("\n").replace("ttwrap","\n")}
        print(data_dic)
        obj = models.Host_net.objects.filter(salt_id=data_dic["salt_id"])
        if obj:
            obj.update(**data_dic)
        else:
            obj.create(**data_dic)




@login_auth
def serverlog(request):
    '''用来展示所有的日志信息'''
    objs = models.Log.objects.order_by('-id')

    page = request.GET.get('page')  # 获取page数
    q = request.GET.get("q")
    print(q)
    if q:
        q1 = Q()
        q1.connector = "OR"
        q1.children.append(("host_ip__ip__icontains", q))
        q1.children.append(("message__icontains", q))
        objs = objs.filter(q1).values("host_ip__ip", "time", "level", "message")
    else:
        q = ""
        objs = objs.values("host_ip__ip", "time", "level", "message")
    print(page, "page---------------")
    paginator = Paginator(objs, 15)  # 每页显示2个 并且把数据传入进来
    try:
        contacts = paginator.page(page)  # 判断有没有page数值
        current_page = int(page)  # 并且设置当前页的数
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)  # 如果没有设置page就返回第一页
        current_page = 1
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)  # 如果超过最大页 就返回最大页
        current_page = paginator.num_pages
    begin = 0
    end_num = 0
    all_page = paginator.num_pages  # 总数

    # 配置显示翻页的数量
    page_dispaly_num = 11
    odd_num, s_num = divmod(page_dispaly_num, 2)
    if s_num == 0:
        left_num = odd_num
        right_num = odd_num
    else:
        left_num = odd_num + 1
        right_num = odd_num
    if all_page >= 1 + page_dispaly_num:
        all_num = all_page - right_num
        if current_page > all_num:
            begin = all_num - left_num
            end_num = all_num + right_num
        elif current_page <= right_num:
            begin = 0
            end_num = page_dispaly_num
        else:
            begin = current_page - left_num
            end_num = current_page + right_num
    else:  # 没大于11页的时候就显示
        begin = 0
        end_num = all_page

    list_page = []
    #    begin_page = "<a href='?page=1'>首页<a>"
    #    list_page.append(begin_page)
    if current_page == 1:
        prev = '<li class ="disabled"><a href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
    else:
        prev = '<li><a href="?page=%s&q=%s" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>' % (
            current_page - 1, q)
    list_page.append(prev)
    for i in range(begin + 1, end_num + 1):
        if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
            temp = '<li class ="active"> <a href="?page=%s&q=%s"> %s <span class ="sr-only"></span ></a></li>' % (
            i, q, i)
        else:
            temp = '<li ><a href="?page=%s&q=%s"> %s <span class ="sr-only"></span ></a></li>' % (i, q, i)
        list_page.append(temp)

    if current_page == all_page:
        down = '<li class ="disabled"><a href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'
    else:
        down = '<li><a href="?page=%s&q=%s" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>' % (
            current_page + 1, q)
    list_page.append(down)
    #    end_page = "<a href='?page=%s'>末页<a>" % all_page
    #    list_page.append(end_page)
    temp = ''.join(list_page)
    return render(request, "serverlog.html", {"objs": objs, 'contacts': contacts, 'str_page': mark_safe(temp)})

@login_auth
def server_error_log(request):
    '''用来展示错误日志信息'''
    objs = models.Log.objects.filter(level__in=["error", "warning"]).order_by('-id')

    page = request.GET.get('page')  # 获取page数
    q = request.GET.get("q")
    print(q)
    if q:
        q1 = Q()
        q1.connector = "OR"
        q1.children.append(("host_ip__ip__icontains", q))
        q1.children.append(("message__icontains", q))
        objs = objs.filter(q1).values("host_ip__ip", "time", "level", "message")
    else:
        q = ""
        objs = objs.values("host_ip__ip", "time", "level", "message")
    paginator = Paginator(objs, 15)  # 每页显示2个 并且把数据传入进来
    print(page, "page---------------")
    try:
        contacts = paginator.page(page)  # 判断有没有page数值
        current_page = int(page)  # 并且设置当前页的数
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)  # 如果没有设置page就返回第一页
        current_page = 1
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)  # 如果超过最大页 就返回最大页
        current_page = paginator.num_pages
    begin = 0
    end_num = 0
    all_page = paginator.num_pages  # 总数

    # 配置显示翻页的数量
    page_dispaly_num = 11
    odd_num, s_num = divmod(page_dispaly_num, 2)
    if s_num == 0:
        left_num = odd_num
        right_num = odd_num
    else:
        left_num = odd_num + 1
        right_num = odd_num
    if all_page >= 1 + page_dispaly_num:
        all_num = all_page - right_num
        if current_page > all_num:
            begin = all_num - left_num
            end_num = all_num + right_num
        elif current_page <= right_num:
            begin = 0
            end_num = page_dispaly_num
        else:
            begin = current_page - left_num
            end_num = current_page + right_num
    else:  # 没大于11页的时候就显示
        begin = 0
        end_num = all_page

    list_page = []
    #    begin_page = "<a href='?page=1'>首页<a>"
    #    list_page.append(begin_page)
    if current_page == 1:
        prev = '<li class ="disabled"><a href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
    else:
        prev = '<li><a href="?page=%s&q=%s" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>' % (
            current_page - 1, q)
    list_page.append(prev)
    for i in range(begin + 1, end_num + 1):
        if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
            temp = '<li class ="active"> <a href="?page=%s&q=%s"> %s <span class ="sr-only"></span ></a></li>' % (
            i, q, i)
        else:
            temp = '<li ><a href="?page=%s&q=%s"> %s <span class ="sr-only"></span ></a></li>' % (i, q, i)
        list_page.append(temp)

    if current_page == all_page:
        down = '<li class ="disabled"><a href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'
    else:
        down = '<li><a href="?page=%s&q=%s" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>' % (
            current_page + 1, q)
    list_page.append(down)
    #    end_page = "<a href='?page=%s'>末页<a>" % all_page
    #    list_page.append(end_page)
    temp = ''.join(list_page)
    return render(request, "server_error_log.html", {"objs": objs, 'contacts': contacts, 'str_page': mark_safe(temp)})




def get_cn_name(admin_class, field_list):
    '''获取字段的中文名称'''
    cn_name_dic = {}
    for field_name in field_list:
        obj = getattr(admin_class, field_name)
        if hasattr(obj, "field"):
            name = obj.field.verbose_name
            cn_name_dic[field_name] = name
        else:
            for field_obj in admin_class._meta.fields:
                if hasattr(field_obj, 'verbose_name'):
                    cn_name_dic[field_obj.name] = field_obj.verbose_name
    return cn_name_dic


def disk_chart(request):
    data = {
        "xm_name":[],
        "disk_all":[],
        "disk_use":[]
    }

    # 从这里开始 是 三期平台的 特殊试图
    ajax_data = request.GET.get("data")
    if ajax_data == "sanqi":
        data = {
            "xm_name": [],
            "all": [],
            "use": []
        }
        disk_all = 0
        disk_use = 0
        group_id = models.Group.objects.filter(name="监管平台三期").values("id", "name")
        b1 = models.Group.objects.get(id=group_id[0]['id'])
        disk_list_data = b1.host_set.filter(status=1, type__in=[1, 2]).values("disk_use", "disk_capacity")
        for obj in disk_list_data:
            if obj["disk_capacity"] != None and obj["disk_use"] != None:
                print(obj["disk_use"],obj)
                disk_all += float(obj["disk_capacity"].strip("g"))
                disk_use += float(obj["disk_use"].strip("g"))
        data["all"].append(round(disk_all, 2))
        data["use"].append(round(disk_use, 2))
        return HttpResponse(json.dumps(data))
    # 从这里开始 是 三期平台的 特殊试图    结束！ 如果不需要了 可以删除

    group_id = models.Group.objects.all().values("id","name")
    for id in group_id:
        disk_all = 0
        disk_use = 0
        data["xm_name"].append(id["name"])
        if id['name'] == "监管平台三期":
            continue
        b1 = models.Group.objects.get(id=id['id'])
        disk_list_data = b1.host_set.filter(status=1,type__in=[1,2]).values("disk_use","disk_capacity")
        for obj in disk_list_data:
            if obj["disk_capacity"] != None and obj["disk_use"] != None:
                disk_all += float(obj["disk_capacity"].strip("g"))
                disk_use += float(obj["disk_use"].strip("g"))
        data["disk_all"].append(round(disk_all,2))
        data["disk_use"].append(round(disk_use,2))

    # data = {"list":[1,2,3,4,5,6,7,8]}
    return HttpResponse(json.dumps(data))



def mem_chart(request):
    data = {
        "xm_name" : [],
        "mem_all" : [],
        "mem_use" : []
    }

    # 三期内存使用情况
    ajax_data = request.GET.get("data")
    if ajax_data == "sanqi":
        data = {
            "xm_name": [],
            "all": [],
            "use": []
        }
        disk_all = 0
        disk_use = 0
        group_id = models.Group.objects.filter(name="监管平台三期").values("id", "name")
        b1 = models.Group.objects.get(id=group_id[0]['id'])
        disk_list_data = b1.host_set.filter(status=1, type__in=[1, 2]).values("mem", "mem_use")
        for obj in disk_list_data:
            if obj["mem"] != None and obj["mem_use"] != None:
                disk_all += float(obj["mem"].strip("g"))
                disk_use += float(obj["mem_use"].strip("g"))
        data["all"].append(round(disk_all,2))
        data["use"].append(round(disk_use,2))
        print(data)
        return HttpResponse(json.dumps(data))
    # 三期内存使用情况  结束 不用的时候可以删除

    group_id = models.Group.objects.all().values("id","name")
    for id in group_id:
        disk_all = 0
        disk_use = 0
        data["xm_name"].append(id["name"])
        if id['name'] == "监管平台三期":
            continue
        b1 = models.Group.objects.get(id=id['id'])
        disk_list_data = b1.host_set.filter(status=1,type__in=[1,2]).values("mem","mem_use")
        for obj in disk_list_data:
            if obj["mem"] != None and obj["mem_use"] != None:
                disk_all += float(obj["mem"].strip("g"))
                disk_use += float(obj["mem_use"].strip("g"))
        data["mem_all"].append(round(disk_all,2))
        data["mem_use"].append(round(disk_use,2))

    # data = {"list":[1,2,3,4,5,6,7,8]}
    return HttpResponse(json.dumps(data))


def car_num_chart(request):
    # [['volvo', '0'], ['北汽常州', '4'], ['丹东黄海', '0'], ['河北廊坊', '0']] result的数据格式
    from filing import zabbix_api
    zabbix_obj = zabbix_api.Item_update('car_num')
    result = zabbix_obj.get_group_name()
    data = {"data_list":result}
    return HttpResponse(json.dumps(data))

def app_chart(request):
    data = {
        "group_list":[],
        "host_list":[],
        "app_list":[]
    }
    group_obj = models.Group.objects.all()
    for obj in group_obj:
        data["host_list"].append(obj.host_set.all().count())
        data["app_list"].append(obj.to_code.all().count())
        data["group_list"].append(obj.name)
    print(data)
    return HttpResponse(json.dumps(data))

def cq_chart(request):
    data = {
        "group_list":[],
        "host_list": []
    }
    group_obj = models.CQ_Group.objects.all()
    for obj in group_obj:
        data["host_list"].append(obj.cq_host_set.all().count())
        data["group_list"].append(obj.name)
    print(data)
    return HttpResponse(json.dumps(data))


def group_history(request):
    info = []
    print("okok")
    group_list = models.Group.objects.values("id","name")
    for group in group_list:
        history_obj = models.Group_disk_history.objects.filter(group_id=group["id"]).values('date', 'disk_num').order_by('id')
        data_list = []
        for history in history_obj:
            date = int(time.mktime(history["date"].timetuple())) * 1000
            data_list.append([date,history["disk_num"]])
        message = {
                             "name": group["name"],
                             "data": data_list
                         }
        info.append(message)
    print(info)
    return HttpResponse(json.dumps({"info":info}))



@csrf_exempt
@login_auth
def command_operation(request):
    """使用salt来执行平台里的命令"""
    if request.session.get('admin',False) != "admin":
        return redirect('/')
    all_ip_list = []
    status = True
    new_data = ''
    salt_id = models.Host.objects.filter(salt_id__isnull=False, status=1, type__in=[1, 2]).values("salt_id")
    if request.method == "POST":
        all_ip = request.POST.get("all")
        command = request.POST.get("command")
        # 判断是不是执行所有主机
        if all_ip == "true":
            for ip in salt_id:
                all_ip_list.append(ip["salt_id"])
        else:
            ip_list = request.POST.get("ip_list")
            all_ip_list = json.loads(ip_list)
        from filing.salt_cmd import Go_ssh
        try:
            # 链接远程的 salt 来做操作
            p_obj = Go_ssh()
            from smcsystem import settings
            result = p_obj.run("python2.6 %s '%s' '%s'"%(settings.SALT_API_SCRIPT_PATH,','.join(all_ip_list),command))
            print(str(result,encoding="utf-8"))
            new_data = json.loads(str(result,encoding="utf-8"))
            print(new_data,"aaaaaaaaaaaaaaa")
            p_obj.ssh_close()
        except:
            status = False
        print(command)
        print(all_ip)
        return HttpResponse(json.dumps({"status":status,"message":new_data}))
    return render(request,"command.html",{"ip_dio":salt_id})



def login(request):
    error_log = ""                                                                                                                                   
    if request.method == "POST":                                                                                                                     
        username = request.POST.get("username")                                                                                                      
        password = request.POST.get("password")                                                                                                      
        print(username,password)                                                                                                                     
        if username and password:                                                                                                                    
            user_obj = models.UserInfo.objects.filter(user=username,passwd=password)                                                                 
            if user_obj:                                                                                                                             
                role = user_obj[0].get_admin_display()                                                                                               
                request.session['admin'] = role                                                                                                      
                request.session['user'] = user_obj[0].user                                                                                           
                user_obj.update(token_session=request.session.session_key)                                                                           
                request.session['token'] = request.session.session_key                                                                               
                return redirect('/')                                                                                                                 
                                                                                                                                                     
            else:                                                                                                                                    
                error_log = "用户名或密码错误!"                                                                                                      
        else:                                                                                                                                        
            error_log = "用户名或密码错误!"                                                                                                          
    request.session['token'] = '9999'
    return render(request,"login.html",{'error':error_log})  



@login_auth
def logout(request):                                                                                                                                 
    token = models.UserInfo.objects.filter(user=request.session["user"]).first()                                                                     
    #del request.session["admin"]                                                                                                                    
    #del request.session["user"]                                                                                                                     
    if token:                                                                                                                                        
        models.UserInfo.objects.filter(user=request.session["user"]).update(token_session="1")                                                       
    request.session.delete(token.token_session)                                                                                                      
    return redirect('/login/')                                                                                                                       



@csrf_exempt
@login_auth
def init_data(request):
    status = True
    host_dic = {}
    group_list = []
    if request.method == "POST":
        import os
        file_path = os.path.join(os.getcwd(),"file.xlsx")
        if os.path.exists(os.path.join(file_path)):
            import xlrd
            bk = xlrd.open_workbook(file_path)
            sh = bk.sheet_by_name("Sheet1")
            nrows = sh.nrows
            for i in range(1, nrows):
                row_data = sh.row_values(i)
                if row_data[0] != "":
                    if row_data[0] not in host_dic:
                        host_dic[row_data[0]] = []
                    host_dic[row_data[0]].append(row_data[1:])
                    group_list.append(row_data[-1])
            # 添加项目
            for group in list(set(group_list)):
                obj = models.Group.objects.filter(name=group)
                if obj:
                    print(group, "已存在")
                else:
                    models.Group.objects.create(name=group)
            # 添加主机信息
            for ip,app_info_list in host_dic.items():
                for app in app_info_list:
                    obj = models.Host.objects.filter(ip=ip)

                    if obj:
                        pass
                    else:
                        print(ip,"主机不存在")
                        if app[7]:
                            models.Host.objects.create(ip=ip,c_room=str(int(app[7])))
                        else:
                            models.Host.objects.create(ip=ip)
                    g_host = models.Host.objects.get(ip=ip)
                    # g_id = models.Group.objects.filter(name=app[-1]).values('id')[0]['id']
                    obj = models.Group.objects.filter(name=app[-1]).values('id')

                    g1 = models.Group.objects.get(id=obj[0]['id'])
                    if not app[4]:
                        code_obj = models.Code.objects.create(name=app[0], path=app[1], log=app[2], start=app[3],
                                                              mapping=app[5],
                                                              www=app[6])
                        c_id = code_obj.id

                    else:
                        code_obj = models.Code.objects.create(name=app[0],path=app[1],log=app[2],start=app[3],port=str(int(app[4])),mapping=app[5],
                                                          www=app[6])
                        c_id = code_obj.id
                    g1.to_code.add(code_obj.id)
                    g_host.to_code.add(c_id)
                    g_host.to_group.add(obj[0]['id'])
                # ip_obj = models.Host.objects.filter(ip=ip)
                # if ip_obj:
                #     for i in app_info_list:
                #         print(i)
                #         g1 = models.Host.objects.get(ip=ip)
                #         g_id = models.Group.objects.filter(name=i[-1]).values('id')[0]['id']
                #         c_id = models.Code.objects.filter(name=i[0],path=i[1]).values('id')[0]['id']
                #         g1.to_code.add(c_id)
                #         g1.to_group.add(g_id)
                #
                # else:
                #     print(ip,"不存在")
                #     models.Host.objects.create(ip=ip)
                #     for i in app_info_list:
                #         g1 = models.Host.objects.get(ip=ip)
                #         g_id = models.Group.objects.filter(name=i[-1]).values('id')[0]['id']
                #         c_id = models.Code.objects.filter(name=i[0],path=i[1]).values('id')[0]['id']
                #         g1.to_code.add(c_id)
                #         g1.to_group.add(g_id)

            message = '导入成功!'
        else:
            message = '文件不存在'
            status = False
        return HttpResponse(json.dumps({'status':status,'message':message}))
    return render(request,'test.html')


@login_auth
def log_cat(request,host_id,app_id):
    status = True
    salt_status = True
    print(host_id,app_id)
    try:
        host_id = int(host_id)
        app_id = int(app_id)
    except:
        status = False
        return render(request, 'app_log.html',{"status":status,'salt_status':salt_status})
    code_obj = models.Code.objects.filter(id=app_id).last()
    host_obj = models.Host.objects.filter(id=host_id).last()
    format_str = ''
    new_data = ''
    if code_obj and host_obj:
        app_name = code_obj.name
        app_log_path = code_obj.log
        host_ip = host_obj.ip
        if app_name != '' and app_log_path != '' and host_ip != '':
            format_str = "主机: %s  日志路径: %s  程序名称: %s"%(host_ip, app_log_path, app_name)
            from filing.salt_cmd import Go_ssh
            try:
                # 链接远程的 salt 来做操作
                p_obj = Go_ssh()
                from smcsystem import settings
                result = p_obj.run(
                    "python2.6 %s '%s' 'tail -200 %s'" % (settings.SALT_API_SCRIPT_PATH, host_ip, app_log_path))
                new_data = json.loads(str(result, encoding="utf-8"))[host_ip]
                p_obj.ssh_close()
            except:
                salt_status = False
        else:
            status = False
    else:
        status = False
    return render(request,'app_log.html',{'format_str':format_str,"status":status,'salt_status':salt_status,'message':new_data})


# 初始化host主机信息
@csrf_exempt
@login_auth
def init_host(request):
    status = True
    if request.method == "POST":
        print("sssssssssssss")
        import os
        message = ''
        file_path = os.path.join(os.getcwd(), "host.xlsx")
        if os.path.exists(os.path.join(file_path)):
            import xlrd
            bk = xlrd.open_workbook(file_path)
            sh = bk.sheet_by_name("Sheet1")
            nrows = sh.nrows
            for i in range(1, nrows):
                row_data = sh.row_values(i)
                if row_data[0] != "":
                    obj = models.Host.objects.filter(ip=row_data[0])
                    if obj:
                        print(row_data[0]+"已存在")
                        message += row_data[0]+"存在 "
                    else:
                        models.Host.objects.create(ip=row_data[0],hostname=row_data[1],cpu_num=row_data[2] if row_data[2] == "" else int(row_data[2]),cpu_model=row_data[3],
                                                   disk_num=row_data[4] if row_data[4] == "" else int(row_data[4]),
                                                   disk_capacity=row_data[5] if row_data[5] == "" else int(row_data[5]),mem=row_data[6] if row_data[6] == "" else int(row_data[6]),brand=row_data[7],
                                                   type=row_data[8] if row_data[8] == "" else int(row_data[8]),sn=row_data[9],system=row_data[10],
                                                   status=row_data[11] if row_data[11] == "" else int(row_data[11]),
                                                   c_room=row_data[12] if row_data[12] == "" else int(row_data[12]),position=row_data[13])
                        print(row_data[0]+"创建成功")
                        message = "导入成功"
        else:
            status = False
            message = "请查看 host.xlsx文件是否存在"
        return HttpResponse(json.dumps({"status":status,"message":message}))


########################## 三方平台数据导入
@csrf_exempt
@login_auth
def init_cq_data(request):
    status = True
    host_dic = {}
    group_list = []
    if request.method == "POST":
        import os
        file_path = os.path.join(os.getcwd(),"file.xlsx")
        if os.path.exists(os.path.join(file_path)):
            import xlrd
            bk = xlrd.open_workbook(file_path)
            sh = bk.sheet_by_name("Sheet1")
            nrows = sh.nrows
            for i in range(1, nrows):
                row_data = sh.row_values(i)
                if row_data[0] != "":
                    if row_data[0] not in host_dic:
                        host_dic[row_data[0]] = []
                    host_dic[row_data[0]].append(row_data[1:])
                    group_list.append(row_data[-1])
            # 添加项目
            for group in list(set(group_list)):
                obj = models.CQ_Group.objects.filter(name=group)
                if obj:
                    print(group, "已存在")
                else:
                    models.CQ_Group.objects.create(name=group)
            # 添加主机信息
            for ip,app_info_list in host_dic.items():
                for app in app_info_list:
                    obj = models.CQ_Host.objects.filter(ip=ip)

                    if obj:
                        pass
                    else:
                        print(ip,"主机不存在")
                        models.CQ_Host.objects.create(ip=ip)
                    g_host = models.CQ_Host.objects.get(ip=ip)

                    obj = models.CQ_Group.objects.filter(name=app[-1]).values('id')

                    g1 = models.CQ_Group.objects.get(id=obj[0]['id'])
                    if not app[4]:
                        code_obj = models.CQ_Code.objects.create(name=app[0], path=app[1], log=app[2], start=app[3],
                                                              mapping=app[5],
                                                              www=app[6])
                        c_id = code_obj.id

                    else:
                        code_obj = models.CQ_Code.objects.create(name=app[0],path=app[1],log=app[2],start=app[3],port=str(int(app[4])),mapping=app[5],
                                                          www=app[6])
                        c_id = code_obj.id
                    g1.to_code.add(code_obj.id)
                    g_host.to_code.add(c_id)
                    g_host.to_group.add(obj[0]['id'])

            message = '导入成功!'
        else:
            message = '文件不存在'
            status = False
        return HttpResponse(json.dumps({'status':status,'message':message}))
    return render(request,'test.html')

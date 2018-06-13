from django.shortcuts import render,HttpResponse,redirect
from king_admin import king_admin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.db.models import Q
from king_admin.form import dynamic_class
from filing.models import Host_net
import re, os


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

# 权限装饰器 role == see是只读
def role_auth(func):
    def inner(request, *args, **kwargs):
        admin = request.session.get('admin', None)
        if request.method == "POST":
            print(admin)
            if admin == "see":
                print("see","-----------------------")
                return redirect(request.path)
        return func(request, *args, **kwargs)
    return inner


def index(request):
    request.session["url"] = {'/king_admin/admin_a/ip_host/':'ip表','/king_admin/admin_a/userinfo/':'用户表','/index/':'仪表盘'}
    return render(request, "king/king.html", {'table':king_admin.register_dic})


# 返回表格信息的视图
@login_auth
def table_obj(request,app_name, table_name):
    module_s = __import__('%s.models' % app_name)
    admin_class = king_admin.register_dic[app_name][table_name]
    if request.method == "POST":
        # 获取所有选中的表内的id
        select_ids = request.POST.get('selected_ids')
        #　获取执行的那个action
        action = request.POST.get('action')
        if select_ids:
            select_objs = admin_class.module.objects.filter(id__in=select_ids.split(','))
        else:
            raise KeyError("No object selectd.")
        if hasattr(admin_class,action):
            action_func = getattr(admin_class,action)
            request._admin_action = action
            return action_func(admin_class,request,select_objs)
    filter_conditions = {}
    filter_str = '?'
    for k,v in request.GET.items():
        if v and k in admin_class.list_filter:
            filter_conditions[k] = v
            filter_str += '%s=%s&'%(k,v)

    #  查看是否有ordering字段（默认排序字段） 如果有那么就调序排序 没有就默认id倒序
    data_list = admin_class.module.objects.filter(**filter_conditions).order_by("%s" % admin_class.ordering if admin_class.ordering else"-id")      # 过滤后的结果


    # 设置点击字段排序的配置
    table_sort = request.GET.get('o')
    if table_sort:
        data_list = data_list.order_by(table_sort)
        o = table_sort
    else:
        o = ''

    # 设置 search搜索的时候的
    search = request.GET.get('q')
    if search:
        q_str = search
        re_p = re.compile(r"\d+-\d+-\d+\|\d+-\d+-\d+")
        end = re.compile(r"(?<=\|)\d+-\d+-\d+$")
        start = re.compile(r"^\d+-\d+-\d+(?=\|)")
        result = re_p.search(search)
        if result:
            if "start_time" in admin_class.list_search:
                print("OKOKOKOKOKOKOKOKOKOK")
                s_time = start.search(search).group()
                end_time = end.search(search).group()
                print(s_time, end_time)
                q1 = Q()
                q1.connector = "AND"
                q1.children.append(("start_time" + "__gte", s_time))
                q1.children.append(("start_time" + "__lte", end_time))
                data_list = data_list.filter(q1)
        else:
            q1 = Q()
            q1.connector = "OR"
            for search_data in admin_class.list_search:
                print(search_data)
                if search_data == "all_ip":
                    q1.children.append((search_data + "__icontains", search+" "))
                else:
                    # 使用Q语句来制造 多条件的搜索，此处（icontains）是忽略大小写
                    q1.children.append((search_data + "__icontains", search))
            data_list = data_list.filter(q1)
            data_list = list(set(data_list))
            print(search, set(data_list))
    else:
        q_str = ''

#############	上面是获取数据，根据自己的需求获取数据 下面是分页的配置

    paginator = Paginator(data_list, admin_class.page_number)  			# 每页显示2个 并且把数据传入进来
    page = request.GET.get('page')				# 获取page数
    try:
        contacts = paginator.page(page)				# 判断有没有page数值
        current_page = int(page)				# 并且设置当前页的数
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)				# 如果没有设置page就返回第一页
        current_page = 1
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)		# 如果超过最大页 就返回最大页
        current_page = paginator.num_pages

    begin = 0
    end_num = 0
    all_page = paginator.num_pages
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
        prev = '<li><a href="%spage=%s&o=%s&q=%s" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'% (filter_str,current_page - 1,o,q_str)
    list_page.append(prev)
    for i in range(begin + 1, end_num + 1):
        active = ''
        if i == current_page:  			# 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
            active = 'active'

        temp = '<li class="%s"><a href="%spage=%s&o=%s&q=%s"> %s <span class ="sr-only"></span ></a></li>'% (active,filter_str,i,o,q_str,i)
        list_page.append(temp)

    if current_page == all_page:
        down = '<li class ="disabled"><a href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'
    else:
        down = '<li><a href="%spage=%s&o=%s&q=%s" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'% (filter_str,current_page + 1,o,q_str)
    list_page.append(down)
#    end_page = "<a href='?page=%s'>末页<a>" % all_page
#    list_page.append(end_page)
    temp = ''.join(list_page)

    # 配置字典，用于排序的判断，{字段:True or False} True 是正序 False是倒序，然后前端做判断
    if table_sort:
        if table_sort.startswith('-'):
            table_sort = {table_sort.strip('-'):False}
        else:
            table_sort = {table_sort: True}

    # 用来设置用户get请求的参数,保存用户上一次访问的查询参数
    get_str = request.META.get("QUERY_STRING","")
    if get_str:
        request.session["get_str"] = "?" + get_str
    else:
        request.session["get_str"] = ""

    return render(request, 'king/king_table.html', {'admin_class':admin_class, 'contacts': contacts, 'str_page':mark_safe(temp),
                                             'filter_conditions':filter_conditions,'table_sort':table_sort,'filter_str':filter_str,
                                                    'q_str':q_str})



# 修改表时的视图
@login_auth
@role_auth
def table_obj_change(request,app_name, table_name, first_field):
    one_list = []
    referer = request.session.get("get_str")
    admin_class = king_admin.register_dic[app_name][table_name]
    try:
        del admin_class.one
    except:
        pass
    ifconfig_info = False
    form_class = dynamic_class(request,admin_class)
    obj = admin_class.module.objects.get(id=first_field)
    print(obj.id,"==================")
    if hasattr(admin_class,'_status'):
        del admin_class._status
    if request.method == "POST":
        for i in admin_class.one_field:
            if obj.__dict__[i] != request.POST.get(i):
                result = admin_class.module.objects.filter(**{i:request.POST.get(i)})
                if result:
                    one_list.append(i)
        if one_list:
            admin_class.one = one_list
        form_obj = form_class(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            # referer 是get请求的uri 用来记录用户之前请求的页面
            return redirect(request.path.replace('/%s/change/'%first_field, '/')+referer)

    else:
        form_obj = form_class(instance=obj)
    if hasattr(obj,"salt_id"):
        salt_id = obj.salt_id
        h_net_obj = Host_net.objects.filter(salt_id=salt_id)
        if h_net_obj:
            ifconfig_info =h_net_obj[0].ip_info
    print(dir(obj))
    if hasattr(obj,"ip"):
        if os.path.exists("statics/imgcode/%s.jpg" % obj.ip):
            img_status = True
        else:
            img_status = False
        img_ip = obj.ip
    else:
        img_status = False
        img_ip = None

    return render(request,'king/king_table_change.html',{'form_obj':form_obj,'app_name':app_name,'table_name':table_name,
                                                         "admin_class":admin_class,"ifconfig_info":ifconfig_info,"get_uri":referer,
                                                         "ip":img_ip,"img_status":img_status})


# 添加时的视图
@login_auth
@role_auth
def table_obj_add(request,app_name,table_name):
    one_list = []
    admin_class = king_admin.register_dic[app_name][table_name]
    # _status 设置添加页面不做readonly的认证 最后要del 删除这个字段 才能正常使用
    admin_class._status = True
    try:
        del admin_class.one
    except:
        pass
    form_class = dynamic_class(request,admin_class)
    if request.method == "POST":
        form_obj = form_class(request.POST)
        for i in admin_class.one_field:
            print('----------------ee',i)
            obj = admin_class.module.objects.filter(**{i:request.POST.get(i)})
            print('1111111111111111111',obj)
            if obj:
                one_list.append(i)
        if one_list:
            admin_class.one = one_list
        if form_obj.is_valid():
            form_obj.save()
            del admin_class._status
            return redirect(request.path.replace('/add/','/'))
    else:
        form_obj = form_class()
    return render(request,'king/king_table_add.html',{'form_obj':form_obj,'app_name':app_name,'table_name':table_name,
                                                      "admin_class":admin_class})

# 删除时的视图
@login_auth
@role_auth
def table_obj_delete(request,app_name,table_name,obj_id):
    admin_class = king_admin.register_dic[app_name][table_name]
    obj = admin_class.module.objects.get(id=obj_id)
    if admin_class.readonly_table:
        error = {"error_info":"此表已为只读，不可删除，此操作非法."}
    else:
        error = {}
    if request.method == "POST":
        if not admin_class.readonly_table:
            obj.delete()
            return redirect(request.path.replace('/%s/delete/'%obj_id, '/'))
    return render(request,'king/king_table_delete.html',{'admin_class':admin_class,'objs':[obj,],'app_name':app_name,
                                                         'table_name':table_name,"error":error})

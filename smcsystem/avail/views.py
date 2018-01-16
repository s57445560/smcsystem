from django.shortcuts import render,HttpResponse,redirect
from avail.models import Info
from filing import models
# Create your views here.
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Count, Min, Max, Sum
import time,json
import datetime
import calendar as cal
import re

from smcsystem import settings

this_year = settings.THIS_YEAR

# 登陆装饰器
def login_auth(func):
    def inner(request, *args, **kwargs):
        user = request.session.get('user', None)
        if not user:
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return inner




@csrf_exempt
@login_auth
def settings_index(request):

    if request.method == "POST":
        year = request.POST.get("year")
        time_r = re.compile(r"^\d\d\d\d$")
        m = time_r.search(year)
        if m:
            global this_year
            this_year = int(year)
            return redirect("/")
    return render(request,"settings.html",{"year":this_year})


@csrf_exempt
@login_auth
def create(request):
    status = True
    message = ""
    group = models.Group.objects.all().values("name")
    cq_group = models.CQ_Group.objects.all().values("name")
    all_group = list(group)+list(cq_group)
    if request.method == "POST":
        start = request.POST.get('start',None)
        end = request.POST.get('end',None)
        text = request.POST.get("text", None)
        level = request.POST.get("level", None)
        xmname = request.POST.get("xmname", None)
        if start and end and text and xmname and level:
            s_time = time.mktime(time.strptime(start,"%Y-%m-%d %H:%M"))
            s_end = time.mktime(time.strptime(end,"%Y-%m-%d %H:%M"))
            if s_time > s_end:
                message = "起始时间不能大于结束时间，请重新填写"
            obj = models.Group.objects.filter(name=xmname)
            cq_obj = models.CQ_Group.objects.filter(name=xmname)
            if obj or cq_obj:
                print("写库")
                Info.objects.create(start_time=start,end_time=end,xmname=xmname,text=text,level=level)
            else:
                message = "所选的项目不存在，请不要修改页面"
        else:
            status = False
            message = "所有项目不能为空"
        print(start,end,text,xmname)
        return HttpResponse(json.dumps({"data":{"message":message,"status":status}}))
    level_table = Info._meta.get_field("level").choices
    return render(request,'avail/create.html',{"all_group":all_group,"level_table":level_table})


@csrf_exempt
@login_auth
def avail_index(request):
    # 新添加的功能 周出图把100%的项目也出图
    timenow = datetime.datetime.now()
    last_day = cal.monthrange(this_year, 12)[1]
    if timenow.year > int(this_year):
        print("9999999999999999999999")
        now_week = datetime.datetime(this_year, 12, last_day, 0, 0, 0).isocalendar()[1]
    else:
        now_week = timenow.isocalendar()[1]
    last_week = datetime.datetime(this_year, 12, last_day, 0, 0, 0).isocalendar()[1]
    group = models.Group.objects.all()
    cq_group = models.CQ_Group.objects.all()
    all_group = list(group) + list(cq_group)
    absolutely_list = []
    ##### 

    xm_list = Info.objects.filter(level=1,start_time__icontains=this_year).values('xmname').annotate(c=Count('xmname'))
    
    #新添加的功能 周出图把100%的项目也出图
    for name in all_group:
        absolutely_list.append(name.name)

    print(xm_list)
    for i in xm_list:
        absolutely_list.remove(i["xmname"])
    print(absolutely_list)
    ab_index = int(len(absolutely_list) / 2)
    ab_left = absolutely_list[ab_index::]
    ab_right = absolutely_list[0:ab_index]
    ##########

    xm_num = len(xm_list)
    xm_index = int(xm_num/2)
    xm_left = xm_list[xm_index::]
    xm_right = xm_list[0:xm_index]
    last_day = cal.monthrange(this_year,12)[1]
    week_day = datetime.datetime(this_year, 12, last_day, 0, 0, 0).isocalendar()[1]
    week_list = list(range(1,week_day+1))
    return render(request,"avail/index.html",{"xm_list":xm_list,"left":xm_left,"right":xm_right,"week_list":week_list,
					"now_week":now_week,"last_week":last_week,"absolutely_list":absolutely_list,
                                              "ab_left":ab_left,"ab_right":ab_right})



# 按周出图
def xm_chart(request):
    week_minute = 10080
    day_minute = 1440
    week_dic = {}
    data_list = []
    timenow = datetime.datetime.now()
    xmname = request.GET.get("xmname")
    last_day = cal.monthrange(this_year, 12)[1]
    if timenow.year > int(this_year):
        now_week = datetime.datetime(this_year, 12, last_day, 0, 0, 0).isocalendar()[1]
    else:
        now_week = timenow.isocalendar()[1]
    obj_list = Info.objects.filter(level=1,start_time__icontains=this_year,xmname=xmname).order_by("start_time")
    last_week_day = datetime.datetime(this_year, 12, last_day, 0, 0, 0).isocalendar()[1]
    for obj in obj_list:
        print(obj.start_time)
        start_day_obj = time.strptime(obj.start_time, "%Y-%m-%d %H:%M")
        end_day_obj = time.strptime(obj.end_time, "%Y-%m-%d %H:%M")
        start_week_day = datetime.datetime(start_day_obj.tm_year, start_day_obj.tm_mon, start_day_obj.tm_mday, 0, 0, 0).isocalendar()[1]
        add_day = 7 - datetime.datetime(start_day_obj.tm_year, start_day_obj.tm_mon, start_day_obj.tm_mday, 0, 0, 0).isocalendar()[2]
        end_week_day = datetime.datetime(end_day_obj.tm_year, end_day_obj.tm_mon, end_day_obj.tm_mday, 0, 0, 0).isocalendar()[1]
        if start_week_day == end_week_day:
            start = time.strptime(obj.start_time, "%Y-%m-%d %H:%M")
            end = time.strptime(obj.end_time, "%Y-%m-%d %H:%M")
            start = datetime.datetime(start[0], start[1], start[2], start[3], start[4], start[5])
            end = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5])
            days = (end-start).days
            minute = (end-start).seconds/60 + days * day_minute
            print((end-start).seconds)
            print(start,end,minute)
            if start_week_day in week_dic:
                week_dic[start_week_day] += minute
            else:
                week_dic[start_week_day] = minute
        else:
            start_end_week = datetime.datetime(start_day_obj.tm_year, start_day_obj.tm_mon, start_day_obj.tm_mday+add_day, 23, 59, 0).strftime("%Y-%m-%d %H:%M")
            end_start_week = (datetime.datetime(start_day_obj.tm_year, start_day_obj.tm_mon, start_day_obj.tm_mday, 0, 0, 0) + datetime.timedelta(days=add_day+1)).strftime("%Y-%m-%d %H:%M")
            start = datetime.datetime.strptime(obj.start_time, "%Y-%m-%d %H:%M")
            start_end = datetime.datetime.strptime(start_end_week, "%Y-%m-%d %H:%M")
            end_start = datetime.datetime.strptime(end_start_week, "%Y-%m-%d %H:%M")
            end_end = datetime.datetime.strptime(obj.end_time, "%Y-%m-%d %H:%M")
            print(start_end_week,end_start_week,add_day)
            start_days = (start_end - start).days
            end_days = (end_end - end_start).days
            start_minute = (start_end - start).seconds / 60 + start_days * day_minute
            end_minute = (end_end - end_start).seconds / 60 + end_days * day_minute
            print(start_days)
            print(end_days)
            if start_week_day in week_dic:
                week_dic[start_week_day] += start_minute
            else:
                week_dic[start_week_day] = start_minute

            if end_week_day in week_dic:
                week_dic[end_week_day] += end_minute
            else:
                week_dic[end_week_day] = end_minute

    print(week_dic)
    year_minute_num = 0
    for i in range(1,last_week_day+1):
        if i <= now_week:
            if i in week_dic:
                num = 100 - (week_dic[i] / week_minute * 100)
                data_list.append(num)
                year_minute_num += week_dic[i]
            else:
                data_list.append(100)
        else:
            data_list.append(0)
    print("okokok!")
    print(sum(data_list),len(data_list))
    data = {"data_list":data_list,"now_week":float('%.5f' %(100 - year_minute_num/525600*100))}

    print(xmname)
    return HttpResponse(json.dumps(data))

# 故障百分比出图
def gz_chart(request):
    xmname = request.GET.get("xmname")
    level1 = Info.objects.filter(xmname=xmname,level=1).count()
    level2 = Info.objects.filter(xmname=xmname,level=2).count()
    level3 = Info.objects.filter(xmname=xmname,level=3).count()
    data_list = []
    data_list.append(["一级故障",level1])
    data_list.append(["二级故障",level2])
    data_list.append(["三级故障",level3])
    data = {"data_list":data_list}
    return HttpResponse(json.dumps(data))



@csrf_exempt
@login_auth
def gz_index(request):
    xm_list = Info.objects.filter(level=1,start_time__icontains=this_year).values('xmname').annotate(c=Count('xmname'))
    xm_num = len(xm_list)
    xm_index = int(xm_num/2)
    xm_left = xm_list[xm_index::]
    xm_right = xm_list[0:xm_index]
    return render(request,"avail/gz_chart.html",{"xm_list":xm_list,"left":xm_left,"right":xm_right,})


@csrf_exempt
@login_auth
def year_chart(request):
    year_minute = 525600
    day_minute = 1440
    all_list = []
    avail_list = []
    obj_dic = {}
    xm_dic = {}
    group = models.Group.objects.all()
    cq_group = models.CQ_Group.objects.all()
    all_group = list(group) + list(cq_group)
    avail_group = Info.objects.filter(level=1,start_time__icontains=this_year).values('xmname').annotate(c=Count('xmname'))
    obj_list = Info.objects.filter(level=1, start_time__icontains=this_year).order_by("start_time")

    print(all_group)
    print(set(obj_list))
    for obj in obj_list:
        start = time.strptime(obj.start_time, "%Y-%m-%d %H:%M")
        end = time.strptime(obj.end_time, "%Y-%m-%d %H:%M")
        start = datetime.datetime(start[0], start[1], start[2], start[3], start[4], start[5])
        end = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5])
        days = (end - start).days
        minute = (end - start).seconds / 60 + days * day_minute
        if obj.xmname in obj_dic:
            obj_dic[obj.xmname] += minute
        else:
            obj_dic[obj.xmname] = minute
    for i in all_group:
        all_list.append(i.name)

    for i in avail_group:
        avail_list.append(i["xmname"])

    print(avail_list,obj_dic)

    for i in avail_list:
        num = 100 - (obj_dic[i] / year_minute * 100)
        xm_dic[i] = float('%.5f' % num)
    for i in set(all_group)-set(avail_list):
        xm_dic[i] = 100
    print(xm_dic)
    return render(request,'avail/year_chart.html',{"xm_dic":xm_dic})

from filing import models
from avail.models import Info
from django.shortcuts import render,redirect

register_dic = {}

# 父类 初始化数据，字典格式的 key：表的字段名，value 填写字段的中文名称。
# list_display 设置前端现实的字段有哪些 必须填写id, 也可以填写自定义的字段,然后必须写一个函数
# list_filter 前端现实的搜索项目有哪些 select
# list_search 设置可以查找的字段
# page_number 设置一页有多少数据显示
# ordering 设置默认排序使用那个字段，如果不设置则使用id排序
# actions 设置动作，并且编写函数
# readonly_fields 设置只读字段
# readonly_table 设置整张表的只读
# filter_horizontal 复选框的格式
# one_field 可以自己设置唯一字段
# note_field 显示鼠标悬停的效果，默认使用note的表字段来做效果，也可以自定义，这个为一个str


class BaseAdmin(object):
    list_display = []
    list_filter = []
    list_search = []
    page_number = 15
    readonly_fields = []
    filter_horizontal = []
    one_field = []
    note_field = 'note'
    ordering = None
    readonly_table = False
    actions = ['delect_select_objs',]

    # 这个是默认自带的删除action功能
    def delect_select_objs(self,request,querysets):
        app_name = self.module._meta.app_label
        table_name = self.module._meta.model_name
        select_id = ','.join([str(i.id) for i in querysets])
        if self.readonly_table:
            error = {"error_info": "此表已为只读，不可删除，此操作非法."}
        else:
            error = {}
        if request.POST.get('delect_data') == "yes":
            if request.session.get("admin") == "see":
                return redirect(request.path)
            if not self.readonly_table:
                querysets.delete()
                return redirect(request.path)
        return render(request, 'king/king_table_delete.html',{'objs': querysets,
                                                              'app_name': app_name,
                                                              'table_name': table_name,
                                                              'action':request._admin_action,
                                                              'select_id':select_id,
                                                              "admin_class":self,
                                                              "error":error})
    # 用来设置action 前台显示的中文名字是什么
    delect_select_objs.select_info_name = u"删除动作"

    def default_form_validation(self):
        # 用户可以自定义的 clean方法，相当于django form里的 clean方法
        pass


class HostAdmin(BaseAdmin):
    list_display = ('id','ip','hostname','cpu_num','disk_num','disk_capacity','mem','brand','type','status','active')
    list_filter = ('cpu_num','status','type','brand','to_group')
    list_search = ('ip', 'hostname', 'system','to_group__name','to_code__name','all_ip')
    filter_horizontal = ("to_code",'to_group')
    ordering = 'id'
    # readonly_fields = ['to_code','hostname']
    one_field = ('ip','salt_id',)
    actions = ['delect_select_objs', ]
    # readonly_table = True

    def active(self):
        h_obj = self.instance
        group_list = []
        for i in h_obj.to_group.all():
            group_list.append(i.name)
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel" style="margin-bottom: 5px">{ip} 主机程序部署详细</h3>
                <h3 id="myModalLabel">所属项目:{group}</h3>
              </div>
              <div class="">'''.format(id=h_obj.id,ip=h_obj.ip,group=', '.join(group_list))
        print(self.instance,"-----------------------obj")

        code_query_set_list = h_obj.to_code.all()
        if code_query_set_list:
            for code in code_query_set_list:
                group_list = []
                for i in code.group_set.all():
                    group_list.append(i.name)
                body += '''<div class="alert alert-info"><h4 style="color:#019858">程序名称:{name} <a class="btn btn-danger btn-mini" target="_blank" href="/king_admin/filing/code/{id}/change/">  修改数据</a>  
                <a class="btn btn-success btn-mini" target="_blank" href="/log/{host_id}/{id}/">  查看日志</a></h4>
                <p style="padding-left: 20px;">程序路径: {path}</p>
                <p style="padding-left: 20px;">端口号: {port} , 外网映射:{mapping}</p>
                <p style="padding-left: 20px;">域名: {www}</p>
                <p style="padding-left: 20px;">启动方法:{start}</p>
                <p style="padding-left: 20px;">日志位置:{log}</p>
                <p style="padding-left: 20px;">所属项目:{group_name}</p>
                </div>'''.format(name=code.name,path=code.path,port=code.port,mapping=code.mapping,start=code.start,
                                 log=code.log,www=code.www,id=code.id,host_id=h_obj.id,group_name=', '.join(group_list))
        last = '''</div>
            </div>
        </div>'''
        return body+last

    active.name = "部署程序"
    # 设置用户自己自定义的form验证
    # add_error用来添加错误信息，第一个字段为表的字段名，第二个是错误信息
    # def default_form_validation(self,admin_class):
    #     err_list = []
    #     user_data = self.cleaned_data.get('ip','')
    #     # 将错误的信息 传递到err_list列表内 然后统一返回给 clean
    #     if len(user_data) < 15:
    #         self.add_error("passwd","不能小于15")
    #
    # 设置 list_display 自定义的字段，在数据库里没有的字段在前台展示，比如跳转到另外一个页面的链接等...
    # def sunyang(self):
    #     return self.instance.id

    # 来设置自定字段的中文名称
    # sunyang.name = "自定义字段"
    # def clean_passwd(self):
    #     print(len(self.cleaned_data.get("passwd")),self.cleaned_data.get("passwd"))
    #     if len(self.cleaned_data.get("passwd")) < 10:
    #         self.add_error("passwd","不能小于10字节")


class GroupAdmin(BaseAdmin):
    list_display = ('id','name','user','phone','qq','email','active')
    list_filter = ('user','to_code')
    list_search = ('to_code__name', 'user')
    filter_horizontal = ('to_code')

    def active(self):
        h_obj = self.instance
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel">程序部署主机</h3>
              </div>
              <div class="">'''.format(id=h_obj.id)
        print(self.instance,"-----------------------obj")

        code_query_set_list = h_obj.to_code.all()
        if code_query_set_list:
            for code in code_query_set_list:
                if code.host_set.all():
                    host_ip = code.host_set.all()[0].ip
                else:
                    host_ip = ''
                body += '''<div class="alert alert-info"><h4 style="color:#019858">程序名称:{name}   所在主机:{host}</h4>
                </div>'''.format(name=code.name,host=host_ip)
        last = '''</div>
            </div>
        </div>'''
        return body+last

    active.name = "所属程序"

class CodeAdmin(BaseAdmin):
    list_display = ('id','name','code_name','path','user','phone','qq','email','active')
    list_search = ('id','name', 'code_name')

    def active(self):
        h_obj = self.instance
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel">所在主机</h3>
              </div>
              <div class="">'''.format(id=h_obj.id)
        print(self.instance, "-----------------------obj")

        code_list = h_obj.host_set.all()
        if code_list:
            for ip in code_list:
                body += '''<div class="alert alert-info"><h4 style="color:#019858">所属主机:{name}</h4>
                </div>'''.format(name=ip.ip)
        last = '''</div>
            </div>
        </div>'''
        return body + last
    active.name = "所属程序"
# register_dic 数据格式如下：
# {
#   app_name:
#   {table_name:admin_class}
#   }


######################### 车企平台
class CQ_HostAdmin(BaseAdmin):
    list_display = ('id','ip','hostname','cpu_num','disk_num','disk_capacity','mem','brand','type','status','active')
    list_filter = ('status','type','to_group')
    list_search = ('ip', 'hostname', 'system','to_group__name','to_code__name')
    filter_horizontal = ("to_code",'to_group')
    ordering = 'id'
    # readonly_fields = ['to_code','hostname']
    actions = ['delect_select_objs', ]
    # readonly_table = True


    def active(self):
        h_obj = self.instance
        group_list = []
        for i in h_obj.to_group.all():
            group_list.append(i.name)
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel" style="margin-bottom: 5px">{ip} 主机程序部署详细</h3>
                <h3 id="myModalLabel">所属项目:{group}</h3>
              </div>
              <div class="">'''.format(id=h_obj.id,ip=h_obj.ip,group=', '.join(group_list))
        print(self.instance,"-----------------------obj")

        code_query_set_list = h_obj.to_code.all()
        if code_query_set_list:
            for code in code_query_set_list:
                group_list = []
                for i in code.cq_group_set.all():
                    group_list.append(i.name)
                body += '''<div class="alert alert-info"><h4 style="color:#019858">程序名称:{name} <a class="btn btn-danger btn-mini" target="_blank" href="/king_admin/filing/code/{id}/change/">  修改数据</a>
                <p style="padding-left: 20px;">程序路径: {path}</p>
                <p style="padding-left: 20px;">端口号: {port} , 外网映射:{mapping}</p>
                <p style="padding-left: 20px;">域名: {www}</p>
                <p style="padding-left: 20px;">启动方法:{start}</p>
                <p style="padding-left: 20px;">日志位置:{log}</p>
                <p style="padding-left: 20px;">所属项目:{group_name}</p>
                </div>'''.format(name=code.name,path=code.path,port=code.port,mapping=code.mapping,start=code.start,
                                 log=code.log,www=code.www,id=code.id,host_id=h_obj.id,group_name=', '.join(group_list))
        last = '''</div>
            </div>
        </div>'''
        return body+last

    active.name = "部署程序"


class CQ_GroupAdmin(BaseAdmin):
    list_display = ('id','name','admin','user','phone','qq','email','active','info')
    list_search = ('to_code__name', 'name')
    filter_horizontal = ('to_code')


    def active(self):
        h_obj = self.instance

        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel">程序部署主机</h3>
              </div>
              <div class="">'''.format(id=h_obj.id)
        print(self.instance,"-----------------------obj")

        code_query_set_list = h_obj.to_code.all()
        if code_query_set_list:
            for code in code_query_set_list:
                if code.cq_host_set.all():
                    host_ip = code.cq_host_set.all()[0].ip
                else:
                    host_ip = ''
                body += '''<div class="alert alert-info"><h4 style="color:#019858">程序名称:{name}   所在主机:{host}</h4>
                </div>'''.format(name=code.name,host=host_ip)
        last = '''</div>
            </div>
        </div>'''
        return body+last

    active.name = "所属程序"

    def info(self):
        h_obj = self.instance
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel">信息</h3>
              </div>
              <div class="">'''.format(id=str(h_obj.id)+"info")
        print(self.instance,"-----------------------eeeee")


        body += '''
        <div class="alert alert-info">
            <h2>登陆方式:</h2>
            <pre>{note}</pre>
        </div>
        <div class="alert alert-info">
            <h2>平台访问地址:</h2>
            <pre>{www}</pre>
        </div>
        <div class="alert alert-info">
        <h4 style="color:#019858">admin 版本: {admin}</h4>
        <h4 style="color:#019858">duboo 版本: {duboo}</h4>
        <h4 style="color:#019858">openservice 版本: {openservice}</h4>
        <h4 style="color:#019858">saveservice 版本: {saveservice}</h4>
        <h4 style="color:#019858">synservice 版本: {synservice}</h4>
        <h4 style="color:#019858">alarmservice 版本: {alarmservice}</h4>
        <h4 style="color:#019858">jdk 版本: {jdk}</h4>
        <h4 style="color:#019858">plat_gb_cli 版本: {plat_gb_cli}</h4>
        <h4 style="color:#019858">term_gb_svr 版本: {term_gb_svr}</h4>
        <h4 style="color:#019858">plat_gb_svr 版本: {plat_gb_svr}</h4>
        <h4 style="color:#019858">storm 版本: {storm}</h4>
        <h4 style="color:#019858">spark 版本: {spark}</h4>
        <h4 style="color:#019858">cdh 版本: {cdh}</h4>
            </div>'''.format(admin=h_obj.admin,duboo=h_obj.duboo,openservice=h_obj.openservice,saveservice=h_obj.saveservice,
                             synservice=h_obj.synservice,alarmservice=h_obj.alarmservice,jdk=h_obj.jdk,
                             plat_gb_cli=h_obj.plat_gb_cli,term_gb_svr=h_obj.term_gb_svr,plat_gb_svr=h_obj.plat_gb_svr,
                             storm=h_obj.storm,spark=h_obj.spark,cdh=h_obj.cdh,note=h_obj.note,www=h_obj.www)
        last = '''</div>
            </div>
        </div>'''

        return body+last

    info.name = "信息"

class CQ_CodeAdmin(BaseAdmin):
    list_display = ('id','name','code_name','path','active')
    list_search = ('id','name', 'code_name')

    def active(self):
        h_obj = self.instance
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel">所在主机</h3>
              </div>
              <div class="">'''.format(id=h_obj.id)
        print(self.instance, "-----------------------obj")

        code_list = h_obj.cq_host_set.all()
        if code_list:
            for ip in code_list:
                body += '''<div class="alert alert-info"><h4 style="color:#019858">所属主机:{name}</h4>
                </div>'''.format(name=ip.ip)
        last = '''</div>
            </div>
        </div>'''
        return body + last
    active.name = "所属程序"


class InfoAdmin(BaseAdmin):
    list_display = ('id','xmname','start_time','end_time','level','text')
    list_filter = ('xmname','level')
    list_search = ('xmname','start_time')
    page_number = 30

    def active(self):
        h_obj = self.instance
        body = '''<div class="controls">
            <a href="#myModal{id}" role="button" class="btn btn-info" data-toggle="modal">查看</a>
            <div id="myModal{id}" class="modal fade" aria-labelledby="myModalLabel"  style="display: none;height: 500px;">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="myModalLabel">所在主机</h3>
              </div>
              <div class="">'''.format(id=h_obj.id)
        print(self.instance, "-----------------------obj")

        code_list = h_obj.host_set.all()
        if code_list:
            for ip in code_list:
                body += '''<div class="alert alert-info"><h4 style="color:#019858">所属主机:{name}</h4>
                </div>'''.format(name=ip.ip)
        last = '''</div>
            </div>
        </div>'''
        return body + last
    active.name = "所属程序"


def register(model_class,admin_class=None):
    app_name = model_class._meta.app_label
    table_name = model_class._meta.model_name
    if app_name not in register_dic:
        register_dic[app_name] = {}
    if admin_class == None:
        admin_class = BaseAdmin
    admin_class.module = model_class
    register_dic[app_name][table_name] = admin_class



register(models.Host, HostAdmin)
register(models.Group, GroupAdmin)
register(models.Code, CodeAdmin)
register(models.CQ_Host, CQ_HostAdmin)
register(models.CQ_Group, CQ_GroupAdmin)
register(models.CQ_Code, CQ_CodeAdmin)
register(Info, InfoAdmin)

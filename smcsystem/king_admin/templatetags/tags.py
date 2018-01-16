from django import template
from django.utils.safestring import mark_safe
from django.template.base import Node, TemplateSyntaxError
from django.db.models import Count, Min, Max, Sum
from django.core.exceptions import FieldDoesNotExist
from avail.models import Info
# 处理前台特殊需求的方法


# 向前台返回表的名字 中文的 在 Meta 里自定义中文名称
register = template.Library()
@register.simple_tag
def table_cn_name(admin_class):
    return admin_class.module._meta.verbose_name_plural




# 用来返回前台的列表数据 形成表格，obj 是查询出来的数据 （UserInfo.objects.all()）
# admin_class 使用views里返回的 表信息和 king_admin中的自定义配置
@register.simple_tag
def table_info(obj, admin_class):
    num = 1
    p = ""
    id_num = ''
    for i in admin_class.list_display:
        try:
            c = admin_class.module._meta.get_field(i)
            if c.choices:
                name = getattr(obj,"get_%s_display" % i)()
            else:
                name = getattr(obj,i)
            # 把第一个id字段设置为点击可修改标签
            if num == 1:
                if admin_class.module == Info:
                    p += "<td><a href='/king_admin/avail/info/%s/change/'>%s</a></td>" % (name, name)
                else:
                    p+="<td><a href='%s/change/'>%s</a></td>"% (name,name)
                id_num = name
                num+=1
            # 把第二个字段也设置为点击即可进入修改页面
            elif num == 2:
                note_field = admin_class.note_field
                if hasattr(obj,note_field):
                    ss = getattr(obj, note_field)
                    if not ss:
                        ss = ''
                else:
                    ss = ''
                if admin_class.module == Info:
                    p +="<td><a data-toggle='tooltip' data-placement='top' title='%s' href='/king_admin/avail/info/%s/change/'>%s</a></td>"% (ss,id_num,name)
                else:
                    p += "<td><a data-toggle='tooltip' data-placement='top' title='%s' href='%s/change/'>%s</a></td>" % (ss, id_num, name)
                num+=1
            # 剩下的标签直接打印名字
            else:
                p+="<td>%s</td>"% name
        except FieldDoesNotExist as e:
            # 用来返回 自定义字段的信息 如果上面执行报错 证明是自定义标签
            if hasattr(admin_class,i):
                result_obj = getattr(admin_class,i)
                # 传递给自定义标签的 对象信息，方便后台做处理
                admin_class.instance = obj
                name = result_obj()
                p += "<td>%s</td>"% name
    return mark_safe(p)


# select的返回结果处理，针对 普通字段 choices类型字段，和foreignkey字段进行判断处理
@register.simple_tag
def select_list(select, admin_class,filter_conditions):
    select_str = '''<select class="form-control input-sm" name="%s"><option value="">------</option>'''% select
    num = len(select_str)
    c = admin_class.module._meta.get_field(select)
    if c.choices:
        status = ''
        for i in c.choices:
            if str(i[0]) == filter_conditions.get(select):
                status = 'selected'
            select_str += '<option value="%s" %s>%s</option>'%(i[0],status,i[1])
            status = ''
    if type(c).__name__ in ["ForeignKey","ManyToManyField"]:
        status = ''
        # c.get_choices() 可以获取多对多和 一对多的 数据格式[('', '---------'), (1, '192.168.1.1'), (2, '192.168.1.2'), (3, '192.168.1.3')]
        for i in c.get_choices()[1:]:
            if str(i[0]) == filter_conditions.get(select):
                status = 'selected'
            select_str += '<option value="%s" %s>%s</option>'%(i[0], status, i[1])
            status = ''

    if len(select_str) == num:
        list_str = admin_class.module.objects.filter().values(select).annotate(c=Count(select))
        status = ''
        for i in list_str:
            if str(i[select]) == filter_conditions.get(select):
                status = 'selected'
            select_str += '''<option value="%s" %s>%s</option>''' % (i[select], status, i[select])
            status = ''
    # for i in admin_class.module.objects.filter(select).all()[0]:
    #     print(i,'aaaaaaaaa')
    #     select_str += '<option value="%s">%s</option>' % (select, i)
    select_str += '</select>'
    return mark_safe(select_str)



# 取出删除的对象，用来展示给前端
def recursive_related_objs_lookup(objs):
    ul_ele = "<ul>"
    for obj in objs:
        # li_ele = '''<li>
        #     <a href="/configure/web_hosts/change/%s/" >%s</a> </li>''' % (obj.id,obj.__repr__().strip("<>"))
        # ul_ele += li_ele
        # print("-----li",li_ele)
        li_ele = '''<li> %s: %s </li>'''%(obj._meta.verbose_name,obj.__str__().strip("<>"))
        ul_ele +=li_ele
        for m2m_field in obj._meta.local_many_to_many:
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name)
            for o in m2m_field_obj.select_related():
                li_ele = '''<li>%s: %s</li>''' % (m2m_field.verbose_name,o.__repr__().strip('<>'))
                sub_ul_ele += li_ele
            sub_ul_ele += '</ul>'
            ul_ele += sub_ul_ele
        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' not in related_obj.__repr__():
                if hasattr(obj, related_obj.get_accessor_name()):
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())

                    if hasattr(accessor_obj, 'select_related'):
                        target_objs = accessor_obj.select_related()
                        sub_ul_ele = '<ul>'
                        for o in target_objs:
                            li_ele = '''<li>%s: %s</li>''' % (o._meta.verbose_name, o.__repr__().strip('<>'))
                            sub_ul_ele += li_ele
                        sub_ul_ele += '</ul>'
                        ul_ele += sub_ul_ele
            elif hasattr(obj,related_obj.get_accessor_name()):
                accessor_obj = getattr(obj,related_obj.get_accessor_name())

                if hasattr(accessor_obj,'select_related'):
                    target_objs = accessor_obj.select_related()

                else:

                    target_objs = accessor_obj
                if len(target_objs) >0:

                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele +="</ul>"
    return ul_ele


@register.simple_tag
def get_table_delete(objs):
    '''把对象及所有相关联的数据取出来'''
    # objs = [objs,]
    if objs:
        model_class = objs[0]._meta.model
        mode_name = objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))


# 获取 action的 中文名字
@register.simple_tag
def get_action_cn_name(admin_class,action):
    action_fun = getattr(admin_class,action)
    return action_fun.select_info_name if hasattr(action_fun,'select_info_name') else action



# 让标签显示中文，需要传递 admin_class 和 king_admin里面设置的字段列表和 要显示的字段
@register.simple_tag
def get_cn_name(admin_class,field_list,field):
    cn_name_dic = {}
    for field_name in field_list:
        # 查找自定义字段内容
        if hasattr(admin_class,field_name):
            obj = getattr(admin_class,field_name)
            name = obj.name
            cn_name_dic[field_name] = name
            continue
        obj = getattr(admin_class.module, field_name)
        if hasattr(obj,"field"):
            name = obj.field.verbose_name
            cn_name_dic[field_name] = name
        else:
            for field_obj in admin_class.module._meta.fields:
                if hasattr(field_obj,'verbose_name'):
                    cn_name_dic[field_obj.name] = field_obj.verbose_name

    return cn_name_dic[field]


# 判断是不是自定义的标签，如果是自定义标签就不让他点击标签排序了
@register.simple_tag
def get_custom_field(admin_class,field):
    if hasattr(admin_class, field):
        return True
    return False


@register.simple_tag
def get_m2m(admin_class,input,form_obj):
    '''返回m2m的所有待选数据'''
    field_obj = getattr(admin_class.module, input.name)
    # 所有数据
    all_data_list = field_obj.rel.to.objects.all()
    if form_obj.instance.id:
        obj = getattr(form_obj.instance, input.name)
        # 所有选中数据
        select_data_list = obj.all()
        return set(all_data_list) - set(select_data_list)
    return field_obj.rel.to.objects.all()



@register.simple_tag
def get_m2m_select(form_obj,input):
    if form_obj.instance.id:
        obj = getattr(form_obj.instance,input.name)
        return obj.all()


@register.simple_tag
def time_format(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")

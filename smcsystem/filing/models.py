from django.db import models
import django.utils.timezone as timezone
# Create your models here.
# 用户表
class UserInfo(models.Model):
    USER_ROLE=(
        (u'1', u'admin'),
        (u'2', u'user'),
        (u'3', u'see'),
    )
    user = models.CharField(verbose_name="用户名", max_length=32)
    passwd = models.CharField(verbose_name="密码", max_length=32)
    admin = models.CharField(verbose_name="状态", max_length=32, choices=USER_ROLE, default="2")
    def __str__(self):
        return self.user

    class Meta:
        verbose_name_plural = u'用户表'


# 业务线
class Group(models.Model):
    name = models.CharField(verbose_name="业务线名称", max_length=32)
    user = models.CharField(verbose_name="总负责人", max_length=32,null=True, blank=True)
    phone = models.CharField(verbose_name="电话", max_length=32,null=True, blank=True)
    qq = models.CharField(verbose_name="qq", max_length=32,null=True, blank=True)
    email = models.EmailField(verbose_name="邮箱", max_length=32,null=True, blank=True)
    to_code = models.ManyToManyField('Code', verbose_name="所属程序", null=True, blank=True)
    note = models.TextField(verbose_name="注释", null=True, blank=True)

    def __str__(self):
        return "%s"%self.name

    class Meta:
        verbose_name_plural = u'业务信息'


# 代码
class Code(models.Model):
    name = models.CharField(verbose_name="程序名称", max_length=32)
    code_name = models.CharField(verbose_name="程序功能名称", max_length=32)
    path = models.CharField(verbose_name="程序路径", max_length=32, null=True, blank=True)
    start = models.CharField(verbose_name="启动方法", max_length=128, null=True, blank=True)
    port = models.CharField(verbose_name="端口号", max_length=128, null=True, blank=True)
    mapping = models.CharField(verbose_name="外网映射", max_length=128, null=True, blank=True)
    www = models.CharField(verbose_name="域名", max_length=128, null=True, blank=True)
    log = models.CharField(verbose_name="日志路径", max_length=128, null=True, blank=True)
    user = models.CharField(verbose_name="负责人", max_length=32, null=True, blank=True)
    phone = models.CharField(verbose_name="负责人电话", max_length=32, null=True, blank=True)
    qq = models.CharField(verbose_name="qq", max_length=32,null=True, blank=True)
    email = models.EmailField(verbose_name="邮箱", max_length=32,null=True, blank=True)
    note = models.TextField(verbose_name="注释", null=True, blank=True)

    def __str__(self):
        return "%s - %s --  %s"%(self.id,self.name,self.path)
    class Meta:
        verbose_name_plural = u'所有程序信息'

# 主机信息
class Host(models.Model):
    GENDER_CHOICE = (
        (u'1', u'在线'),
        (u'2', u'下线'),
    )
    GENDER_CROOM = (
        (u'1', u'西山机房'),
        (u'2', u'国防科技园'),
    )
    Host_CHOICE = (
        (u'1', u'物理机'),
        (u'2', u'虚拟机'),
        (u'3', u'交换机'),
        (u'4', u'路由器'),
        (u'5', u'防火墙'),
        (u'6', u'VMware'),
    )
    ip = models.CharField(verbose_name="ip地址", max_length=32,unique=True)
    hostname = models.CharField(verbose_name="主机名", max_length=50, null=True, blank=True)
    cpu_num = models.CharField(verbose_name="cpu数", max_length=32, null=True, blank=True)
    cpu_model = models.CharField(verbose_name="cpu型号", max_length=64, null=True, blank=True)
    disk_num = models.CharField(verbose_name="磁盘个数", max_length=32, null=True, blank=True)
    disk_capacity = models.CharField(verbose_name="磁盘总量", max_length=32, null=True, blank=True)
    disk_use = models.CharField(verbose_name="磁盘已用", max_length=32, null=True, blank=True)
    mem = models.CharField(verbose_name="内存大小", max_length=32, null=True, blank=True)
    mem_use = models.CharField(verbose_name="内存已用", max_length=32, null=True, blank=True)
    brand = models.CharField(verbose_name="品牌", max_length=32, null=True, blank=True)
    type = models.CharField(verbose_name="主机性质", choices=Host_CHOICE, max_length=32, null=True, blank=True, default="1")
    sn = models.CharField(verbose_name="sn号", max_length=32, null=True, blank=True)
    system = models.CharField(verbose_name="系统版本", max_length=60, null=True, blank=True)
    kernel = models.CharField(verbose_name="系统内核", max_length=60, null=True, blank=True)
    status = models.CharField(verbose_name="状态", max_length=32, choices=GENDER_CHOICE, default="1")
    c_room = models.CharField(verbose_name="机房", max_length=32, choices=GENDER_CROOM, null=True,blank=True)
    position = models.CharField(verbose_name="机柜位置", max_length=32, null=True, blank=True)
    to_code = models.ManyToManyField('Code',verbose_name="程序",null=True, blank=True)
    to_group = models.ManyToManyField('Group',verbose_name="所属项目",null=True, blank=True)
    all_ip = models.CharField(verbose_name="所有ip", max_length=128, null=True, blank=True)
    salt_id = models.CharField(verbose_name="salt配置id", max_length=32, null=True, blank=True,unique=True)
    note = models.TextField(verbose_name="注释", max_length=256, null=True, blank=True)



    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = u'主机信息'

class Host_net(models.Model):
    salt_id = models.CharField(verbose_name="salt配置id", max_length=32, null=True, blank=True, unique=True)
    ip_info = models.TextField(verbose_name="ip信息", null=True, blank=True)


# 日志
class Log(models.Model):
    host_ip = models.ForeignKey("Host",verbose_name="ip地址")
    time = models.DateTimeField(verbose_name="时间",default = timezone.now)
    level = models.CharField(verbose_name="级别", max_length=32)
    message = models.CharField(verbose_name="日志内容", max_length=128)


# 平台的历史使用数据
class Group_disk_history(models.Model):
    group = models.ForeignKey("Group", verbose_name="组的信息")
    disk_num = models.FloatField(verbose_name="使用量", max_length=32)
    date = models.DateField(verbose_name="日期",auto_now_add=True)



###################### 车企平台的配置


class CQ_Group(models.Model):
    name = models.CharField(verbose_name="业务线名称", max_length=32)
    user = models.CharField(verbose_name="总负责人", max_length=32,null=True, blank=True)
    phone = models.CharField(verbose_name="电话", max_length=32,null=True, blank=True)
    qq = models.CharField(verbose_name="qq", max_length=32,null=True, blank=True)
    email = models.EmailField(verbose_name="邮箱", max_length=32,null=True, blank=True)
    to_code = models.ManyToManyField('CQ_Code', verbose_name="所属程序", null=True, blank=True)
    www = models.TextField(verbose_name="平台访问地址", max_length=128,null=True, blank=True)
    note = models.TextField(verbose_name="登陆方式",max_length=256, null=True, blank=True)
    admin = models.CharField(verbose_name="admin 版本",max_length=32, null=True, blank=True)
    duboo = models.CharField(verbose_name="duboo 版本",max_length=32, null=True, blank=True)
    openservice = models.CharField(verbose_name="openservice 版本",max_length=32, null=True, blank=True)
    saveservice = models.CharField(verbose_name="saveservice 版本",max_length=32, null=True, blank=True)
    synservice = models.CharField(verbose_name="synservice 版本",max_length=32, null=True, blank=True)
    alarmservice = models.CharField(verbose_name="alarmservice 版本", max_length=32, null=True, blank=True)
    jdk = models.CharField(verbose_name="jdk 版本",max_length=32, null=True, blank=True,default="jdk1.7.0_67")
    plat_gb_cli = models.CharField(verbose_name="plat_gb_cli 版本",max_length=32, null=True, blank=True)
    term_gb_svr = models.CharField(verbose_name="term_gb_svr 版本",max_length=32, null=True, blank=True)
    plat_gb_svr = models.CharField(verbose_name="plat_gb_svr 版本",max_length=32, null=True, blank=True)
    storm = models.CharField(verbose_name="storm 版本",max_length=32, null=True, blank=True)
    spark = models.CharField(verbose_name="spark 版本",max_length=32, null=True, blank=True)
    cdh = models.CharField(verbose_name="cdh 版本",max_length=32, null=True, blank=True)

    def __str__(self):
        return "%s"%self.name

    class Meta:
        verbose_name_plural = u'三方平台项目信息'


# 代码
class CQ_Code(models.Model):
    name = models.CharField(verbose_name="程序名称", max_length=32)
    code_name = models.CharField(verbose_name="程序功能名称", max_length=32)
    path = models.CharField(verbose_name="程序路径", max_length=32, null=True, blank=True)
    start = models.CharField(verbose_name="启动方法", max_length=512, null=True, blank=True)
    port = models.CharField(verbose_name="端口号", max_length=128, null=True, blank=True)
    mapping = models.CharField(verbose_name="外网映射", max_length=128, null=True, blank=True)
    www = models.CharField(verbose_name="域名", max_length=128, null=True, blank=True)
    log = models.CharField(verbose_name="日志路径", max_length=128, null=True, blank=True)
    note = models.TextField(verbose_name="注释", null=True, blank=True)

    def __str__(self):
        return "%s - %s --  %s"%(self.id,self.name,self.path)
    class Meta:
        verbose_name_plural = u'三方平台程序信息'

# 主机信息
class CQ_Host(models.Model):
    GENDER_CHOICE = (
        (u'1', u'在线'),
        (u'2', u'下线'),
    )

    Host_CHOICE = (
        (u'1', u'物理机'),
        (u'2', u'虚拟机'),
        (u'3', u'交换机'),
        (u'4', u'路由器'),
        (u'5', u'防火墙'),
        (u'6', u'VMware'),
    )
    ip = models.CharField(verbose_name="ip地址", max_length=32)
    hostname = models.CharField(verbose_name="主机名", max_length=50, null=True, blank=True)
    cpu_num = models.CharField(verbose_name="cpu数", max_length=32, null=True, blank=True)
    cpu_model = models.CharField(verbose_name="cpu型号", max_length=64, null=True, blank=True)
    disk_num = models.CharField(verbose_name="磁盘个数", max_length=32, null=True, blank=True)
    disk_capacity = models.CharField(verbose_name="磁盘总量", max_length=32, null=True, blank=True)
    disk_use = models.CharField(verbose_name="磁盘已用", max_length=32, null=True, blank=True)
    mem = models.CharField(verbose_name="内存大小", max_length=32, null=True, blank=True)
    mem_use = models.CharField(verbose_name="内存已用", max_length=32, null=True, blank=True)
    brand = models.CharField(verbose_name="品牌", max_length=32, null=True, blank=True)
    type = models.CharField(verbose_name="主机性质", choices=Host_CHOICE, max_length=32, null=True, blank=True, default="1")
    sn = models.CharField(verbose_name="sn号", max_length=32, null=True, blank=True)
    system = models.CharField(verbose_name="系统版本", max_length=60, null=True, blank=True)
    kernel = models.CharField(verbose_name="系统内核", max_length=60, null=True, blank=True)
    status = models.CharField(verbose_name="状态", max_length=32, choices=GENDER_CHOICE, default="1")
    c_room = models.CharField(verbose_name="机房", max_length=32, null=True,blank=True)
    position = models.CharField(verbose_name="机柜位置", max_length=32, null=True, blank=True)
    to_code = models.ManyToManyField('CQ_Code',verbose_name="程序",null=True, blank=True)
    to_group = models.ManyToManyField('CQ_Group',verbose_name="所属项目",null=True, blank=True)
    note = models.TextField(verbose_name="注释", max_length=256, null=True, blank=True)


    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = u'三方平台主机信息'
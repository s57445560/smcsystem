from django.db import models

# Create your models here.

class Info(models.Model):
    GENDER_LEVEL = (
        (u'1', u'一级故障'),
        (u'2', u'二级故障'),
        (u'3', u'三级故障'),
    )
    END = (
        (u'1',u'处理完毕'),
        (u'2',u'遗留故障'),
    )
    xmname = models.CharField(verbose_name="项目名称", max_length=32)
    start_time = models.CharField(verbose_name="开始时间", max_length=32)
    end_time = models.CharField(verbose_name="结束时间", max_length=32, null=True, blank=True)
    text = models.TextField(verbose_name="故障信息", max_length=128, null=True, blank=True)
    level = models.CharField(verbose_name="故障级别", max_length=32, choices=GENDER_LEVEL, null=True, blank=True)
    end = models.CharField(verbose_name="处理状态", max_length=32, choices=END, null=True, blank=True,default='1')
    username = models.CharField(verbose_name="故障提交人", max_length=32, null=True, blank=True,default='admin')

    def __str__(self):
        return "%s"%self.xmname
    class Meta:
        verbose_name_plural = u'所有平台故障信息'

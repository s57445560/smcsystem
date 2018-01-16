from django.contrib import admin
from filing import models
# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('user',) 			# 设置多字段显示

admin.site.register(models.UserInfo,ArticleAdmin)
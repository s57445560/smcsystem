from django.forms import ModelForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _
# 动态生成modelform
def dynamic_class(rquest,admin_class):

    def default_clean(self):
        # 默认给所有的form添加一个 clean方法
        print('----- run clean',self.cleaned_data)
        error_list = []
        print('idididid',self.instance.id)
        if hasattr(admin_class, 'one'):
            for i in admin_class.one:
                self.add_error(i, "唯一字段")
        if self.instance.id:
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance,field)
                print(dir(field_val))
                if hasattr(field_val,'select_related'):
                    m2m_obj = getattr(field_val,'select_related')().select_related()
                    m2m_vals = [i[0] for i in m2m_obj.values_list('id')]
                    if set(m2m_vals) != set([ i.id for i in self.cleaned_data.get(field)]):
                        print('-----set',set(m2m_vals),set([ i.id for i in self.cleaned_data.get(field)]))
                        self.add_error(field, "不能被修改")
                    continue

                field_val_form_frontend = self.cleaned_data.get(field)
                print('----->',field_val,field_val_form_frontend)
                if field_val != field_val_form_frontend:
                    # error_list.append(ValidationError(
                    #     _("Field %(field)s readonly,data should be %(value)s" ),
                    #     code='invalid',
                    #     params={'field':field,'value':field_val},
                    # ))
                    self.add_error(field , "不能被修改")
        if admin_class.readonly_table:
            raise ValidationError(
                        _("这张表只读无法修改" ),
                        code='invalid',
                    )
        self.ValidationError = ValidationError
        admin_class.default_form_validation(self)
            # if response:
            #     for error_data in response:
            #         error_list.append(error_data)
            # if error_list:
            #     raise ValidationError(error_list)

            # 执行用户自己的 clean方法


    def __new__(cls,*args, **kwargs):
        for field_name,obj in cls.base_fields.items():
            # 用来给生成的标签 添加样式
            obj.widget.attrs['class'] = 'form-control'
            if not hasattr(admin_class,'_status'):
                if field_name in admin_class.readonly_fields:
                    obj.widget.attrs['disabled'] = 'disabled'

            if hasattr(admin_class,"clean_%s" % field_name):
                field_clean_func = getattr(admin_class,"clean_%s" % field_name)
                setattr(cls, "clean_%s" % field_name,field_clean_func)
        return ModelForm.__new__(cls)

    class Meta:
        model = admin_class.module
        fields = '__all__'

    parameter = {'Meta':Meta}
    d_class = type('Dynamic_class',(ModelForm,),parameter)
    setattr(d_class,'__new__',__new__)
    setattr(d_class, 'clean', default_clean)
    return d_class
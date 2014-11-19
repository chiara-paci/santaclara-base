from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms
from django.utils.html import format_html

from santaclara_base.models import Version,Annotation,Tag,Tagging,Comment
from santaclara_base.models import NameFormat,NameType,NameFormatCollection,Icon,IconFamily
from santaclara_base.forms  import VersionAdminForm, WithIconForm

class CommentInline(generic.GenericStackedInline):
    model = Comment
    extra = 0
    ordering = [ 'created' ]

class TimestampAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        if not change:
            obj.created_by = request.user
        obj.save()

class VersionAdmin(TimestampAdmin):
    list_display=('id','__unicode__','content_object','label','valid','is_current','count_characters')
    list_filter=('is_current',)
    form = VersionAdminForm

admin.site.register(Version,VersionAdmin)

class VersionInline(generic.GenericStackedInline):
    model = Version
    extra = 0
    ordering = [ '-last_modified' ]
    form = VersionAdminForm

admin.site.register(Annotation,TimestampAdmin)
admin.site.register(Tagging,TimestampAdmin)
admin.site.register(Tag)

class CommentAdmin(TimestampAdmin):
    list_display=('id','__unicode__','content_object','text',"is_public")
    list_editable=["is_public"]

admin.site.register(Comment,CommentAdmin)

class AnnotationInline(generic.GenericStackedInline):
    model = Annotation
    extra = 0
    ordering = [ 'created' ]

class TaggingInline(generic.GenericStackedInline):
    model = Tagging
    extra = 0
    ordering = [ 'created' ]

def xed_object_admin_factory(CLASS_LIST):
    class XedObjectAdmin(admin.ModelAdmin):
        def save_formset(self, request, form, formset, change):
            instances = formset.save(commit=False)
            for instance in instances:
                if reduce(lambda y,z: y or z,map(lambda x: isinstance(instance,x),CLASS_LIST)):
                    if not instance or not instance.id:
                        instance.created_by = request.user
                    instance.modified_by = request.user            
                instance.save()
            formset.save_m2m()

        def save_model(self,request, obj, form, change):
            super(XedObjectAdmin,self).save_model(request, obj, form, change)
            if Version in CLASS_LIST:
                obj.set_current()
    return XedObjectAdmin
        
VersionedObjectAdmin=xed_object_admin_factory([Version])
AnnotatedObjectAdmin=xed_object_admin_factory([Annotation])
AnnotatedVersionedObjectAdmin=xed_object_admin_factory([Annotation,Version])

admin.site.register(NameType)

class NameFormatAdmin(admin.ModelAdmin):
    list_display= ['label','pattern','description']
    list_editable = ['pattern']

admin.site.register(NameFormat,NameFormatAdmin)

class NameFormatCollectionAdmin(admin.ModelAdmin):
    list_display= ['label','description','required_name_types','long_format','short_format','list_format','ordering_format']
    list_editable = ['long_format','short_format','list_format','ordering_format']

admin.site.register(NameFormatCollection,NameFormatCollectionAdmin)

class IconAdmin(admin.ModelAdmin):
    list_display=[ "__unicode__","html_render","html",'family' ]
    list_editable=[ "html",'family' ]

    class Media:
        css = {
            "all": ("css/font-awesome.min.css",)
            }
    
    def html_render(self,obj):
        return format_html(obj.html)
    html_render.allow_tags = True

admin.site.register(Icon,IconAdmin)

class WithIconAdmin(admin.ModelAdmin):
    form = WithIconForm
    class Media:
        css = {
            "all": ("css/font-awesome.min.css",)
            }

    def html_icon_render(self,obj):
        return format_html(obj.icon.html)
    html_icon_render.allow_tags = True

    def get_changelist_form(self, request, **kwargs):
        return WithIconForm

admin.site.register(IconFamily)

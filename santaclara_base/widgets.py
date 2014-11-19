from django import forms
from django.utils.safestring import mark_safe
from santaclara_base.models import Tag
from django.utils.safestring import SafeUnicode

class SantaClaraWidget(forms.Textarea):
    class Media:
        js = ('js/jquery.js',
              'localjs/santa-clara-widget.js')

    def render(self, name, value, attrs=None):
        html = super(SantaClaraWidget, self).render(name, value, attrs=attrs)
        S=u'<div class="editor"><div class="toolbar">'
        for (tag,i) in [ ("left","align-left"), ("center","align-center"), ("right","align-right"), ("justify","align-justify"),
                          ("b","bold"), ("i","italic"), ("s","strikethrough"), ("u","underline") ]:
            S+=u'<a href="" name="'+tag+'"><i class="editor-button icon-'+i+'"></i></a>'
        S+=u'<a href="" name="code"><span class="editor-button"><b><tt>TT</tt></b></span></a>'
        S+=u'<a href="" name="term"><i class="editor-button icon-desktop"></i></a>'
        S+=u"</div>"
        return mark_safe(S+html+"</div>")

class TagWidget(forms.TextInput):
    class Media:
        js = ('js/jquery.js',
              'santaclara_base/tag-widget.js')

    def render(self, name, value, attrs=None):
        def render_tag(tag):
            T=unicode(tag)
            T='<a class="taglabel" data-widget-name='+name+'>'+T+'</a>'
            return T
        html = super(TagWidget, self).render(name, value, attrs=attrs)
        S=""
        S+=u'<a class="taglistopen" data-widget-name="'+name+'"><i class="icon-chevron-sign-left"></i><span class="tooltip">view tag list</span></a>'
        S+=u'<div class="taglist" id="taglist_'+name+'">'
        S+=u"<br/>".join(map(render_tag,Tag.objects.all()))
        S+=u'</div>'
        S+=u'<a class="taglistclose" data-widget-name="'+name+'"><i class="icon-chevron-sign-up"></i><span class="tooltip">close tag list</span></a>'
        S='<div class="taginput">'+S+html+'</div>'
        return mark_safe(S)

class IconSelect(forms.Select): 
    class Media:
        js = ('js/jquery.js',
              'santaclara_base/iconselect.css',
              'santaclara_base/iconselect.js')

    def render(self, name, value, attrs=None, choices=()):
        field_id=attrs["id"]

        hidden=u'<input id="'+field_id+'" name="'+name+'" type="hidden" value="" />'

        selected=u'none selected'
        optionsarea=u'<ul id="'+field_id+'_optionsarea" class="santaclaraiconselectul">\n'
        for k,v in self.choices:
            if not k: continue
            optionsarea+=u'<li data-value="k"'
            if unicode(k)==unicode(value):
                selected=SafeUnicode(v)
                optionsarea+=u' class="selected"'
            optionsarea+='><a href="" data-value="'+unicode(k)+'" data-target="'+field_id+'_view">'+SafeUnicode(v)+'</a></li>\n'
        optionsarea+="</ul>"

        U=u'<a href="" id="'+field_id+'_view" class="santaclaraiconselect"'
        U+=u' data-input_id="'+field_id+'" data-optionsarea_id="'+field_id+'_optionsarea">'
        U+=selected+'</a>\n'
        U+=optionsarea
        U+=hidden
        return U


        


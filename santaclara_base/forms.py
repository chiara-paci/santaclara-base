from django import forms
from santaclara_base.widgets import TagWidget,IconSelect
from santaclara_editor.widgets import SantaClaraSimpleWidget,SantaClaraJQueryUIWidget
from santaclara_base.models import Annotation,Tagging,Comment,Version

class AnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields=["object_id","content_type","text"]
        widgets = {
            'object_id': forms.HiddenInput,
            'content_type': forms.HiddenInput,
            'text': SantaClaraSimpleWidget
            }

class TaggingForm(forms.ModelForm):
    newlabel = forms.CharField(widget=TagWidget)
    class Meta:
        model = Tagging
        exclude = ('label',)
        widgets = {
            'object_id': forms.HiddenInput,
            'content_type': forms.HiddenInput,
            }

class CommentForm(forms.ModelForm):
    is_public = forms.BooleanField(required=False)
    is_removed = forms.BooleanField(required=False)

    class Meta:
        model = Comment
        fields = ["object_id","content_type","text","is_public","is_removed"]
        widgets = {
            'object_id': forms.HiddenInput,
            'content_type': forms.HiddenInput,
            'text': SantaClaraSimpleWidget
            }

class VersionForm(forms.ModelForm):
    valid = forms.BooleanField(required=False)
    label = forms.CharField(required=False)

    class Meta:
        model = Version
        fields = ["object_id","content_type","text","valid","label"]
        widgets = {
            'object_id': forms.HiddenInput,
            'content_type': forms.HiddenInput,
            'text': SantaClaraSimpleWidget
            }

class VersionAdminForm(forms.ModelForm):
    class Meta:
        model = Version
        widgets = {
            "text": SantaClaraJQueryUIWidget(attrs={"style":"adminstyle"})
            }

class WithIconForm(forms.ModelForm):
    class Meta:
        widgets = {
            "icon": IconSelect
            }

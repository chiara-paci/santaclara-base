import json

from django.http import HttpResponseRedirect,HttpResponse,HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.generic import ListView,UpdateView,CreateView,RedirectView,DeleteView,DetailView,TemplateView
from django.shortcuts import get_object_or_404,render

from santaclara_base.models import Annotation,Tagging,Tag,Comment,Version
from santaclara_base.annotability import annotator
from santaclara_base.taggability import taggator
from santaclara_base.moderators import moderator

from santaclara_base.forms import AnnotationForm,TaggingForm,CommentForm,VersionForm
from santaclara_base.forms import VersionedUpdateTextForm,VersionedVersionFormset

import santaclara_base.settings as settings

class JSTemplateView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(JSTemplateView, self).render_to_response(context,content_type='application/javascript', **kwargs)

class ByUserListView(ListView):
    def get_queryset(self):
        uid=self.kwargs["uid"]
        q=ListView.get_queryset(self)
        return q.filter(user__id=uid)

    def get_context_data(self,**kwargs):
        uid=self.kwargs["uid"]
        user=get_object_or_404(User,id=uid)
        context=super(ByUserListView,self).get_context_data(**kwargs)
        context["user_owner"]=user
        return context
    #get_context_data.alters_data = True

class RedirectToContentObjectView(RedirectView):
    model = None
    anchor = ""
    def get_redirect_url(self,pk):
        obj=get_object_or_404(self.model,pk=pk)
        if self.anchor:
            return obj.content_object.get_absolute_url()+"#"+self.anchor
        return obj.content_object.get_absolute_url()

class DeleteToContentObjectView(DeleteView):
    anchor = ""
    def get_object(self,*args,**kwargs):
        obj=DeleteView.get_object(self,*args,**kwargs)
        self.success_url=obj.content_object.get_absolute_url()
        if self.anchor:
            self.success_url+="#"+self.anchor
        return obj

class UpdateToContentObjectView(UpdateView): pass

class JsonByUserListView(ByUserListView): 
    def render_to_response(self, context, **kwargs):
        return super(JsonByUserListView, self).render_to_response(context,content_type='application/json', **kwargs)

    def get_template_names(self):
        L=super(JsonByUserListView, self).get_template_names()
        ret=map(lambda x: x.replace(".html",".json"),L)
        return(ret)

class JsonByObjectGenericListView(ListView):
    def get_queryset(self):
        content_type_id=self.kwargs["content_type_id"]
        object_id=self.kwargs["object_id"]
        q=ListView.get_queryset(self)
        return q.filter(content_type__id=content_type_id,object_id=object_id)

    def get_context_data(self,**kwargs):
        content_type_id=self.kwargs["content_type_id"]
        object_id=self.kwargs["object_id"]
        context=super(JsonByObjectGenericListView,self).get_context_data(**kwargs)
        context["content_type_id"]=content_type_id
        context["object_id"]=object_id
        return context

    def render_to_response(self, context, **kwargs):
        return super(JsonByObjectGenericListView, self).render_to_response(context,content_type='application/json', **kwargs)

    def get_template_names(self):
        L=super(JsonByObjectGenericListView, self).get_template_names()
        ret=map(lambda x: x.replace(".html",".json"),L)
        return(ret)

class JsonDetailView(DetailView): 
    def render_to_response(self, context, **kwargs):
        return super(JsonDetailView, self).render_to_response(context,content_type='application/json; charset=utf8', **kwargs)

    def get_template_names(self):
        L=super(JsonDetailView, self).get_template_names()
        ret=map(lambda x: x.replace(".html",".json"),L)
        return(ret)

class JsonListView(ListView): 
    def render_to_response(self, context, **kwargs):
        return super(JsonListView, self).render_to_response(context,content_type='application/json; charset=utf8', **kwargs)

    def get_template_names(self):
        L=super(JsonListView, self).get_template_names()
        ret=map(lambda x: x.replace(".html",".json"),L)
        return(ret)

class JsonDeleteView(DeleteView):
    def form_valid(self,form): 
        response = super(JsonDeleteView, self).form_valid(form)
        return HttpResponse(json.dumps({"delete":"OK"}),content_type='application/json')

    def form_invalid(self, form):
        response = super(JsonDeleteView, self).form_invalid(form)
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

    def delete(self,request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(json.dumps({"delete":"OK"}),content_type='application/json')

    # def dispatch(self, *args, **kwargs):
    #     response = super(JsonDeleteView, self).dispatch(*args, **kwargs)
    #     response.content_type='application/json'
    #     return response

class JsonCreateView(CreateView):
    template_name_json_response = "santaclara_base/create_response.json"

    def form_valid(self,form): 
        response = super(JsonCreateView, self).form_valid(form)
        self.object = form.save(commit=True)
        return render(self.request,self.template_name_json_response,
                      {'object': self.object},
                      content_type='application/json')

    def form_invalid(self, form):
        response = super(JsonCreateView, self).form_invalid(form)
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

class JsonTimestampCreateView(CreateView):
    template_name_json_response = "santaclara_base/create_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        response = super(JsonTimestampCreateView, self).form_valid(form)
        self.object = form.save(commit=True)
        return render(self.request,self.template_name_json_response,
                      {self.context_object_name: self.object},
                      content_type='application/json')

    def form_invalid(self, form):
        response = super(JsonTimestampCreateView, self).form_invalid(form)
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

class JsonUpdateView(UpdateView):
    template_name_json_response = "santaclara_base/update_response.json"

    def form_valid(self,form): 
        response = super(JsonUpdateView, self).form_valid(form)
        self.object = form.save(commit=True)
        return render(self.request,self.template_name_json_response,
                      {self.context_object_name: self.object},
                      content_type='application/json')

    def form_invalid(self, form):
        response = super(JsonUpdateView, self).form_invalid(form)
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

### annotation

class CreateAnnotationView(CreateView):
    model = Annotation
    form_class = AnnotationForm

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        if annotator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(settings.SANTACLARA_BASE_CONTEXT+"/annotations/add")

    #def as_view(*args, **kwargs):
    #    return CreateView.as_view(*args, **kwargs)

class JsonCreateAnnotationView(JsonCreateView):
    model = Annotation
    form_class = AnnotationForm
    template_name_json_response = "santaclara_base/annotation_add_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        response = super(JsonCreateAnnotationView, self).form_valid(form)
        if annotator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return render(self.request,self.template_name_json_response,
                          {'annotation': self.object},
                          content_type='application/json')
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

class JsonUpdateAnnotationView(JsonUpdateView):
    model = Annotation
    form_class = AnnotationForm
    template_name_json_response = "santaclara_base/annotation_update_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        response = super(JsonUpdateAnnotationView, self).form_valid(form)
        if annotator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return render(self.request,self.template_name_json_response,
                          {'annotation': self.object},
                          content_type='application/json')
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')


class CreateTaggingView(CreateView):
    model = Tagging
    form_class = TaggingForm

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        (tag,flag)=Tag.objects.get_or_create(label=form.cleaned_data["newlabel"])
        form.instance.label=tag
        if taggator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(settings.SANTACLARA_BASE_CONTEXT+"/taggings/add")
        

    #def as_view(*args, **kwargs):
    #    return CreateView.as_view(*args, **kwargs)

### comment

class CreateCommentView(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        response = super(JsonCreateCommentView, self).form_valid(form)
        if moderator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(settings.SANTACLARA_BASE_CONTEXT+"/comments/add")

class JsonCreateCommentView(JsonCreateView):
    model = Comment
    form_class = CommentForm
    template_name_json_response = "santaclara_base/comment_add_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        response = super(JsonCreateCommentView, self).form_valid(form)
        if moderator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return render(self.request,self.template_name_json_response,
                          {'comment': self.object},
                          content_type='application/json')
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

class JsonUpdateCommentView(JsonUpdateView):
    model = Comment
    form_class = CommentForm
    template_name_json_response = "santaclara_base/comment_update_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        response = super(JsonUpdateCommentView, self).form_valid(form)
        if moderator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return render(self.request,self.template_name_json_response,
                          {'comment': self.object},
                          content_type='application/json')
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

### version

class CreateVersionView(CreateView):
    model = Version
    form_class = VersionForm

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        response = super(JsonCreateVersionView, self).form_valid(form)
        if moderator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(settings.SANTACLARA_BASE_CONTEXT+"/versions/add")

class JsonCreateVersionView(JsonCreateView):
    model = Version
    form_class = VersionForm
    template_name_json_response = "santaclara_base/version_add_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        form.instance.created_by=self.request.user
        response = super(JsonCreateVersionView, self).form_valid(form)
        if moderator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return render(self.request,self.template_name_json_response,
                          {'version': self.object},
                          content_type='application/json')
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

class JsonUpdateVersionView(JsonUpdateView):
    model = Version
    form_class = VersionForm
    template_name_json_response = "santaclara_base/version_update_response.json"

    def form_valid(self,form): 
        form.instance.modified_by=self.request.user
        response = super(JsonUpdateVersionView, self).form_valid(form)
        if moderator.allow(self.request,form.instance):
            self.object = form.save(commit=True)
            return render(self.request,self.template_name_json_response,
                          {'version': self.object},
                          content_type='application/json')
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

class JsonDeleteVersionView(JsonDeleteView):
    model=Version

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Version.objects.all())
        if self.object.is_current:
            return HttpResponseBadRequest(json.dumps({"message":"can't delete current version","status": 400}),
                                          content_type='application/json')
        return super(JsonDeleteVersionView,self).post(request, *args, **kwargs)

#### da spostare

class JsonUpdateMassiveView(MultipleObjectMixin,View):
    template_name = "object_list.json"
    template_name_json_response = "object_list.json"
    form_class=None

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return render(request, self.template_name,
                      { self.context_object_name: queryset },
                      content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super(JsonUpdateMassiveView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        formset = self.formset_class(request.POST,request.FILES,queryset=self.get_queryset())
        if formset.is_valid():
            formset.save()
            object_list=[]
            for form in formset:
                object_list.append(form.instance)
            return render(request,self.template_name_json_response,
                          {self.context_object_name: object_list},
                          content_type='application/json')
        data={}
        data["formset_errors"]=formset.errors
        data["form_errors"]=[]
        for form in formset:
            data["form_errors"].append({"instance": form.instance.id,"errors":form.errors})
        data=json.dumps(data)
        return HttpResponse(data,status=400,content_type='application/json')

class JsonUpdateSingleView(SingleObjectMixin,View): 
    context_object_name = "object"
    model=None
    template_name="object_detail.json"
    template_name_json_response="object_detail.json"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())
        return render(request, self.template_name,
                      { self.context_object_name: self.object },
                      content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super(JsonUpdateFormView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.object
        return context

class JsonUpdateFormView(JsonUpdateSingleView): 
    form_class=None

    def get_post_form(self,request):
        return self.form_class(request.POST)

    def post_form_is_valid(self,request,form): 
        context={}
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())

        form=self.get_post_form(request)
        if form.is_valid():
            context=self.post_form_is_valid(request,form)
            return render(request,self.template_name_json_response,
                          context,content_type='application/json')
        data={}
        data["form_errors"]=form.errors
        data=json.dumps(data)
        return HttpResponse(data,status=400,content_type='application/json')

class JsonUpdateFormsetView(JsonUpdateSingleView):
    formset_class=None

    def get_post_formset(self,request):
        return self.formset_class(request.POST)

    def post_formset_is_valid(self,request,formset):
        context={}
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Book.objects.all())

        formset=self.get_post_formset(request)
        if formset.is_valid():
            context=self.post_formset_is_valid(request,formset)
            return render(request,self.template_name_json_response,
                          context,content_type='application/json')
        data={}
        data["formset_errors"]=formset.errors
        for form in formset:
            data["form_errors"].append({"instance": form.instance.id,"errors":form.errors})
        data=json.dumps(data)
        return HttpResponse(data,status=400,content_type='application/json')

class JsonAddChildView(JsonUpdateFormView):
    context_object_child_name = "child"
    child_model = None
    filtered_by_user = False
    default_parameters = {}
    
    def get_post_form(self,request):
        foreign_keys = []
        for field in self.child_model._meta.fields:
            if isinstance(self.child_model._meta.get_field_by_name(field.name)[0], models.ForeignKey):
                if field.rel.to == self.model:
                    foreign_keys.append(field.name)
        if not foreign_keys:
            raise Exception("%s has no ForeignKey to %s",self.child_model,self.model)
        if len(foreign_keys)>1:
            raise Exception("%s has too many ForeignKey to %s",self.child_model,self.model)
        parent_field=foreign_keys[0]

        if self.filtered_by_user:
            queryset=self.model.objects.by_user(request.user)
        else:
            queryset=self.model.objects.all()
        self.object = self.get_object(queryset=queryset)
        form=self.form_class(request.POST)
        setattr(form.instance,parent_field,self.object)
        return form

    def post_form_is_valid(self,request,form):
        self.object = self.get_object(queryset=self.model.objects.all())
        child_name=self.child_model.__name__.lower()

        params={}
        for k,v in self.default_parameters.items:
            params[k]=v
        for k,v in form.cleaned_data.items:
            params[k]=v
        params["user"]=request.user

        f_add=getattr(self.object,"add_"+child_name)
        child=f_add(params)

        return { self.context_object_child_name: child }

class JsonPositionedInsertView(JsonUpdateFormView): 
    template_name_json_response = "books/object_insert_response.json"
    parent_model = None
    context_object_parent_name = "parent"
    context_object_siblings_name = "siblings"
    parent_filtered_by_user = False

    def get_post_form(self,request):
        if self.parent_filtered_by_user:
            parent_queryset=self.parent_model.objects.by_user(request.user)
        else:
            parent_queryset=self.parent_model.objects.all()
        class MyForm(forms.Form):
            parent = forms.ModelChoiceField(queryset=parent_queryset, empty_label=None)
            before = forms.IntegerField()
        form=MyForm(request.POST)
        return form

    def post_form_is_valid(self,request,form):
        self.object = self.get_object(queryset=self.model.objects.by_user(request.user))
        parent=form.cleaned_data["parent"]
        before=form.cleaned_data["before"]
        self.object.pos_insert(parent,before)
        f=getattr(parent,"siblings_"+self.model.__name__.lower())
        return {
            self.context_object_siblings_name: f(), 
            "parent_pos": parent.full_pos()
            }

class JsonPositionedAppendView(JsonUpdateFormView): 
    template_name_json_response = "books/object_insert_response.json"
    parent_model = None
    context_object_parent_name = "parent"
    context_object_siblings_name = "siblings"
    parent_filtered_by_user = False

    def get_post_form(self,request):
        if self.parent_filtered_by_user:
            parent_queryset=self.parent_model.objects.by_user(request.user)
        else:
            parent_queryset=self.parent_model.objects.all()
        class MyForm(forms.Form):
            parent = forms.ModelChoiceField(queryset=parent_queryset, empty_label=None)
        form=MyForm(request.POST)
        return form

    def post_form_is_valid(self,request,form):
        self.object = self.get_object(queryset=self.model.objects.by_user(request.user))
        parent=form.cleaned_data["parent"]
        self.object.pos_append(parent)
        f=getattr(parent,"siblings_"+self.model.__name__.lower())
        return {
            self.context_object_siblings_name: f(), 
            "parent_pos": parent.full_pos()
            }
    
class JsonVersionedSetCurrentView(JsonUpdateFormView): 
    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())
        self.object.set_current()
        return render(request,self.template_name_json_response,
                      {self.context_object_name: self.object},
                      content_type='application/json')

class JsonVersionedUpdateTextView(JsonUpdateFormView): 
    as_new_version=False
    form_class=VersionedUpdateTextForm

    def post_form_is_valid(self,request,form):
        self.object = self.get_object(queryset=self.model.objects.all())
        text=form.cleaned_data["text"]
        self.object.save_text(request,text,as_new_version=self.as_new_version)
        return { self.context_object_name: self.object }

class VersionedUpdateVersionsView(DetailView):
    version_formset_class=VersionedVersionFormset

    def get_context_data(self,**kwargs):
        self.object=self.get_object(queryset=self.model.objects.all())
        context=super(VersionedUpdateVersionsView, self).get_context_data(**kwargs)
        context['formset_versions']=self.version_formset_class(queryset=self.object.versions.all().order_by('-created'))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())
        formset=self.version_formset_class(request.POST)
        if formset.is_valid():
            formset.save()
            self.object.save()
        return render(request,self.template_name,self.get_context_data())

class VersionedUpdateView(UpdateView):
    def get_context_data(self, **kwargs):
        context = super(VersionedUpdateView, self).get_context_data(**kwargs)
        self.object=self.get_object(queryset=self.model.objects.all())
        context['form_text'] = VersionedUpdateTextForm(instance=self.object.current)
        return context


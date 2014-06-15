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
        return super(JsonDetailView, self).render_to_response(context,content_type='application/json', **kwargs)

    def get_template_names(self):
        L=super(JsonDetailView, self).get_template_names()
        ret=map(lambda x: x.replace(".html",".json"),L)
        return(ret)

class JsonDeleteView(DeleteView):
    success_url="/"

    def form_valid(self,form): 
        response = super(JsonDeleteView, self).form_valid(form)
        return HttpResponse(json.dumps({"delete":"OK"}),content_type='application/json')

    def form_invalid(self, form):
        response = super(JsonDeleteView, self).form_invalid(form)
        return HttpResponse(json.dumps(form.errors),status=400,content_type='application/json')

    def dispatch(self, *args, **kwargs):
        response = super(JsonDeleteView, self).dispatch(*args, **kwargs)
        response.content_type='application/json'
        return response

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

class JsonUpdateView(UpdateView):
    template_name_json_response = "santaclara_base/update_response.json"

    def form_valid(self,form): 
        response = super(JsonUpdateView, self).form_valid(form)
        self.object = form.save(commit=True)
        return render(self.request,self.template_name_json_response,
                      {'object': self.object},
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



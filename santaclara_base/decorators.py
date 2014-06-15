from django.http import Http404
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required

def staff_or_404(view):
    def dec_view(request,*args,**kwargs):
        if not request.user.is_authenticated():
            raise Http404
        if request.user.is_staff:
            return view(request,*args,**kwargs)
        if request.user.is_superuser:
            return view(request,*args,**kwargs)
        raise Http404
    return dec_view

def permission_or_404(perm,model=None):
    def internal_f(view):
        def dec_view_no_model(request,*args,**kwargs):
            p_view=permission_required(perm,raise_exception=True)(view)
            try:
                ret=p_view(request,*args,**kwargs)
            except PermissionDenied, e:
                raise Http404
            except Exception,e:
                print e
                raise e
            return ret

        def dec_view(request,pk=0,*args,**kwargs):
            obj=model.objects.get(pk=pk)
            if not obj:
                raise Http404
            if request.user.has_perm(perm,obj=obj):
                return view(request,pk=pk,*args,**kwargs)
            return Http404

        if model:
            return dec_view
        else:
            return dec_view_no_model

    return internal_f


# def it_is_my_object(model):
#     def internal_f(view):
#         def dec_view(request,pk=0,*args,**kwargs):
#             if not request.user.is_authenticated():
#                 raise NotAuthenticatedException
#             if not model:
#                 raise Http404
#             obj=model.objects.get(pk=pk)
#             if not obj:
#                 raise Http404
#             try:
#                 if callable(obj.user):
#                     user=obj.user()
#                 else:
#                     user=obj.user
#             except AttributeError, e:
#                 raise Http404
#             if user.id==request.user.id:
#                 return view(request,pk=pk,*args,**kwargs)
#             raise NotMineException(request.user,obj,user)
#         return dec_view
#     return internal_f


from django.conf.urls import patterns, include, url
from django.conf import settings
#from django.views.generic import simple
from django.views.generic import DeleteView

from santaclara_base.models import Annotation,Tagging,Comment,Version

from santaclara_base.views import RedirectToContentObjectView,DeleteToContentObjectView,UpdateToContentObjectView,JsonDeleteView,JsonByObjectGenericListView
from santaclara_base.views import CreateAnnotationView,JsonCreateAnnotationView,JsonUpdateAnnotationView
from santaclara_base.views import CreateCommentView,JsonCreateCommentView,JsonUpdateCommentView
from santaclara_base.views import CreateVersionView,JsonCreateVersionView,JsonUpdateVersionView,JsonDeleteVersionView
from santaclara_base.views import CreateTaggingView
from django.contrib.auth.decorators import permission_required

from santaclara_base.decorators import staff_or_404,permission_or_404

urlpatterns =patterns('',
                      ( r'^annotations/add/?$',
                        permission_required('santaclara_base.add_annotation')(CreateAnnotationView.as_view())),
                      ( r'^annotations/(?P<pk>\d+)/?$',
                        permission_required('santaclara_base.view_annotation')(RedirectToContentObjectView.as_view(model=Annotation))),
                      ( r'^annotations/(?P<pk>\d+)/update/?$',
                        permission_required('santaclara_base.change_annotation')(UpdateToContentObjectView.as_view(model=Annotation))),
                      ( r'^annotations/(?P<pk>\d+)/delete/?$',
                        permission_required('santaclara_base.delete_annotation')(DeleteToContentObjectView.as_view(model=Annotation))),
                      ( r'^json/annotations/add/?$',
                        permission_required('santaclara_base.add_annotation')(JsonCreateAnnotationView.as_view())),
                      ( r'^json/annotations/(?P<pk>\d+)/update/?$',
                        permission_required('santaclara_base.change_annotation')(JsonUpdateAnnotationView.as_view())),
                      ( r'^json/annotations/(?P<pk>\d+)/delete/?$',
                        permission_required('santaclara_base.delete_annotation')(JsonDeleteView.as_view(model=Annotation))),
                      )

urlpatterns +=patterns('',
                       ( r'^taggings/add/?$',
                         permission_required('santaclara_base.add_tagging')(CreateTaggingView.as_view())),
                       ( r'^taggings/(?P<pk>\d+)/?$',
                         permission_required('santaclara_base.view_tagging')(RedirectToContentObjectView.as_view(model=Tagging,anchor="tags"))),
                       ( r'^taggings/(?P<pk>\d+)/delete/?$',
                         permission_required('santaclara_base.delete_tagging')(DeleteToContentObjectView.as_view(model=Tagging,anchor="tags"))),
                       )

urlpatterns +=patterns('',
                       ( r'^comments/add/?$',
                         permission_required('santaclara_base.add_comment')(CreateCommentView.as_view())),
                       ( r'^comments/(?P<pk>\d+)/?$',
                         permission_required('santaclara_base.view_comment')(RedirectToContentObjectView.as_view(model=Comment))),
                       ( r'^comments/(?P<pk>\d+)/update/?$',
                         permission_required('santaclara_base.change_comment')(UpdateToContentObjectView.as_view(model=Comment))),
                       ( r'^comments/(?P<pk>\d+)/delete/?$',
                         permission_required('santaclara_base.delete_comment')(DeleteToContentObjectView.as_view(model=Comment))),
                       ( r'^json/comments/add/?$',
                         permission_required('santaclara_base.add_comment')(JsonCreateCommentView.as_view())),
                       ( r'^json/comments/(?P<pk>\d+)/update/?$',
                         permission_required('santaclara_base.change_comment')(JsonUpdateCommentView.as_view())),
                       ( r'^json/comments/(?P<pk>\d+)/delete/?$',
                         permission_required('santaclara_base.delete_comment')(JsonDeleteView.as_view(model=Comment))),
                       ( r'^json/comments/list_by_object/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$',
                         permission_required('santaclara_base.view_comment')(JsonByObjectGenericListView.as_view(model=Comment))),
                       )

urlpatterns +=patterns('',
                       ( r'^versions/add/?$',
                         permission_required('santaclara_base.add_version')(CreateVersionView.as_view())),
                       ( r'^versions/(?P<pk>\d+)/?$',
                         permission_required('santaclara_base.view_version')(RedirectToContentObjectView.as_view(model=Version))),
                       ( r'^versions/(?P<pk>\d+)/update/?$',
                         permission_required('santaclara_base.change_version')(UpdateToContentObjectView.as_view(model=Version))),
                       ( r'^versions/(?P<pk>\d+)/delete/?$',
                         permission_required('santaclara_base.delete_version')(DeleteToContentObjectView.as_view(model=Version))),
                       ( r'^json/versions/add/?$',
                         permission_required('santaclara_base.add_version')(JsonCreateVersionView.as_view())),
                       ( r'^json/versions/(?P<pk>\d+)/update/?$',
                         permission_required('santaclara_base.change_version')(JsonUpdateVersionView.as_view())),
                       ( r'^json/versions/(?P<pk>\d+)/delete/?$',
                         permission_required('santaclara_base.delete_version')(JsonDeleteVersionView.as_view())),
                       ( r'^json/versions/list_by_object/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$',
                         permission_required('santaclara_base.view_version')(JsonByObjectGenericListView.as_view(model=Version))),
                       )



# quelle che seguono sono quelle di costruttoridimondi, trovare un modo per gestire i permessi

# urlpatterns =patterns('',
#                       ( r'^annotations/add/?$',
#                         introduction_or_404(CreateAnnotationView.as_view())),
#                       ( r'^annotations/(?P<pk>\d+)/?$',
#                         it_is_my_object(Annotation)(RedirectToContentObjectView.as_view(model=Annotation))),
#                       ( r'^annotations/(?P<pk>\d+)/update/?$',
#                         it_is_my_object(Annotation)(UpdateToContentObjectView.as_view(model=Annotation))),
#                       ( r'^annotations/(?P<pk>\d+)/delete/?$',
#                         it_is_my_object(Annotation)(DeleteToContentObjectView.as_view(model=Annotation))),
#                       ( r'^json/annotations/add/?$',
#                         introduction_or_404(JsonCreateAnnotationView.as_view())),
#                       ( r'^json/annotations/(?P<pk>\d+)/update/?$',
#                         it_is_my_object(Annotation)(JsonUpdateAnnotationView.as_view())),
#                       ( r'^json/annotations/(?P<pk>\d+)/delete/?$',
#                         it_is_my_object(Annotation)(JsonDeleteView.as_view(model=Annotation))),
#                       )

# urlpatterns +=patterns('',
#                        ( r'^taggings/add/?$',
#                          introduction_or_404(CreateTaggingView.as_view())),
#                        ( r'^taggings/(?P<pk>\d+)/?$',
#                          it_is_my_object(Tagging)(RedirectToContentObjectView.as_view(model=Tagging,anchor="tags"))),
#                        ( r'^taggings/(?P<pk>\d+)/delete/?$',
#                          it_is_my_object(Tagging)(DeleteToContentObjectView.as_view(model=Tagging,anchor="tags"))),
#                        )

# urlpatterns +=patterns('',
#                        ( r'^comments/add/?$',
#                          introduction_or_404(CreateCommentView.as_view())),
#                        ( r'^comments/(?P<pk>\d+)/?$',
#                          introduction_or_404(RedirectToContentObjectView.as_view(model=Comment))),
#                        ( r'^comments/(?P<pk>\d+)/update/?$',
#                          it_is_my_object(Comment)(UpdateToContentObjectView.as_view(model=Comment))),
#                        ( r'^comments/(?P<pk>\d+)/delete/?$',
#                          it_is_my_object(Comment)(DeleteToContentObjectView.as_view(model=Comment))),
#                        ( r'^json/comments/add/?$',
#                          introduction_or_404(JsonCreateCommentView.as_view())),
#                        ( r'^json/comments/(?P<pk>\d+)/update/?$',
#                          it_is_my_object(Comment)(JsonUpdateCommentView.as_view())),
#                        ( r'^json/comments/(?P<pk>\d+)/delete/?$',
#                          it_is_my_object(Comment)(JsonDeleteView.as_view(model=Comment))),
#                        ( r'^json/comments/list_by_object/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$',
#                          JsonByObjectGenericListView.as_view(model=Comment)),
#                        )

# urlpatterns +=patterns('',
#                        ( r'^versions/add/?$',
#                          introduction_or_404(CreateVersionView.as_view())),
#                        ( r'^versions/(?P<pk>\d+)/?$',
#                          introduction_or_404(RedirectToContentObjectView.as_view(model=Version))),
#                        ( r'^versions/(?P<pk>\d+)/update/?$',
#                          it_is_my_object(Version)(UpdateToContentObjectView.as_view(model=Version))),
#                        ( r'^versions/(?P<pk>\d+)/delete/?$',
#                          it_is_my_object(Version)(DeleteToContentObjectView.as_view(model=Version))),
#                        ( r'^json/versions/add/?$',
#                          introduction_or_404(JsonCreateVersionView.as_view())),
#                        ( r'^json/versions/(?P<pk>\d+)/update/?$',
#                          it_is_my_object(Version)(JsonUpdateVersionView.as_view())),
#                        ( r'^json/versions/(?P<pk>\d+)/delete/?$',
#                          it_is_my_object(Version)(JsonDeleteVersionView.as_view())),
#                        ( r'^json/versions/list_by_object/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$',
#                          JsonByObjectGenericListView.as_view(model=Version)),
#                        )

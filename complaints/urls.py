from django.urls import path
from .views import ComplaintCommentsListCreate, ComplaintList, ComplaintDetail, CommentsDetail




urlpatterns = [
    path("api/complaint/",ComplaintList.as_view(), name="complaint_list"),
    path("api/complaint/<int:pk>/",ComplaintDetail.as_view(), name="complaint_list"),
    path("api/complaint/<int:complaint_id>/comments/",ComplaintCommentsListCreate.as_view(), name="complaint_list"),
    path("api/comments/<int:pk>/",CommentsDetail.as_view(),name="complaints_detail"), # list comments by its own id

]
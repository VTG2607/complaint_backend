from django.urls import path
from .views import (CommentsListCreate, 
                    ComplaintList, 
                    ComplaintDetail, 
                    CommentsDetail,  
                    CategoryList)


urlpatterns = [
    path("complaint/",ComplaintList.as_view(), name="complaint_list"), # all complaints list
    path("complaint/<int:pk>/",ComplaintDetail.as_view(), name="complaint_list"), # complaints list by id
    path("complaint/<int:complaint_id>/comments/",CommentsListCreate.as_view(), name="complaint_list"),
    path("comments/<int:pk>/",CommentsDetail.as_view(), name="complaints_detail"), # list comments by its own id
    path("categories/",CategoryList.as_view(), name="category_list"),
    
]
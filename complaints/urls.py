from django.urls import path, include
from .views import (CommentsListCreate, 
                    ComplaintList,
                    ComplaintListUser,
                    ComplaintDetail,
                    CommentsDetail,  
                    CategoryList,
                    UserMe,
                    ComplaintListByCategory,
                    UserViewSet)
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("complaint/", ComplaintList.as_view(), name="complaint_list"), # all complaints list
    path("complaint/<int:pk>/", ComplaintDetail.as_view(), name="complaint_list_id"), # complaints list by id
    path("complaint/<int:complaint_id>/comments/",CommentsListCreate.as_view(), name="comment_list"), # list and create comments for a certain complaint
    path("comments/<int:pk>/", CommentsDetail.as_view(), name="comments_detail"), # list comments by its own id
    path("categories/", CategoryList.as_view(), name="category_list"), # list categories
    path("complaint/category/<int:category_id>/", ComplaintListByCategory.as_view(), name="complaint_by_category"), # list complaints by category
    path("me/",UserMe.as_view(), name="user_me"), # list current logged in user
    path("complaint/me/", ComplaintListUser.as_view(), name="complaint_list_user"), # logged in user's complaints
    path("", include(router.urls)),   # This auto-adds all the user endpoints
]
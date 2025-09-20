from django.shortcuts import render
from .models import Comments, Category, Complaint
from .serializers import CommentsSerializer, ComplaintSerializer, CategorySerializer, UserSerializer
from rest_framework import generics, permissions
from .permissions import IsAuthororReadOnly, IsAdminOrReadOnly
from django.contrib.auth import get_user_model,get_user
from rest_framework import viewsets
from rest_framework.exceptions import APIException



class ComplaintList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user) #other users cannot set created_by


class ComplaintListUser(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    
    def get_queryset(self):
        return Complaint.objects.filter(created_by=self.request.user)  #returns the complaints of the specific user
    



class CommentsListCreate(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    
    def get_queryset(self):
        complaint_id = self.kwargs.get("complaint_id")
        return Comments.objects.filter(post_id=complaint_id) # Django automatically stores the linked complaint’s primary key in a column called post_id.


    def perform_create(self, serializer):
        complaint_id = self.kwargs.get("complaint_id")
        serializer.save(
            post_id = complaint_id,
            comment_author = self.request.user   # sets logged in user as the commenter, so u cant jsut use anyones account
        )


class ComplaintListByCategory(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Complaint.objects.filter(category_id=category_id)



class CategoryList(generics.ListCreateAPIView):    #listing/creating Categories
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ComplaintDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthororReadOnly] # detail complaints can be deleted by author only
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer


class CommentsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthororReadOnly] # all comments are listed and can be deleted by author
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer



"""class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthororReadOnly]   # Admin can delete categories/update them
    queryset = Category.objects.all()
    serializer_class = CatgeorySerializer """



class UserMe(generics.RetrieveAPIView):     #users can view data about themselves
    permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet): # viewset for accessing the users
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer



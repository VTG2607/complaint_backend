from django.shortcuts import render
from .models import Comments, Category, Complaint
from .serializers import CommentsSerializer, ComplaintSerializer, CategorySerializer
from rest_framework import generics

class ComplaintList(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer


class ComplaintCommentsListCreate(generics.ListCreateAPIView):
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

class ComplaintDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer


class CommentsDetail(generics.RetrieveUpdateDestroyAPIView): # all comments are listed and can be deleted
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
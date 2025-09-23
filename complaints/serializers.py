from .models import Complaint, Category, Comments
from rest_framework import serializers
from django.contrib.auth import get_user_model


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields=(
            "name",
        )
class ComplaintSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Complaint
        fields = (
            "id",
            "title",
            "body",
            "created_by",
            "created_at",
            "updated_at",
            "category",
            "priority",
            "status",
        )
        read_only_fields = ("created_by",) # read-only



class CommentsSerializer(serializers.ModelSerializer):
    comment_author = serializers.StringRelatedField()
    class Meta:
        model = Comments
        fields = (
            "id",
            "post",
            "comment_body",
            "comment_author",
            "created_at",
        )
        read_only_fields = ["comment_author","post"]

class UserSerializer(serializers.ModelSerializer): 
    class Meta:
        model = get_user_model()
        fields = ("id", "username","email")
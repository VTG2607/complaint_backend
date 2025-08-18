from .models import Complaint, Category, Comments
from rest_framework import serializers, generics



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields={
            "name",
        }
class ComplaintSerializer(serializers.ModelSerializer):
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
        



class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = (
            "id",
            "post",
            "comment_body",
            "comment_author",
            "created_at",
        )
from rest_framework import permissions



class IsAuthororReadOnly(permissions.BasePermission):

    # Authenticated users can see list view
    def has_permission(self,request, view):
        if request.user.is_authenticated:
            return True
        
        return False
    


    def has_object_permission(self, request, view, obj):
        #ANyone is allowed to do GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        

        # Write Permissions for authors only or staff
        if hasattr(obj,"comment_author"):
            return obj.comment_author == request.user or request.user.is_staff
        
        if hasattr(obj,"created_by"):
            return obj.created_by == request.user or request.user.is_superuser
        
        return False
    
        

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        

        return request.user and request.user.is_staff
    


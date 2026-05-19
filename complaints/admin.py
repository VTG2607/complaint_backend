from django.contrib import admin
from django.db.models import Case, Count, IntegerField, Value, When

from .models import Category, Comments, Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
	# Display fields in the admin list view
	list_display = (
		"title",
		"category",
		"priority_display",
		"last_changed",
		"comment_count",
		"status",
		"created_at",
	)
	list_filter = ("category",) # Filter by category in the admin sidebar
	search_fields = ("title", "body") # Enable search by title and body
	ordering = ("-updated_at",) # Order by last updated date descending
	list_select_related = ("category", "created_by") # Optimize queries by selecting related category and user

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		return queryset.annotate(
			# Annotate the number of comments for each complaint
			comment_count=Count("comments", distinct=True), 
			# Annotate a priority rank for ordering purposes
			priority_rank=Case(
				When(priority=Complaint.Priority.LOW, then=Value(1)),
				When(priority=Complaint.Priority.MEDIUM, then=Value(2)),
				When(priority=Complaint.Priority.HIGH, then=Value(3)),
				default=Value(0),
				output_field=IntegerField(),
			),
		)
	
	# Display the priority as a human-readable string in the admin list view
	@admin.display(ordering="priority_rank", description="Priority")
	def priority_display(self, obj):
		return obj.priority

	@admin.display(ordering="updated_at", description="Last changed")
	def last_changed(self, obj):
		return obj.updated_at

	@admin.display(ordering="comment_count", description="Comments")
	def comment_count(self, obj):
		return obj.comment_count


admin.site.register(Comments)
admin.site.register(Category)

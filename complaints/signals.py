from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Complaint, Comments


@receiver(post_save, sender=Comments)
@receiver(post_delete, sender=Comments)
def touch_complaint_on_comment_change(sender, instance, **kwargs):
    Complaint.objects.filter(pk=instance.post_id).update(updated_at=timezone.now())
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile
import os

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_delete, sender=Profile)
def delete_profile_files(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

    if instance.shop_logo:
        instance.shop_logo.delete(save=False)
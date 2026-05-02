from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            Profile.objects.get_or_create(user=instance)

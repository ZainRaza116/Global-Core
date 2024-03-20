from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Messages


@receiver(post_save, sender=Messages)
def handle_message_post_save(sender, instance, created, **kwargs):
    if created:
        sale = instance.sale
        sale.messages.exclude(pk=instance.pk).update(is_read=False)

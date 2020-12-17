from django.db import models

# Create your models here.
from django.db.models import ForeignKey

from deferred_save.managers import BulkHelperManager


class Blog(models.Model):
    name = models.TextField()


class Post(models.Model):
    name = models.TextField()
    blog = models.ForeignKey("Blog", on_delete=models.CASCADE)

    objects = models.Manager()
    bulk_manager = BulkHelperManager()


class Comment(models.Model):
    parent_obj_keys = ["post"]
    name = models.TextField()
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    tags = models.ManyToManyField("Tag")

    objects = models.Manager()
    bulk_manager = BulkHelperManager()


class Tag(models.Model):
    name = models.TextField()


Comment_Tag = Comment.tags.through
Comment_Tag.add_to_class("bulk_manager", BulkHelperManager())

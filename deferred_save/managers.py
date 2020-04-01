from django.db import models
from django.db.models import ForeignKey



class BulkHelperMixin:
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        foreign_key_fields = [field for field in objs[0]._meta.get_fields() if type(field) == ForeignKey]
        for obj in objs:
            for foreign_key_field in foreign_key_fields:
                parent_obj = getattr(obj, foreign_key_field.name)
                if parent_obj and getattr(obj, foreign_key_field.column) is None:
                    setattr(obj, foreign_key_field.name, parent_obj)
        return super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)


class BulkHelperManager(BulkHelperMixin, models.Manager):
    pass

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy

from onadata.apps.fieldsight.models import Site
from onadata.apps.logger.models import XForm

@receiver(post_save, sender=XForm)
def save_to_fieldsight_form(sender, instance, **kwargs):
    FieldSightXF.objects.create(xf=instance)

SHARED_LEVEL = [(0, 'Global'), (1, 'Organization'), (2, 'Project'),]


class FormGroup(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="form_group")

    class Meta:
        db_table = 'fieldsight_forms_group'
        verbose_name = ugettext_lazy("FieldSight Form Group")
        verbose_name_plural = ugettext_lazy("FieldSight Form Groups")
        ordering = ("-date_modified",)


class Stage(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(FormGroup,related_name="stage")
    order = models.IntegerField(default=0)
    stage = models.ForeignKey('self', blank=True, null=True, related_name="parent")
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fieldsight_forms_stage'
        verbose_name = ugettext_lazy("FieldSight Form Stage")
        verbose_name_plural = ugettext_lazy("FieldSight Form Stages")
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.parent and self.parent.parent:
            raise Exception("SubStage Cant Have Substages")
        else:
            super(Stage, self).save(*args, **kwargs)

    def get_display_name(self):
        return "Stage" if self.stage else "SubStage"

    def is_main_stage(self):
        return True if self.stage else False

    def __unicode__(self):
        return getattr(self, "name", "")


#  table name in meta , consistent

#  save only one sub stage depth.

# class SubStage(models.Model):
#     name = models.CharField(max_length=256)
#     order_no = models.IntegerField
#     stage = models.ForeignKey(Stages, related_name="sub_stage")

class Schedule(models.Model):
    name = models.CharField("Schedule Name", max_length=256)
    date_range_start = models.DateField(auto_now=True)
    date_range_end = models.DateField(auto_now=True)
    group = models.ForeignKey(FormGroup, related_name="schedule")
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)

    class Meta:
        db_table = 'fieldsight_forms_schedule'
        verbose_name = ugettext_lazy("Form Schedule")
        verbose_name_plural = ugettext_lazy("Form Schedules")
        ordering = ("date_range_start",)

    def __unicode__(self):
        return getattr(self, "name", "")


class FieldSightXF(models.Model):
    xf = models.ForeignKey(XForm, related_name="field_sight_form")
    site = models.ForeignKey(Site, related_name="site_forms", null=True, blank=True)
    is_staged = models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True)
    schedule = models.ForeignKey(Schedule, blank=True, null=True)
    stage = models.ForeignKey(Stage, blank=True, null=True)
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)

    class Meta:
        db_table = 'fieldsight_forms_data'
        # unique_together = (("xf", "site"), ("xf", "is_staged", "stage"),("xf", "is_scheduled", "schedule"))
        verbose_name = ugettext_lazy("XForm")
        verbose_name_plural = ugettext_lazy("XForms")
        ordering = ("-date_created",)

    def url(self):
        return reverse(
            "download_fild_sight_form",
            kwargs={
                "site": self.site.username,
                "id_string": self.id_string
            }
        )

    def form_type(self):
        if self.is_scheduled: return "Scheduled"
        if self.is_staged: return "Staged"
        if not self.is_scheduled and not self.is_staged: return "Normal"

    def __unicode__(self):
        return u'{}- {}- {}'.format(self.xf, self.site, self.is_staged)

post_save.connect(save_to_fieldsight_form, sender=XForm)
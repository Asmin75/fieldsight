# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_reportdashboard_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportdashboard',
            name='dashboadData',
            field=jsonfield.fields.JSONField(default=dict, null=True, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_auto_20181002_1643'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportdashboard',
            old_name='dashboadData',
            new_name='dashboardData',
        ),
    ]

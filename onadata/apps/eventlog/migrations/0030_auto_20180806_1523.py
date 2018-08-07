# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0029_auto_20180513_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='task_type',
            field=models.IntegerField(default=0, choices=[(0, 'Bulk Site Upload'), (1, 'Multi User Assign Project'), (2, 'Multi User Assign Site'), (3, 'Report Generation'), (4, 'Site Import')]),
        ),
    ]

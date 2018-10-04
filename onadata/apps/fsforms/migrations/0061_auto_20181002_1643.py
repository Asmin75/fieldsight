# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0060_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectgeojson',
            name='project',
        ),
        migrations.DeleteModel(
            name='ProjectGeoJSON',
        ),
    ]

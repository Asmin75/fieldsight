# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0065_auto_20180903_1514'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportDashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dashboadData', jsonfield.fields.JSONField(default=dict)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(null=True, blank=True)),
                ('is_deployed', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('project', models.ForeignKey(related_name='project_report_dashboards', to='fieldsight.Project')),
            ],
        ),
    ]

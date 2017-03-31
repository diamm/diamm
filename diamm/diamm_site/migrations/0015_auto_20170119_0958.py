# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0014_remove_dissertationpage_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemreport',
            name='completed',
        ),
        migrations.AddField(
            model_name='problemreport',
            name='accepted',
            field=models.BooleanField(default=False, help_text="If the change has been accepted as substantive by DIAMM staff, check this box. This will add the record to the linked source's Contributors area."),
        ),
    ]

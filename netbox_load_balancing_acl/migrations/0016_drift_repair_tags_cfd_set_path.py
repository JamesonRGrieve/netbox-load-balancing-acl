# SPDX-License-Identifier: AGPL-3.0-or-later
# Repairs migration-state drift that predates 0015 (makemigrations --check failed on main): tags on the three 0007
# tuning models (TaggedItem m2m, no table), CustomFieldJSONEncoder on their custom_field_data and lbacl.tags state,
# and set_path's default="" (0009) that the model never declared. State only: no DDL (card 406).

import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0138_customfieldchoiceset_choice_colors'),
        ('netbox_load_balancing_acl', '0015_routing_rule_path_scope'),
    ]

    operations = [
        migrations.AddField(
            model_name='lbbackendtuning',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='lbfrontendtuning',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='lbhealthchecktuning',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        # 0004 created lbacl.tags as a plain ManyToManyField (join table netbox_load_balancing_acl_lbacl_tags), but the
        # model's tags are NetBoxModel's TaggableManager through extras.TaggedItem, which the ORM has always used. Django
        # cannot AlterField an M2M into a through= manager ("not compatible types"), so fix the state only. The orphan join
        # table is left untouched; dropping it is DDL and a separate decision (card 406).
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name='lbacl', name='tags'),
                migrations.AddField(
                    model_name='lbacl',
                    name='tags',
                    field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterField(
            model_name='lbbackendtuning',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AlterField(
            model_name='lbfrontendtuning',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AlterField(
            model_name='lbhealthchecktuning',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AlterField(
            model_name='lbroutingrule',
            name='set_path',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

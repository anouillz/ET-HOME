# Generated by Django 5.1.4 on 2025-01-20 13:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ET_HOME', '0003_bankaccount_secret_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='spendingcategory',
            name='default_budget',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='spendingcategory',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='spendingcategory',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='spendingcategory',
            name='user_budget',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]

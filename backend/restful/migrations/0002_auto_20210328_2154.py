# Generated by Django 3.1.5 on 2021-03-28 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restful', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='assign_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courier',
            name='complete_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='assignee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_orders', to='restful.courier'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

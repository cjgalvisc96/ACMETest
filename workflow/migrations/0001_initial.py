# Generated by Django 3.2.6 on 2021-08-08 23:04

from django.db import migrations, models
import djongo.models.fields
import workflow.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('balance', models.FloatField()),
                ('workflows_ids', djongo.models.fields.JSONField(verbose_name=[models.CharField(max_length=24)])),
                ('user', djongo.models.fields.EmbeddedField(model_container=workflow.models.User)),
                ('transactions', djongo.models.fields.ArrayField(model_container=workflow.models.Transaction)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('old_balance', models.FloatField()),
                ('balance_after_transaction', models.FloatField()),
                ('previous_transaction_id', models.FloatField()),
                ('next_transaction_id', models.FloatField()),
                ('workflow_id', models.CharField(max_length=24)),
                ('action', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('condition', djongo.models.fields.JSONField(verbose_name=[{'field_id': models.CharField(max_length=200), 'from_id': models.CharField(max_length=200, null=True), 'operator': models.CharField(max_length=200), 'value': [models.BooleanField(), models.FloatField()]}])),
                ('target', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=200)),
                ('pin', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('steps', djongo.models.fields.JSONField(verbose_name=[{'action': models.CharField(max_length=200), 'id': models.CharField(max_length=200), 'params': djongo.models.fields.JSONField(verbose_name={}), 'transitions': djongo.models.fields.ArrayField(model_container=workflow.models.Transition)}])),
                ('trigger', djongo.models.fields.JSONField(verbose_name={'id': models.CharField(max_length=200), 'params': djongo.models.fields.JSONField(verbose_name={}), 'transitions': djongo.models.fields.ArrayField(model_container=workflow.models.Transition)})),
            ],
        ),
    ]

from djongo import models


class User(models.Model):
    _id = models.ObjectIdField()
    user_id = models.CharField(max_length=50)
    pin = models.IntegerField()

    class Meta:
        abstract = True


class Transaction(models.Model):
    _id = models.ObjectIdField()
    date = models.DateTimeField()
    old_balance = models.FloatField()
    balance_after_transaction = models.FloatField()
    previous_transaction_id = models.FloatField()
    next_transaction_id = models.FloatField()
    workflow_id = models.CharField(max_length=24)


class Account(models.Model):
    _id = models.ObjectIdField()
    balance = models.FloatField()
    workflows_ids = models.JSONField(
        [
            models.CharField(max_length=24)
        ]
    )
    user = models.EmbeddedField(model_container=User)
    transactions = models.ArrayField(model_container=Transaction)


class Transition(models.Model):
    _id = models.ObjectIdField()
    condition = models.JSONField(
        [
            {
                "from_id": models.CharField(max_length=50, null=True),
                "field_id": models.CharField(max_length=50),
                "operator": models.CharField(max_length=50),
                "value": [models.BooleanField(), models.FloatField()]
            }
        ]
    )
    target = models.CharField(max_length=50)


class Workflow(models.Model):
    _id = models.ObjectIdField()
    steps = models.JSONField(
        [
            {
                "id": models.CharField(max_length=50),
                "params": models.JSONField({}),
                "action": models.CharField(max_length=50),
                "transitions": models.ArrayField(model_container=Transition)
            }
        ]
    )
    trigger = models.JSONField(
        {
            "id": models.CharField(max_length=50),
            "params": models.JSONField({}),
            "transitions": models.ArrayField(model_container=Transition)
        }
    )

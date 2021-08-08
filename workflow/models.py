from djongo import models


class User(models.Model):
    _id = models.ObjectIdField()
    user_id = models.CharField(max_length=50)
    pin = models.IntegerField()

    class Meta:
        abstract = True


class Transaction(models.Model):
    _id = models.ObjectIdField()
    transaction_id = models.CharField(max_length=50)
    date = models.DateTimeField()
    old_balance = models.FloatField()
    balance_after_transaction = models.FloatField()
    previous_transaction_id = models.FloatField()
    next_transaction_id = models.FloatField()


class Account(models.Model):
    _id = models.ObjectIdField()
    account_id = models.CharField(max_length=50)
    balance = models.FloatField()
    workflow_id = models.CharField(max_length=24)
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
            "params": models.JSONField({}),
            "transitions": models.ArrayField(model_container=Transition),
            "id": models.CharField(max_length=50)
        }
    )

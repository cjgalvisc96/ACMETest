from djongo import models


class Account(models.Model):
    _id = models.ObjectIdField()
    balance = models.FloatField()
    user = models.JSONField(
        {
            "user_id": models.CharField(max_length=200),
            "pin": models.IntegerField()
        }
    )
    transactions = models.JSONField([])


class Transition(models.Model):
    _id = models.ObjectIdField()
    condition = models.JSONField(
        [
            {
                "from_id": models.CharField(max_length=200, null=True),
                "field_id": models.CharField(max_length=200),
                "operator": models.CharField(max_length=200),
                "value": [models.BooleanField(), models.FloatField()]
            }
        ]
    )
    target = models.CharField(max_length=200)


class Workflow(models.Model):
    _id = models.ObjectIdField()
    steps = models.JSONField(
        [
            {
                "id": models.CharField(max_length=200),
                "params": models.JSONField({}),
                "action": models.CharField(max_length=200),
                "transitions": models.ArrayField(model_container=Transition)
            }
        ]
    )
    trigger = models.JSONField(
        {
            "id": models.CharField(max_length=200),
            "params": models.JSONField({}),
            "transitions": models.ArrayField(model_container=Transition)
        }
    )

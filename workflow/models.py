from djongo import models


class Article(models.Model):
    _id = models.ObjectIdField()
    user_id = models.CharField(max_length=50)
    pin = models.IntegerField()

from django.db import models

class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=50)

    class Meta:
        db_table = 'admin'
        managed = False

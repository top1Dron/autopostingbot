from tortoise import Tortoise, fields, run_async
from tortoise.models import Model


class Chat(Model):
    id = fields.BigIntField(pk=True)
    title = fields.TextField(null=True)
    invite_link = fields.CharField(max_length=100)
    type = fields.CharField(max_length=100)

    class Meta:
        table = "chat"

    def __str__(self):
        return self.name


class MessageQueue(Model):
    id = fields.IntField(pk=True)
    chat = fields.ForeignKeyField('models.Chat', related_name='messages')
    text = fields.TextField()


class FrequencyPosting(Model):
    id = fields.IntField(pk=True)
    chat = fields.ForeignKeyField('models.Chat', related_name='frequency')
    type = fields.CharField(max_length=20)
    count_time = fields.IntField(null=True)
    type_time = fields.CharField(max_length=20, null=True)
    day_of_week = fields.CharField(max_length=15, null=True)
    day_of_month = fields.IntField(null=True)


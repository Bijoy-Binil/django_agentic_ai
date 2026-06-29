from django.contrib import admin
from support.models import Conversation,AgentLog,Message
# Register your models here.
admin.site.register(Conversation)
admin.site.register(AgentLog)
admin.site.register(Message)
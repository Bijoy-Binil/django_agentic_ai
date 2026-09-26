from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from support.models import Conversation,AgentLog,Message
# Register your models here.


class MessageInline(admin.TabularInline):
    model=Message
    fields=["role","content","created_at"]
    readonly_fields=["role","content","created_at"]
    ordering=["created_at"]
    extra=0
    can_delete=False
    show_change_link=True


class AgentLogInline(admin.TabularInline):
    model=AgentLog
    fields=["event_type","message","created_at"]
    readonly_fields=["event_type","message","created_at"]
    ordering=["created_at"]
    extra=0
    can_delete=False
    classes=["collapse"]


class ConversationAdmin(admin.ModelAdmin):
    list_display=["id","user","order","message_count","created_at"]
    list_filter=["created_at","user"]
    search_fields=["user__username","order__id"]
    date_hierarchy="created_at"
    inlines=[MessageInline,AgentLogInline]

    def get_queryset(self,request):
        return super().get_queryset(request).annotate(num_messages=Count("message"))

    @admin.display(description="Messages",ordering="num_messages")
    def message_count(self,obj):
        return obj.num_messages


class MessageAdmin(admin.ModelAdmin):
    list_display=["conversation","role_badge","short_content","created_at"]
    list_display_links=["short_content"]
    list_filter=["role","conversation"]
    search_fields=["content","conversation__user__username"]
    list_select_related=["conversation__user","conversation__order"]
    ordering=["conversation","created_at"]

    @admin.display(description="Role",ordering="role")
    def role_badge(self,obj):
        color="#2e7d32" if obj.role=="user" else "#1565c0"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;">{}</span>',
            color,obj.get_role_display(),
        )

    @admin.display(description="Message")
    def short_content(self,obj):
        return obj.content if len(obj.content)<=80 else obj.content[:80]+"..."


class AgentLogAdmin(admin.ModelAdmin):
    list_display=["conversation","event_type","message","created_at"]
    list_filter=["event_type","conversation"]
    list_select_related=["conversation__user","conversation__order"]
    ordering=["conversation","created_at"]


admin.site.register(Conversation,ConversationAdmin)
admin.site.register(AgentLog,AgentLogAdmin)
admin.site.register(Message,MessageAdmin)

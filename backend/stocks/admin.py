from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, StockInfo, StockConcept, StockConceptRel,
    StockDailyKline, StockMinuteKline, StockRealtime,
    UserPortfolio, StockFinancial, SelectionTask, TaskDetail, OperationLog, SysConfig
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'status', 'is_staff', 'date_joined']
    list_filter = ['role', 'status', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone')}),
        ('Permissions', {'fields': ('role', 'status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(StockInfo)
class StockInfoAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'industry', 'sector', 'status', 'list_date', 'created_at']
    list_filter = ['industry', 'sector', 'status']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(StockConcept)
class StockConceptAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(StockConceptRel)
class StockConceptRelAdmin(admin.ModelAdmin):
    list_display = ['stock', 'concept']
    list_filter = ['concept']
    search_fields = ['stock__code', 'stock__name', 'concept__name']


@admin.register(StockDailyKline)
class StockDailyKlineAdmin(admin.ModelAdmin):
    list_display = ['code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'change_pct']
    list_filter = ['code', 'trade_date']
    search_fields = ['code__code', 'code__name']
    date_hierarchy = 'trade_date'
    ordering = ['-trade_date']


@admin.register(StockMinuteKline)
class StockMinuteKlineAdmin(admin.ModelAdmin):
    list_display = ['code', 'trade_time', 'period', 'open', 'high', 'low', 'close', 'volume']
    list_filter = ['code', 'period', 'trade_time']
    search_fields = ['code__code', 'code__name']
    ordering = ['-trade_time']


@admin.register(StockRealtime)
class StockRealtimeAdmin(admin.ModelAdmin):
    list_display = ['code', 'price', 'open', 'high', 'low', 'prev_close', 'volume', 'update_time']
    search_fields = ['code__code', 'code__name']
    ordering = ['code']


@admin.register(UserPortfolio)
class UserPortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'shares', 'available_shares', 'cost_price', 'updated_at']
    list_filter = ['user', 'stock']
    search_fields = ['user__username', 'stock__code', 'stock__name']
    ordering = ['-updated_at']


@admin.register(StockFinancial)
class StockFinancialAdmin(admin.ModelAdmin):
    list_display = ['stock', 'report_date', 'report_type', 'revenue', 'net_profit', 'eps', 'roe', 'pe']
    list_filter = ['stock', 'report_type', 'report_date']
    search_fields = ['stock__code', 'stock__name']
    ordering = ['-report_date']


@admin.register(SelectionTask)
class SelectionTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'strategy', 'status', 'created_at', 'started_at', 'finished_at']
    list_filter = ['status', 'strategy']
    search_fields = ['name', 'strategy']
    ordering = ['-created_at']


@admin.register(TaskDetail)
class TaskDetailAdmin(admin.ModelAdmin):
    list_display = ['task', 'stock', 'score', 'reason', 'created_at']
    list_filter = ['task', 'stock']
    search_fields = ['task__name', 'stock__code', 'stock__name']
    ordering = ['-score']


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target', 'ip_addr', 'created_at']
    list_filter = ['action', 'user']
    search_fields = ['user__username', 'action', 'target']
    ordering = ['-created_at']


@admin.register(SysConfig)
class SysConfigAdmin(admin.ModelAdmin):
    list_display = ['config_key', 'description', 'updated_at']
    search_fields = ['config_key', 'description']
    ordering = ['config_key']

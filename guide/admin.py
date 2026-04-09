from django.contrib import admin
from .models import Decision


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'recommendation',
        'industry',
        'priority',
        'complexity',
        'growth',
        'integration',
        'business_size',
        'budget',
        'compliance',
        'created_at',
    )
    list_filter = (
        'priority',
        'complexity',
        'growth',
        'integration',
        'business_size',
        'budget',
        'compliance',
        'created_at',
    )
    search_fields = ('recommendation', 'explanation')

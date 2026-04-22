from django.contrib import admin
from .models import (
    Decision, UserProfile, Industry, Question, QuestionOption,
    ERPSystem, ScoringRule, DecisionThreshold, Analytics, SubscriptionPlan
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'industry',
                    'business_size', 'subscription_plan')
    list_filter = ('industry', 'business_size', 'subscription_plan')


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    fields = ('key', 'label', 'order', 'is_active')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'field_key', 'question_type',
                    'required', 'order', 'is_active')
    list_filter = ('question_type', 'required', 'is_active')
    ordering = ('order',)
    inlines = [QuestionOptionInline]
    fields = ('text', 'field_key', 'question_type',
              'required', 'order', 'is_active')


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'label', 'key', 'order', 'is_active')
    list_filter = ('question', 'is_active')
    ordering = ('question__order', 'order')


@admin.register(ERPSystem)
class ERPSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_filter = ('is_active',)
    ordering = ('order',)
    fields = ('name', 'description', 'focus', 'modules',
              'risks', 'approach', 'is_active', 'order')


class ScoringRuleInline(admin.TabularInline):
    model = ScoringRule
    extra = 1
    fields = ('question_option', 'erp_system', 'score', 'is_active')


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ('question_option', 'erp_system', 'score', 'is_active')
    list_filter = ('erp_system', 'is_active')
    search_fields = ('question_option__question__text',
                     'question_option__label')


@admin.register(DecisionThreshold)
class DecisionThresholdAdmin(admin.ModelAdmin):
    list_display = ('erp_system', 'min_score_advantage', 'is_fallback')
    fields = ('erp_system', 'min_score_advantage', 'is_fallback')


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'recommendation',
                    'confidence_score', 'created_at')
    list_filter = ('industry', 'created_at')
    search_fields = ('user__username', 'company_name', 'recommendation')


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'max_recommendations', 'is_active')
    list_filter = ('is_active',)

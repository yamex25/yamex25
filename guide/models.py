from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=50, blank=True, null=True)
    business_size = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='Uganda')
    subscription_plan = models.CharField(max_length=20, default='free')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.name


class ERPSystem(models.Model):
    """ERP systems available for recommendation"""
    name = models.CharField(
        max_length=100, unique=True)  # e.g., "QuickBooks", "Odoo", "Hybrid Strategy"
    description = models.TextField(blank=True)
    focus = models.TextField(blank=True)  # Strategic focus
    modules = models.TextField(blank=True)  # Recommended modules
    risks = models.TextField(blank=True)  # Primary risks
    approach = models.TextField(blank=True)  # Implementation approach
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Question(models.Model):
    QUESTION_TYPES = [
        ('choice', 'Multiple Choice'),
        ('text', 'Text Input'),
        ('number', 'Number'),
    ]

    text = models.CharField(max_length=255)
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default='choice')
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    industries = models.ManyToManyField(Industry, blank=True)
    is_active = models.BooleanField(default=True)
    field_key = models.CharField(
        max_length=50, blank=True, help_text="Internal field name (priority, complexity, etc.)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text

    def get_options_dict(self):
        """Return options as a dictionary for the questionnaire"""
        options = {}
        for opt in self.questionoption_set.filter(is_active=True).order_by('order'):
            options[opt.key] = opt.label
        return options


class QuestionOption(models.Model):
    """Database-driven question options - replaces hardcoded options"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)  # Internal value
    label = models.CharField(max_length=255)  # Display label
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ['question', 'key']

    def __str__(self):
        return f"{self.question.text} - {self.label}"


class ScoringRule(models.Model):
    """Database-driven scoring rules: which answer option leads to which ERP system"""
    question_option = models.ForeignKey(
        QuestionOption, on_delete=models.CASCADE)
    erp_system = models.ForeignKey(ERPSystem, on_delete=models.CASCADE)
    score = models.IntegerField(
        default=1, help_text="Weight/score for this option towards this system")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['question_option', 'erp_system']

    def __str__(self):
        return f"{self.question_option.question.field_key}={self.question_option.key} → {self.erp_system.name} (+{self.score})"


class DecisionThreshold(models.Model):
    """Thresholds that determine when to recommend a system"""
    erp_system = models.OneToOneField(ERPSystem, on_delete=models.CASCADE)
    min_score_advantage = models.IntegerField(
        default=4,
        help_text="Minimum score difference needed to recommend this system (e.g., Odoo must lead by 4 points)"
    )
    is_fallback = models.BooleanField(
        default=False,
        help_text="Use this system as fallback when scores are close (e.g., Hybrid Strategy)"
    )

    def __str__(self):
        return f"{self.erp_system.name} - Threshold: +{self.min_score_advantage}"


class Decision(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=120, blank=True)
    industry = models.ForeignKey(
        Industry, on_delete=models.SET_NULL, null=True, blank=True)
    answers = models.JSONField(default=dict)  # Store all answers
    recommendation = models.CharField(max_length=120)
    explanation = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ANSWER_LABELS = {
        'priority': {
            'accounting': 'Financial control and reporting',
            'mixed': 'Finance + operations oversight',
            'operations': 'End-to-end operations and growth',
        },
        'complexity': {
            'low': 'Standard accounting workflows',
            'medium': 'Integrated finance and operations',
            'high': 'Complex cross-functional processes',
        },
        'growth': {
            'stable': 'Stable with predictable demand',
            'growing': 'Steady expansion',
            'scaling': 'Rapid scaling and new markets',
        },
        'integration': {
            'low': 'Accounting only',
            'medium': 'Finance plus sales or inventory',
            'high': 'Multi-team operational workflows',
        },
        'industry': {
            'services': 'Professional services',
            'trade': 'Retail / trade',
            'manufacturing': 'Manufacturing / production',
            'agriculture': 'Agriculture / agro-trade',
            'hospitality': 'Hospitality / tourism',
        },
        'business_size': {
            'small': 'Small / emerging entity',
            'medium': 'Mid-market organisation',
            'large': 'Large / complex enterprise',
        },
        'budget': {
            'rapid': 'Fast launch with tight budget',
            'balanced': 'Balanced cost and delivery',
            'strategic': 'Strategic transformation investment',
        },
        'compliance': {
            'standard': 'Single-country compliance',
            'regional': 'Regional or multi-office',
            'global': 'Global / multi-entity',
        },
    }

    def _get_answer_display(self, key):
        value = self.answers.get(key)
        if not value:
            return 'Not specified'
        if key == 'industry' and self.industry:
            return self.industry.name
        return self.ANSWER_LABELS.get(key, {}).get(value, str(value))

    def get_priority_display(self):
        return self._get_answer_display('priority')

    def get_complexity_display(self):
        return self._get_answer_display('complexity')

    def get_growth_display(self):
        return self._get_answer_display('growth')

    def get_integration_display(self):
        return self._get_answer_display('integration')

    def get_business_size_display(self):
        return self._get_answer_display('business_size')

    def get_budget_display(self):
        return self._get_answer_display('budget')

    def get_compliance_display(self):
        return self._get_answer_display('compliance')

    def get_industry_display(self):
        return self._get_answer_display('industry')

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.recommendation}"


class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # e.g., 'generated_recommendation', 'viewed_report'
    action = models.CharField(max_length=100)
    data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()  # List of features
    max_recommendations = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

from django.db import models


class Decision(models.Model):
    PRIORITY_CHOICES = [
        ('accounting', 'Accounting Focus'),
        ('mixed', 'Finance + Operations'),
        ('operations', 'Full Operations'),
    ]

    COMPLEXITY_CHOICES = [
        ('low', 'Simple'),
        ('medium', 'Moderate'),
        ('high', 'Complex'),
    ]

    GROWTH_CHOICES = [
        ('stable', 'Stable'),
        ('growing', 'Growing'),
        ('scaling', 'Scaling'),
    ]

    INTEGRATION_CHOICES = [
        ('low', 'Minimal'),
        ('medium', 'Moderate'),
        ('high', 'High Integration'),
    ]

    INDUSTRY_CHOICES = [
        ('services', 'Professional Services'),
        ('trade', 'Retail / Trade'),
        ('manufacturing', 'Manufacturing / Production'),
        ('agriculture', 'Agriculture / Agro-trade'),
        ('hospitality', 'Hospitality / Tourism'),
    ]

    BUSINESS_SIZE_CHOICES = [
        ('small', 'Small / Emerging'),
        ('medium', 'Mid-market'),
        ('large', 'Large / Complex'),
    ]

    BUDGET_CHOICES = [
        ('rapid', 'Fast launch / constrained budget'),
        ('balanced', 'Balanced cost and timeline'),
        ('strategic', 'Strategic investment / transformation'),
    ]

    COMPLIANCE_CHOICES = [
        ('standard', 'Standard local compliance'),
        ('regional', 'Regional or multi-office'),
        ('global', 'Global / multi-entity compliance'),
    ]

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES)
    growth = models.CharField(max_length=20, choices=GROWTH_CHOICES)
    integration = models.CharField(max_length=20, choices=INTEGRATION_CHOICES)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    business_size = models.CharField(max_length=20, choices=BUSINESS_SIZE_CHOICES)
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    compliance = models.CharField(max_length=20, choices=COMPLIANCE_CHOICES)
    company_name = models.CharField(max_length=120, blank=True, default='')

    recommendation = models.CharField(max_length=120)
    explanation = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.recommendation

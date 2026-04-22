from guide.models import Question

# Define questions with their options
questions_data = [
    {
        'text': '1. Business priority',
        'options': {
            'accounting': 'Financial control and reporting',
            'mixed': 'Finance + operations oversight',
            'operations': 'End-to-end operations and growth',
        },
        'order': 1,
        'key': 'priority'
    },
    {
        'text': '2. Process complexity',
        'options': {
            'low': 'Standard accounting workflows',
            'medium': 'Integrated finance and operations',
            'high': 'Complex cross-functional processes',
        },
        'order': 2,
        'key': 'complexity'
    },
    {
        'text': '3. Growth trajectory',
        'options': {
            'stable': 'Stable with predictable demand',
            'growing': 'Steady expansion',
            'scaling': 'Rapid scaling and new markets',
        },
        'order': 3,
        'key': 'growth'
    },
    {
        'text': '4. Integration requirement',
        'options': {
            'low': 'Accounting only',
            'medium': 'Finance plus sales or inventory',
            'high': 'Multi-team operational workflows',
        },
        'order': 4,
        'key': 'integration'
    },
    {
        'text': '5. Industry sector',
        'options': {
            'services': 'Professional services',
            'trade': 'Retail / trade',
            'manufacturing': 'Manufacturing / production',
            'agriculture': 'Agriculture / agro-trade',
            'hospitality': 'Hospitality / tourism',
        },
        'order': 5,
        'key': 'industry'
    },
    {
        'text': '6. Business size',
        'options': {
            'small': 'Small / emerging entity',
            'medium': 'Mid-market organisation',
            'large': 'Large / complex enterprise',
        },
        'order': 6,
        'key': 'business_size'
    },
    {
        'text': '7. Budget & timeline',
        'options': {
            'rapid': 'Fast launch with tight budget',
            'balanced': 'Balanced cost and delivery',
            'strategic': 'Strategic transformation investment',
        },
        'order': 7,
        'key': 'budget'
    },
    {
        'text': '8. Compliance scope',
        'options': {
            'standard': 'Single-country compliance',
            'regional': 'Regional or multi-office',
            'global': 'Global / multi-entity',
        },
        'order': 8,
        'key': 'compliance'
    },
]

for q_data in questions_data:
    Question.objects.get_or_create(
        text=q_data['text'],
        defaults={
            'question_type': 'choice',
            'options': q_data['options'],
            'order': q_data['order'],
            'required': True,
            'is_active': True,
        }
    )
    print(f"✓ Created: {q_data['text']}")

print("\n✅ All default questions created successfully!")

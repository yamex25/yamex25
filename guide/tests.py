import json

from django.test import Client, TestCase
from django.urls import reverse

from .decision_guide import evaluate_answers
from .models import Decision


class DecisionGuideTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_payload = {
            'priority': 'mixed',
            'complexity': 'medium',
            'growth': 'growing',
            'integration': 'medium',
            'industry': 'trade',
            'business_size': 'medium',
            'budget': 'balanced',
            'compliance': 'regional',
            'company_name': 'Uganda Ventures Ltd',
        }

    def test_evaluate_answers_returns_hybrid_for_moderate_inputs(self):
        result = evaluate_answers(self.valid_payload)
        self.assertIn(result['system'], ['Hybrid Strategy', 'Hybrid Approach'])
        self.assertIn('Implementation', result['approach'] if 'approach' in result else '')

    def test_evaluate_view_creates_decision(self):
        response = self.client.post(
            reverse('evaluate'),
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decision.objects.count(), 1)
        decision = Decision.objects.first()
        self.assertEqual(decision.priority, 'mixed')
        self.assertEqual(decision.business_size, 'medium')
        self.assertEqual(decision.industry, 'trade')
        self.assertEqual(decision.company_name, 'Uganda Ventures Ltd')
        self.assertEqual(decision.recommendation, response.json()['system'])

    def test_evaluate_view_requires_all_fields(self):
        response = self.client.post(
            reverse('evaluate'),
            data=json.dumps({'priority': 'accounting'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('missing', response.json())

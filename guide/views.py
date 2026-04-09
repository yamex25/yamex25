# from django.shortcuts import render
# from django.http import JsonResponse
# import json
# from .decision_guide import evaluate_answers


# def index(request):
#     return render(request, 'index.html')


# def evaluate(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         answers = data.get("answers")

#         result = evaluate_answers(answers)

#         return JsonResponse({"recommendation": result})


from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
import json

from .models import Decision
from .decision_guide import evaluate_answers


@ensure_csrf_cookie
def index(request):
    recent = Decision.objects.order_by('-created_at')[:5]
    return render(request, "index.html", {'recent': recent})


def history(request):
    company_query = request.GET.get('company', '').strip()
    recommendation_query = request.GET.get('recommendation', '').strip()

    decisions = Decision.objects.order_by('-created_at')
    if company_query:
        decisions = decisions.filter(company_name__icontains=company_query)
    if recommendation_query:
        decisions = decisions.filter(recommendation__icontains=recommendation_query)

    decisions = decisions[:50]
    return render(request, "history.html", {
        'decisions': decisions,
        'company_query': company_query,
        'recommendation_query': recommendation_query,
    })


def printable_report(request, decision_id):
    decision = Decision.objects.filter(id=decision_id).first()
    if not decision:
        return render(request, 'report.html', {
            'error': 'The requested report was not found.',
            'decision': None,
        })

    return render(request, 'report.html', {'decision': decision})


def user_logout(request):
    auth_logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    recent = Decision.objects.order_by('-created_at')[:10]
    totals = {
        'total': Decision.objects.count(),
        'odoo': Decision.objects.filter(recommendation__icontains='Odoo').count(),
        'quickbooks': Decision.objects.filter(recommendation__icontains='QuickBooks').count(),
        'hybrid': Decision.objects.filter(recommendation__icontains='Hybrid').count(),
    }

    industry_stats = Decision.objects.values('industry').annotate(count=Count('id')).order_by('-count')
    compliance_stats = Decision.objects.values('compliance').annotate(count=Count('id')).order_by('-count')
    top_industry = industry_stats[0] if industry_stats else None
    top_compliance = compliance_stats[0] if compliance_stats else None
    label_map = dict(Decision.INDUSTRY_CHOICES)
    compliance_map = dict(Decision.COMPLIANCE_CHOICES)

    top_recommendation = 'Hybrid Strategy'
    if totals['odoo'] >= totals['quickbooks'] and totals['odoo'] >= totals['hybrid']:
        top_recommendation = 'Odoo ERP'
    elif totals['quickbooks'] >= totals['odoo'] and totals['quickbooks'] >= totals['hybrid']:
        top_recommendation = 'QuickBooks Online'

    report = {
        'top_industry_label': label_map.get(top_industry['industry']) if top_industry else 'N/A',
        'top_industry_count': top_industry['count'] if top_industry else 0,
        'top_compliance_label': compliance_map.get(top_compliance['compliance']) if top_compliance else 'N/A',
        'top_compliance_count': top_compliance['count'] if top_compliance else 0,
        'top_recommendation': top_recommendation,
        'local_message': 'Ugandan businesses are prioritising systems that support compliance, budgeting and operational scalability.',
    }

    return render(request, 'dashboard.html', {'recent': recent, 'totals': totals, 'report': report})


@require_POST
def evaluate(request):
    try:
        data = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    required_fields = ['priority', 'complexity', 'growth', 'integration', 'business_size', 'budget', 'compliance', 'industry']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return JsonResponse({
            'error': 'Please answer all questions before submitting.',
            'missing': missing,
        }, status=400)

    result = evaluate_answers(data)
    decision = Decision.objects.create(
        priority=data.get('priority'),
        complexity=data.get('complexity'),
        growth=data.get('growth'),
        integration=data.get('integration'),
        industry=data.get('industry'),
        business_size=data.get('business_size'),
        budget=data.get('budget'),
        compliance=data.get('compliance'),
        company_name=data.get('company_name', ''),
        recommendation=result['system'],
        explanation=result['explanation'],
    )

    response = result.copy()
    response['saved_at'] = decision.created_at.isoformat()
    response['decision_id'] = decision.id
    return JsonResponse(response)

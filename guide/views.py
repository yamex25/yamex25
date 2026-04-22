from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import json

# Optional: ReportLab for PDF generation
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from .models import Decision, Analytics, Industry, Question
from .decision_guide import evaluate_answers
from .forms import UserProfileForm, UserUpdateForm
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import DecisionSerializer, IndustrySerializer, QuestionSerializer


@ensure_csrf_cookie
def index(request):
    # Auto-create industries if none exist
    if Industry.objects.count() == 0:
        industries_list = [
            'Professional Services',
            'Retail & Trade',
            'Manufacturing',
            'Agriculture & Agro-trade',
            'Hospitality & Tourism',
            'Healthcare',
            'Education',
            'Construction',
            'Technology',
            'Transportation & Logistics',
        ]
        for name in industries_list:
            Industry.objects.get_or_create(
                name=name, defaults={'is_active': True})

    # Auto-create questions and options if none exist
    if Question.objects.count() == 0:
        questions_data = [
            {
                'text': '1. Business priority',
                'options': {
                    'accounting': 'Financial control and reporting',
                    'mixed': 'Finance + operations oversight',
                    'operations': 'End-to-end operations and growth',
                }
            },
            {
                'text': '2. Process complexity',
                'options': {
                    'low': 'Standard accounting workflows',
                    'medium': 'Integrated finance and operations',
                    'high': 'Complex cross-functional processes',
                }
            },
            {
                'text': '3. Growth trajectory',
                'options': {
                    'stable': 'Stable with predictable demand',
                    'growing': 'Steady expansion',
                    'scaling': 'Rapid scaling and new markets',
                }
            },
            {
                'text': '4. Integration requirement',
                'options': {
                    'low': 'Accounting only',
                    'medium': 'Finance plus sales or inventory',
                    'high': 'Multi-team operational workflows',
                }
            },
            {
                'text': '5. Industry sector',
                'options': {}  # Will be populated from Industry model
            },
            {
                'text': '6. Business size',
                'options': {
                    'small': 'Small / emerging entity',
                    'medium': 'Mid-market organisation',
                    'large': 'Large / complex enterprise',
                }
            },
            {
                'text': '7. Budget & timeline',
                'options': {
                    'rapid': 'Fast launch with tight budget',
                    'balanced': 'Balanced cost and delivery',
                    'strategic': 'Strategic transformation investment',
                }
            },
            {
                'text': '8. Compliance scope',
                'options': {
                    'standard': 'Single-country compliance',
                    'regional': 'Regional or multi-office',
                    'global': 'Global / multi-entity',
                }
            },
        ]

        from .models import QuestionOption
        for order, q_data in enumerate(questions_data, 1):
            q, created = Question.objects.get_or_create(
                text=q_data['text'],
                defaults={
                    'question_type': 'choice',
                    'order': order,
                    'required': True,
                    'is_active': True,
                }
            )

            # Create QuestionOptions for this question
            if created:
                if '5. Industry sector' in q_data['text']:
                    # For industry, pull from Industry model
                    for ind in Industry.objects.filter(is_active=True):
                        QuestionOption.objects.get_or_create(
                            question=q,
                            key=ind.name,
                            defaults={
                                'label': ind.name,
                                'is_active': True,
                            }
                        )
                else:
                    # For other questions, create from hardcoded data (this is the only time we use it)
                    for opt_order, (key, label) in enumerate(q_data['options'].items(), 1):
                        QuestionOption.objects.get_or_create(
                            question=q,
                            key=key,
                            defaults={
                                'label': label,
                                'order': opt_order,
                                'is_active': True,
                            }
                        )

    recent = Decision.objects.filter(user__isnull=False).order_by(
        '-created_at')[:5] if request.user.is_authenticated else None
    questions = Question.objects.filter(is_active=True).order_by('order')

    # Map question text to field names
    key_map = {
        'business priority': 'priority',
        'process complexity': 'complexity',
        'growth trajectory': 'growth',
        'integration requirement': 'integration',
        'industry sector': 'industry',
        'business size': 'business_size',
        'budget': 'budget',
        'compliance': 'compliance',
    }

    questions_json = []
    for q in questions:
        # Extract field name from question text
        q_lower = q.text.lower()
        field_key = None
        for pattern, key in key_map.items():
            if pattern in q_lower:
                field_key = key
                break

        if not field_key:
            continue

        # Get options from database (QuestionOption model)
        options = q.get_options_dict()

        questions_json.append({
            'id': q.id,
            'text': q.text,
            'field_key': field_key,
            'type': 'choice',
            'options': options,
            'required': q.required,
        })

    # Pre-fill company name from profile if available
    company_name = ''
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        company_name = request.user.userprofile.company_name or ''

    return render(request, "index.html", {
        'recent': recent,
        'questions': questions_json,
        'questions_json': json.dumps(questions_json),
        'company_name': company_name,
    })


@login_required
def history(request):
    user_decisions = Decision.objects.filter(user=request.user)
    company_query = request.GET.get('company', '').strip()
    recommendation_query = request.GET.get('recommendation', '').strip()

    if company_query:
        user_decisions = user_decisions.filter(
            company_name__icontains=company_query)
    if recommendation_query:
        user_decisions = user_decisions.filter(
            recommendation__icontains=recommendation_query)

    decisions = user_decisions.order_by('-created_at')[:50]
    return render(request, "history.html", {
        'decisions': decisions,
        'company_query': company_query,
        'recommendation_query': recommendation_query,
    })


@login_required
def printable_report(request, decision_id):
    decision = Decision.objects.filter(
        id=decision_id, user=request.user).first()
    if not decision:
        return render(request, 'report.html', {
            'error': 'The requested report was not found.',
            'decision': None,
        })

    return render(request, 'report.html', {'decision': decision})


@login_required
def download_pdf(request, decision_id):
    decision = Decision.objects.filter(
        id=decision_id, user=request.user).first()
    if not decision:
        return HttpResponse('Report not found', status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="erp_recommendation_{decision_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph(f"ERP Recommendation Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Company
    if decision.company_name:
        company = Paragraph(
            f"Company: {decision.company_name}", styles['Normal'])
        story.append(company)
        story.append(Spacer(1, 12))

    # Recommendation
    rec = Paragraph(
        f"Recommended System: {decision.recommendation}", styles['Heading2'])
    story.append(rec)
    story.append(Spacer(1, 12))

    # Explanation
    exp = Paragraph(decision.explanation, styles['Normal'])
    story.append(exp)
    story.append(Spacer(1, 12))

    # Answers
    answers_title = Paragraph("Your Answers:", styles['Heading3'])
    story.append(answers_title)
    for key, value in decision.answers.items():
        ans = Paragraph(f"{key}: {value}", styles['Normal'])
        story.append(ans)

    doc.build(story)
    return response


# API Views
class DecisionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DecisionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Decision.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IndustryListAPIView(generics.ListAPIView):
    queryset = Industry.objects.filter(is_active=True)
    serializer_class = IndustrySerializer
    permission_classes = [permissions.AllowAny]


class QuestionListAPIView(generics.ListAPIView):
    queryset = Question.objects.filter(is_active=True)
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_evaluate(request):
    data = request.data
    required_fields = ['priority', 'complexity', 'growth',
                       'integration', 'business_size', 'budget', 'compliance', 'industry']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return Response({
            'error': 'Please answer all questions before submitting.',
            'missing': missing,
        }, status=400)

    result = evaluate_answers(data)
    decision = Decision.objects.create(
        user=request.user,
        company_name=data.get('company_name', ''),
        answers=data,
        recommendation=result['system'],
        explanation=result['explanation'],
        confidence_score=result.get('confidence', 0.0),
    )

    serializer = DecisionSerializer(decision)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_evaluate_anonymous(request):
    # Remove CSRF check for anonymous users
    from django.views.decorators.csrf import csrf_exempt
    from django.utils.decorators import method_decorator

    data = request.data
    required_fields = ['priority', 'complexity', 'growth',
                       'integration', 'business_size', 'budget', 'compliance', 'industry']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return Response({
            'error': 'Please answer all questions before submitting.',
            'missing': missing,
        }, status=400)

    result = evaluate_answers(data)

    # Don't save to database for anonymous users
    response = result.copy()
    response['anonymous'] = True
    response['message'] = 'This is a preview. Sign up to save your recommendations and get personalized insights.'
    return Response(response)


def user_logout(request):
    auth_logout(request)
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(
                request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/signup.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def dashboard(request):
    user_decisions = Decision.objects.filter(user=request.user)
    recent = user_decisions.order_by('-created_at')[:10]
    totals = {
        'total': user_decisions.count(),
        'odoo': user_decisions.filter(recommendation__icontains='Odoo').count(),
        'quickbooks': user_decisions.filter(recommendation__icontains='QuickBooks').count(),
        'hybrid': user_decisions.filter(recommendation__icontains='Hybrid').count(),
    }

    industry_stats = user_decisions.values('industry__name').annotate(
        count=Count('id')).order_by('-count')
    top_industry = industry_stats[0] if industry_stats else None

    # For compliance, since it's in answers JSON, need to aggregate differently
    compliance_counts = {}
    for decision in user_decisions:
        compliance = decision.answers.get('compliance')
        if compliance:
            compliance_counts[compliance] = compliance_counts.get(
                compliance, 0) + 1
    top_compliance = max(
        compliance_counts, key=compliance_counts.get) if compliance_counts else None

    compliance_map = {
        'standard': 'Standard local compliance',
        'regional': 'Regional or multi-office',
        'global': 'Global / multi-entity compliance',
    }

    top_recommendation = 'Hybrid Strategy'
    if totals['odoo'] >= totals['quickbooks'] and totals['odoo'] >= totals['hybrid']:
        top_recommendation = 'Odoo ERP'
    elif totals['quickbooks'] >= totals['odoo'] and totals['quickbooks'] >= totals['hybrid']:
        top_recommendation = 'QuickBooks Online'

    report = {
        'top_industry_label': top_industry['industry__name'] if top_industry else 'N/A',
        'top_industry_count': top_industry['count'] if top_industry else 0,
        'top_compliance_label': compliance_map.get(top_compliance, 'N/A') if top_compliance else 'N/A',
        'top_compliance_count': compliance_counts.get(top_compliance, 0) if top_compliance else 0,
        'top_recommendation': top_recommendation,
        'local_message': 'Your business decisions are shaping the future of ERP adoption.',
    }

    return render(request, 'dashboard.html', {'recent': recent, 'totals': totals, 'report': report})


@require_POST
@login_required
def evaluate(request):
    try:
        data = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    required_fields = ['priority', 'complexity', 'growth',
                       'integration', 'business_size', 'budget', 'compliance', 'industry']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return JsonResponse({
            'error': 'Please answer all questions before submitting.',
            'missing': missing,
        }, status=400)

    result = evaluate_answers(data)
    decision = Decision.objects.create(
        user=request.user,
        company_name=data.get('company_name', ''),
        answers=data,  # Store all answers as JSON
        recommendation=result['system'],
        explanation=result['explanation'],
        confidence_score=result.get('confidence', 0.0),
    )

    # Log analytics
    Analytics.objects.create(user=request.user, action='generated_recommendation', data={
                             'decision_id': decision.id})

    response = result.copy()
    response['saved_at'] = decision.created_at.isoformat()
    response['decision_id'] = decision.id
    return JsonResponse(response)

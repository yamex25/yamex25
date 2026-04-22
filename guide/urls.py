from django.urls import path
from .views import (
    index, evaluate, history, dashboard, printable_report, user_logout, signup, profile, download_pdf,
    DecisionListCreateAPIView, IndustryListAPIView, QuestionListAPIView, api_evaluate, api_evaluate_anonymous
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('report/<int:decision_id>/', printable_report, name='printable_report'),
    path('report/<int:decision_id>/pdf/', download_pdf, name='download_pdf'),
    path('evaluate/', evaluate, name='evaluate'),
    path('history/', history, name='history'),
    path('logout/', user_logout, name='user_logout'),
    path('signup/', signup, name='signup'),
    path('profile/', profile, name='profile'),
    # API
    path('api/decisions/', DecisionListCreateAPIView.as_view(), name='api_decisions'),
    path('api/industries/', IndustryListAPIView.as_view(), name='api_industries'),
    path('api/questions/', QuestionListAPIView.as_view(), name='api_questions'),
    path('api/evaluate/', api_evaluate, name='api_evaluate'),
    path('api/evaluate-anonymous/', api_evaluate_anonymous,
         name='api_evaluate_anonymous'),
]

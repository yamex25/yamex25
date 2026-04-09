from django.urls import path
from .views import index, evaluate, history, dashboard, printable_report, user_logout

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('report/<int:decision_id>/', printable_report, name='printable_report'),
    path('evaluate/', evaluate, name='evaluate'),
    path('history/', history, name='history'),
    path('logout/', user_logout, name='user_logout'),
]

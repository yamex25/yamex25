from rest_framework import serializers
from .models import Decision, UserProfile, Industry, Question, Analytics

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    industries = IndustrySerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

class DecisionSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source='industry.name', read_only=True)

    class Meta:
        model = Decision
        fields = ['id', 'company_name', 'industry', 'industry_name', 'answers', 'recommendation', 'explanation', 'confidence_score', 'created_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = '__all__'
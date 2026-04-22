from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Industry, QuestionOption


class UserProfileForm(forms.ModelForm):
    industry = forms.ModelChoiceField(
        queryset=Industry.objects.filter(is_active=True),
        empty_label="Select Industry",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically build business_size choices from database
        # Get the "6. Business size" question options
        from .models import Question
        try:
            size_question = Question.objects.get(text='6. Business size')
            size_options = QuestionOption.objects.filter(
                question=size_question,
                is_active=True
            ).order_by('order')

            business_size_choices = [('', 'Select Business Size')]
            for opt in size_options:
                business_size_choices.append((opt.key, opt.label))
        except Question.DoesNotExist:
            # Fallback if question doesn't exist
            business_size_choices = [
                ('', 'Select Business Size'),
                ('small', 'Small / Emerging'),
                ('medium', 'Mid-market'),
                ('large', 'Large / Complex'),
            ]

        self.fields['business_size'] = forms.ChoiceField(
            choices=business_size_choices,
            required=False
        )

    class Meta:
        model = UserProfile
        fields = ['company_name', 'industry',
                  'business_size', 'role', 'phone', 'country']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

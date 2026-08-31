from django import forms
from .models import EnquiryData, EnquiryStatus


class EnquiryDataForm(forms.ModelForm):
    class Meta:
        model = EnquiryData
        fields = ['name', 'phone_number', 'email', 'age', 'status', 'conversion', 
                 'last_follow_up_date', 'next_follow_up_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter age'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'conversion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class EnquiryStatusForm(forms.ModelForm):
    class Meta:
        model = EnquiryStatus
        fields = ['description', 'status', 'call_status']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Enter follow-up description...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'call_status': forms.Select(attrs={'class': 'form-control'}),
        }


class EnquiryFilterForm(forms.Form):
    CONVERSION_CHOICES = [
        ('', 'All'),
        ('False', 'Not Converted'),
        ('True', 'Converted'),
    ]
    
    STATUS_CHOICES = [('', 'All Status')] + EnquiryData.STATUS_CHOICES
    
    conversion = forms.ChoiceField(
        choices=CONVERSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, phone, or email...'
        })
    )
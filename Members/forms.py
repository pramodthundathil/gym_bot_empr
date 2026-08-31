from django.forms import ModelForm, TextInput, Textarea, FileInput, Select
from .models import MemberData, Subscription, Batch_DB, Subscription_Period, TypeSubsription, Payment
from datetime import datetime

date =  str(datetime.now()).split(" ")[0]


class MemberAddForm(ModelForm):
    class Meta:
        model = MemberData
        fields = [
            "First_Name",
            "Last_Name",
            "Date_Of_Birth",
            "Gender",
            "Mobile_Number",
            "Email",
            "Registration_Date",
            "Access_Token_Id",
            "Photo",
            "Id_Upload",
            "Address",
            "Medical_History",
        ]

        widgets = {
            "First_Name":TextInput(attrs={"class":"form-control"}),
            "Last_Name":TextInput(attrs={"class":"form-control"}),
            "Date_Of_Birth":TextInput(attrs={"class":"form-control","type":"date","max":date}),
            "Gender":Select(attrs={"class":"form-control"}),
            # "Date_Of_Birth":TextInput(attrs={"class":"form-control","type":"date","min":date}),
            "Mobile_Number":TextInput(attrs={"class":"form-control","type":"number"}),
            "Email":TextInput(attrs={"class":"form-control","type":"email"}),
            "Registration_Date":TextInput(attrs={"class":"form-control","type":"date"}),
            # "Address":TextInput(attrs={"class":"form-control",'style': 'height: 3em !importent;'}),
            # "Medical_History":TextInput(attrs={"class":"form-control"}),
            "Photo":FileInput(attrs={"class":"form-control",'accept': 'image/*', 'capture':'camera', "id":"profilePic"}),
            "Id_Upload":FileInput(attrs={"class":"form-control",'accept': 'image/*', 'capture':'camera'}),
            "Access_Token_Id":TextInput(attrs={"class":"form-control"})

        }

class SubscriptionAddForm(ModelForm):
    class Meta:
        model = Subscription
        fields = [
            "Type_Of_Subscription",
            "Period_Of_Subscription",
            "Amount",
            "Subscribed_Date",
            # "Subscription_End_Date",
            "Batch",
        ]

        widgets = {
            "Type_Of_Subscription":Select(attrs={"class":"form-control","required":"required"}),
            "Period_Of_Subscription":Select(attrs={"class":"form-control","required":"required"}),
            "Amount":TextInput(attrs={"class":"form-control","type":"number"}),
            "Subscribed_Date":TextInput(attrs={"class":"form-control","type":"date"}),
            # "Subscription_End_Date":TextInput(attrs={"class":"form-control","type":"date","min":date}),
            "Batch":Select(attrs={"class":"form-control","required":"required"}),

        }

class BatchForm(ModelForm):
    class Meta:
        model = Batch_DB
        fields = ["Batch_Name","Batch_Time"]

        widgets = {
            "Batch_Name":Select(attrs={"class":"form-control"}),
            "Batch_Time":TextInput(attrs={"class":"form-control",'type':"time"}),
        }

class Subscription_PeriodForm(ModelForm):
    class Meta:
        model = Subscription_Period
        fields = ["Period","Category"]

        widgets = {
            "Period":TextInput(attrs={"class":"form-control","type":"number"}),
            "Category":Select(attrs={"class":"form-control"}),
        }

class TypeSubsriptionForm(ModelForm):
    class Meta:
        model = TypeSubsription
        fields = ["Type"]
        widgets = {
           
            "Type":TextInput(attrs={"class":"form-control"}),

        }

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ["Member", "Payment_Date","Mode_of_Payment"]

        widgets = {

            "Member":Select(attrs={"class":"form-control"}),
            "Amount":TextInput(attrs={"class":"form-control","type":"number"}),
            "Payment_Date":TextInput(attrs={"class":"form-control","type":"date"}),
            "Mode_of_Payment":Select(attrs={"class":"form-control"})
        }



from django import forms
from .models import MemberData

class MemberBulkUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select Excel file',
        help_text='Upload an Excel file (.xlsx) containing member data'
    )


class MemberAddQuickForm(ModelForm):
    class Meta:
        model = MemberData
        fields = [
            "First_Name",
            "Gender",
            "Mobile_Number",    
            "Photo",
            "Medical_History",
        ]
        labels = {
            "First_Name": "Full Name",
        }

        widgets = {
            "First_Name":TextInput(attrs={"class":"form-control"}),
            # "Last_Name":TextInput(attrs={"class":"form-control"}),
            "Weight":TextInput(attrs={"class":"form-control"}),
            "Gender":Select(attrs={"class":"form-control"}),
            # "Date_Of_Birth":TextInput(attrs={"class":"form-control","type":"date","min":date}),
            "Mobile_Number":TextInput(attrs={"class":"form-control","type":"number"}),
            "Height":TextInput(attrs={"class":"form-control"}),
            # "Registration_Date":TextInput(attrs={"class":"form-control","type":"date","max":date}),
            # "Address":TextInput(attrs={"class":"form-control",'style': 'height: 3em !importent;'}),
            # "Medical_History":TextInput(attrs={"class":"form-control"}),
            "Photo":FileInput(attrs={"class":"form-control",'accept': 'image/*', 'capture':'camera', "id":"profilePic"}),
            # "Id_Upload":FileInput(attrs={"class":"form-control",'accept': 'image/*', 'capture':'camera'}),
            # "Access_Token_Id":TextInput(attrs={"class":"form-control"})

        }


from django.forms import inlineformset_factory
from .models import HealthHistory, Medication, ParqForm

class HealthHistoryForm(forms.ModelForm):
    class Meta:
        model = HealthHistory
        exclude = ['member', 'date_completed', 'last_updated']
        
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name',
                'required': True
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relationship (e.g., Spouse, Parent, Sibling)',
                'required': True
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Phone',
                'required': True
            }),
            'emergency_contact_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Emergency Contact Address'
            }),
            'current_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in KG',
                'step': '0.1',
                'required': True
            }),
            'current_height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in CM',
                'step': '0.1',
                'required': True
            }),
            'fitness_goal': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'fitness_goal_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your specific fitness goals...'
            }),
            'pt_availability': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'preferred_days': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monday, Wednesday, Friday',
                'required': True
            }),
            'physician_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Physician Name'
            }),
            'physician_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Physician Phone'
            }),
            'medical_care_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for medical care...'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any allergies (medications, foods, environmental)...'
            }),
            'personal_asthma': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Asthma details...'
            }),
            'personal_respiratory': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Respiratory condition details...'
            }),
            'personal_diabetes_type1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type 1 diabetes details...'
            }),
            'personal_diabetes_type2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type 2 diabetes details...'
            }),
            'diabetes_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'How long?'
            }),
            'personal_epilepsy_petite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Petite Mal details...'
            }),
            'personal_epilepsy_grand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Grand Mal details...'
            }),
            'personal_epilepsy_other': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Other epilepsy details...'
            }),
            'personal_osteoporosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Osteoporosis details...'
            }),
            'occupational_stress': forms.Select(attrs={'class': 'form-control'}),
            'energy_level': forms.Select(attrs={'class': 'form-control'}),
            'caffeine_daily': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of caffeine beverages daily'
            }),
            'alcohol_weekly': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of alcoholic drinks weekly'
            }),
            'colds_per_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of colds per year'
            }),
            'anemia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Anemia details...'
            }),
            'gastrointestinal_disorder': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'GI disorder details...'
            }),
            'hypoglycemia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hypoglycemia details...'
            }),
            'thyroid_disorder': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Thyroid disorder details...'
            }),
            'prenatal_postnatal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pre/Postnatal information...'
            }),
            'high_bp_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'High blood pressure details...'
            }),
            'hypertension_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hypertension details...'
            }),
            'high_cholesterol': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'High cholesterol details...'
            }),
            'hyperlipidemia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Hyperlipidemia details...'
            }),
            'heart_disease': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Heart disease details...'
            }),
            'heart_attack': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Heart attack details...'
            }),
            'stroke': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stroke details...'
            }),
            'angina': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Angina details...'
            }),
            'gout': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gout details...'
            }),
            'exercise_restrictions_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain any exercise restrictions...'
            }),
            'chest_pain_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain chest pain episodes...'
            }),
            'smoking_quit_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'head_neck_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Head/Neck issues...'
            }),
            'upper_back_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Upper back issues...'
            }),
            'shoulder_clavicle_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Shoulder/Clavicle issues...'
            }),
            'arm_elbow_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Arm/Elbow issues...'
            }),
            'wrist_hand_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Wrist/Hand issues...'
            }),
            'lower_back_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Lower back issues...'
            }),
            'hip_pelvis_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Hip/Pelvis issues...'
            }),
            'thigh_knee_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Thigh/Knee issues...'
            }),
            'arthritis_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Arthritis details...'
            }),
            'hernia_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hernia details...'
            }),
            'surgeries_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Previous surgeries details...'
            }),
            'other_musculoskeletal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Other musculoskeletal issues...'
            }),
            'diet_plan_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Diet plan details...'
            }),
            'supplements_list': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'List supplements...'
            }),
            'weight_change_amount': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +5kg or -3kg'
            }),
            'weight_change_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2 months, 6 weeks'
            }),
            'caffeine_beverages_daily': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of beverages'
            }),
            'nutritional_habits_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your current nutritional habits...'
            }),
            'food_allergies_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Food allergies, meal times, etc...'
            }),
            'work_exercise_habits': forms.Select(attrs={'class': 'form-control'}),
            'work_stress_level': forms.Select(attrs={'class': 'form-control'}),
            'home_stress_level': forms.Select(attrs={'class': 'form-control'}),
            'additional_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any additional comments pertinent to your exercise program...'
            }),

            'has_risky_heart_conditions': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'risky_heart_conditions_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please explain specific heart/cardiovascular conditions (e.g., heart disease, uncontrolled high blood pressure, irregular heartbeat, history of heart attack/stroke)...'
            }),
            'has_risky_health_conditions': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'risky_health_conditions_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please explain other health conditions that may be risky for gym workouts (respiratory issues, joint problems, metabolic conditions, neurological disorders, etc.)...'
            }),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark mandatory fields
        mandatory_fields = [
            'emergency_contact_name', 'emergency_contact_relationship', 
            'emergency_contact_phone', 'current_weight', 'current_height', 
            'fitness_goal', 'pt_availability', 'preferred_days'
        ]
        
        for field_name in mandatory_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                if 'placeholder' in self.fields[field_name].widget.attrs:
                    self.fields[field_name].widget.attrs['placeholder'] += ' *'


class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        exclude = ['health_history']
        widgets = {
            'medication_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medication name/type'
            }),
            'dosage_frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10mg twice daily'
            }),
            'reason_for_taking': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for taking this medication'
            }),
        }

# Create formset for medications
MedicationFormSet = inlineformset_factory(
    HealthHistory, 
    Medication, 
    form=MedicationForm,
    extra=3,  # Show 3 empty forms initially
    can_delete=True
)



#ParQ
class ParqFormModelForm(forms.ModelForm):
    class Meta:
        model = ParqForm
        fields = [
            
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_mobile',
            'heart_condition',
            'chest_pain_activity',
            'chest_pain_last_month',
            'lose_consciousness',
            'bone_joint_problem',
            'medical_conditions',
            'medical_conditions_specify',
            'current_treatment',
            'current_treatment_specify',
            'other_reason',
            'other_reason_specify',
            'participant_signature',
            'parent_guardian_signature',
            'tutor_signature',
            'participant_signature_date',
            'parent_guardian_signature_date',
            'tutor_signature_date'
        ]
        
        widgets = {
            'member': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select Member'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Phone'
            }),
            'emergency_contact_mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Mobile'
            }),
            'medical_conditions_specify': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please specify medical conditions'
            }),
            'current_treatment_specify': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please specify current treatment'
            }),
            'other_reason_specify': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please specify other reasons'
            }),
            'participant_signature': forms.HiddenInput(),
            'parent_guardian_signature': forms.HiddenInput(),
            'tutor_signature': forms.HiddenInput(),
            'participant_signature_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'parent_guardian_signature_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tutor_signature_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to boolean fields
        boolean_fields = [
            'heart_condition', 'chest_pain_activity', 'chest_pain_last_month',
            'lose_consciousness', 'bone_joint_problem', 'medical_conditions',
            'current_treatment', 'other_reason'
        ]
        
        for field_name in boolean_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-check-input'
            })

class ParqUpdateForm(forms.ModelForm):
    class Meta:
        model = ParqForm
        fields = [
            'emergency_contact_name',
            'emergency_contact_phone', 
            'emergency_contact_mobile',
            'heart_condition',
            'chest_pain_activity',
            'chest_pain_last_month',
            'lose_consciousness',
            'bone_joint_problem',
            'medical_conditions',
            'medical_conditions_specify',
            'current_treatment',
            'current_treatment_specify',
            'other_reason',
            'other_reason_specify'
        ]
        
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Phone'
            }),
            'emergency_contact_mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Mobile'
            }),
            'medical_conditions_specify': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please specify medical conditions'
            }),
            'current_treatment_specify': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please specify current treatment'
            }),
            'other_reason_specify': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please specify other reasons'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to boolean fields
        boolean_fields = [
            'heart_condition', 'chest_pain_activity', 'chest_pain_last_month',
            'lose_consciousness', 'bone_joint_problem', 'medical_conditions',
            'current_treatment', 'other_reason'
        ]
        
        for field_name in boolean_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-check-input'
            })


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Setting classess 

class Batch_DB(models.Model):
    Batch_Name = models.CharField(max_length=255,choices=(("Morning","Morning"),("Evening","Evening"),("Stoped","Stoped")))
    Batch_Status = models.BooleanField(default=True)
    Batch_Time = models.TimeField(auto_now_add=False)

    def __str__(self):
        return (str(self.Batch_Name) + " " + str(self.Batch_Time))


class TypeSubsription(models.Model):
    Type = models.CharField(max_length=255)
    def __str__(self):
        return self.Type



class Subscription_Period(models.Model):
    Period = models.PositiveIntegerField()
    Category = models.CharField(max_length=255, choices=(("Day","Day"),("Week","Week"),("Month","Month"),("Year","Year")))

    def __str__(self):
        return (str(self.Period) + " " +str(self.Category))
    

class MemberData(models.Model):
    First_Name = models.CharField(max_length=255)
    Last_Name = models.CharField(max_length=255, null= True,blank=True)
    Date_Of_Birth = models.DateField(auto_now_add=False,null= True,blank=True)
    Gender = models.CharField(max_length=255,choices=(("Male","Male"),("Female","Female"),("Other","Other")),default="Male")
    Mobile_Number = models.CharField(max_length=255)
    Discount = models.FloatField(null=True, blank= True)
    Special_Discount = models.BooleanField(default = False)
    Email = models.EmailField(null=True, blank=True)
    Address = models.TextField(max_length=200, null= True,blank=True )
    Medical_History = models.TextField(max_length=2000,null=True,blank=True)
    Registration_Date = models.DateField(auto_now_add=False)
    Photo = models.FileField(upload_to='member_photo', null= True,blank=True)
    Id_Upload = models.FileField(upload_to="member_id", null=True, blank=True)
    Date_Added = models.DateField(auto_now_add=True)
    Active_status = models.BooleanField(default=True)
    Access_status = models.BooleanField(default=False)
    Access_Token_Id = models.CharField(max_length=255,null=True,blank=True)
    risk_medical = models.BooleanField(default=False)

    def update_active_status(self):
        """
        Check if the member has any unpaid subscriptions.
        If any subscription has Payment_Status=False, set Active_status=False.
        """
        has_unpaid_subscriptions = self.Member_subscription.filter(Payment_Status=False).exists()
        
        if has_unpaid_subscriptions:
            self.Active_status = False
        else:
            self.Active_status = True  # Optionally re-enable if all are paid
        
        self.save()

    def __str__(self):
        if self.Last_Name == None:
            last_name = " "
        else:
            last_name = self.Last_Name
        try:
            return str(self.First_Name) + " " + str(last_name)
        except:
            return str(self.First_Name) + " " + str(self.Mobile_Number)

class Subscription(models.Model):
    Member = models.ForeignKey(MemberData, on_delete=models.CASCADE,null=True, blank=True, related_name="Member_subscription")
    Type_Of_Subscription = models.ForeignKey(TypeSubsription,on_delete=models.SET_NULL,null=True,blank=True)
    Period_Of_Subscription = models.ForeignKey(Subscription_Period, on_delete=models.SET_NULL,null=True, blank=True)
    Amount = models.IntegerField()
    Subscribed_Date = models.DateField(auto_now_add=False)
    Subscription_End_Date = models.DateField(auto_now_add=False,null=True,blank=True)
    Batch = models.ForeignKey(Batch_DB, on_delete=models.SET_NULL,null=True, blank=True, related_name="batch_time")
    Batch_Status = models.BooleanField(default=True)
    Payment_Status = models.BooleanField(default=False)
    partial_payment = models.BooleanField(default=False)

    sub_disable = models.BooleanField(default=False)


    def __str__(self):
        return str(self.Type_Of_Subscription) + " " + str(self.Period_Of_Subscription)
    


from django.core.exceptions import ValidationError

class Payment(models.Model):
    Member = models.ForeignKey(MemberData, on_delete=models.CASCADE)
    Subscription_ID = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name="Subscription_payment")
    Amount = models.IntegerField(null=True, blank=True)
    Mode_of_Payment = models.CharField(max_length=255, null=True, blank=True, choices=(("Cash", "Cash"), ("Bank Transfer", "Bank Transfer"), ("Card", "Card")))
    Payment_Date = models.DateField(auto_now_add=False, null=True, blank=True)
    Payment_Balance = models.FloatField(default=0)
    Payment_Status = models.BooleanField(default=False)
    Access_status = models.BooleanField(default=False)
    partial_payment = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If Payment_Balance is greater than 0, force Payment_Status to False
        if self.Payment_Balance > 0:
            self.Payment_Status = False
        super().save(*args, **kwargs)

    def clean(self):
        # Validation to prevent Payment_Status from being True when Payment_Balance > 0
        if self.Payment_Balance > 0 and self.Payment_Status:
            raise ValidationError({
                'Payment_Status': 'Payment status cannot be True when payment balance is greater than 0.'
            })
        super().clean()

   



class BalancePayment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="balance_payment")
    Amount = models.FloatField()
    Payment_Date = models.DateField(auto_now_add=True) 

class AccessToGate(models.Model):
    Member = models.ForeignKey(MemberData, on_delete=models.CASCADE)
    Subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    Validity_Date = models.DateField(auto_now_add=False)
    Status = models.BooleanField(default=False)
    Payment_status = models.BooleanField(default=False)

class Discounts(models.Model):
    Discount_Percentage = models.FloatField()
    Till_Date = models.DateField()


class HealthHistory(models.Model):
    # Link to existing member
    member = models.OneToOneField('MemberData', on_delete=models.CASCADE, related_name='health_history')
    
    # MANDATORY FIELDS
    # Emergency Contact Information (Mandatory)
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_address = models.TextField(max_length=500, null=True, blank=True)
    
    # Current Physical Information (Mandatory)
    current_weight = models.FloatField(validators=[MinValueValidator(0)])
    current_height = models.FloatField(validators=[MinValueValidator(0)])  # in cm
    
    # Fitness Goals (Mandatory)
    FITNESS_GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_building', 'Muscle Building'),
        ('cardiovascular', 'Cardiovascular Fitness'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility & Mobility'),
        ('sports_specific', 'Sports Specific Training'),
        ('general_fitness', 'General Fitness'),
        ('rehabilitation', 'Rehabilitation'),
        ('other', 'Other'),
    ]
    fitness_goal = models.CharField(max_length=50, choices=FITNESS_GOAL_CHOICES)
    fitness_goal_details = models.TextField(max_length=500, null=True, blank=True)
    
    # PT Session Availability (Mandatory)
    AVAILABILITY_CHOICES = [
        ('morning', 'Morning (6 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 6 PM)'),
        ('evening', 'Evening (6 PM - 10 PM)'),
        ('flexible', 'Flexible'),
    ]
    pt_availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES)
    preferred_days = models.CharField(max_length=200, help_text="e.g., Monday, Wednesday, Friday")
    
    # OPTIONAL FIELDS
    # Physician Information
    physician_name = models.CharField(max_length=255, null=True, blank=True)
    physician_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Current Health Care
    under_medical_care = models.BooleanField(default=False)
    medical_care_reason = models.TextField(max_length=500, null=True, blank=True)
    
    # Medications
    taking_medications = models.BooleanField(default=False)
    
    # Allergies
    allergies = models.TextField(max_length=1000, null=True, blank=True)
    
    # Basic Health Questions
    high_blood_pressure = models.BooleanField(default=False)
    bone_joint_problems = models.BooleanField(default=False)
    over_65 = models.BooleanField(default=False)
    unaccustomed_exercise = models.BooleanField(default=False)
    
    # Medical Conditions - Family History and Personal
    family_asthma = models.BooleanField(default=False)
    personal_asthma = models.TextField(max_length=500, null=True, blank=True)
    
    family_respiratory = models.BooleanField(default=False)
    personal_respiratory = models.TextField(max_length=500, null=True, blank=True)
    
    family_diabetes = models.BooleanField(default=False)
    personal_diabetes_type1 = models.TextField(max_length=200, null=True, blank=True)
    personal_diabetes_type2 = models.TextField(max_length=200, null=True, blank=True)
    diabetes_duration = models.CharField(max_length=100, null=True, blank=True)
    
    family_epilepsy = models.BooleanField(default=False)
    personal_epilepsy_petite = models.TextField(max_length=200, null=True, blank=True)
    personal_epilepsy_grand = models.TextField(max_length=200, null=True, blank=True)
    personal_epilepsy_other = models.TextField(max_length=200, null=True, blank=True)
    
    family_osteoporosis = models.BooleanField(default=False)
    personal_osteoporosis = models.TextField(max_length=500, null=True, blank=True)
    
    # Lifestyle Factors
    STRESS_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    occupational_stress = models.CharField(max_length=10, choices=STRESS_LEVEL_CHOICES, null=True, blank=True)
    
    ENERGY_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    energy_level = models.CharField(max_length=10, choices=ENERGY_LEVEL_CHOICES, null=True, blank=True)
    
    caffeine_daily = models.IntegerField(null=True, blank=True)
    alcohol_weekly = models.IntegerField(null=True, blank=True)
    colds_per_year = models.IntegerField(null=True, blank=True)
    
    anemia = models.TextField(max_length=300, null=True, blank=True)
    gastrointestinal_disorder = models.TextField(max_length=500, null=True, blank=True)
    hypoglycemia = models.TextField(max_length=300, null=True, blank=True)
    thyroid_disorder = models.TextField(max_length=300, null=True, blank=True)
    prenatal_postnatal = models.TextField(max_length=300, null=True, blank=True)
    
    # Cardiovascular
    high_bp_details = models.TextField(max_length=300, null=True, blank=True)
    hypertension_details = models.TextField(max_length=300, null=True, blank=True)
    high_cholesterol = models.TextField(max_length=500, null=True, blank=True)
    hyperlipidemia = models.TextField(max_length=500, null=True, blank=True)
    heart_disease = models.TextField(max_length=500, null=True, blank=True)
    heart_attack = models.TextField(max_length=300, null=True, blank=True)
    stroke = models.TextField(max_length=300, null=True, blank=True)
    angina = models.TextField(max_length=300, null=True, blank=True)
    gout = models.TextField(max_length=300, null=True, blank=True)
    
    # Exercise Restrictions
    exercise_restrictions = models.BooleanField(default=False)
    exercise_restrictions_details = models.TextField(max_length=1000, null=True, blank=True)
    
    chest_pain_exercise = models.BooleanField(default=False)
    chest_pain_details = models.TextField(max_length=500, null=True, blank=True)
    
    # Smoking
    SMOKING_CHOICES = [
        ('non_user', 'Non-user or former user'),
        ('cigar_pipe', 'Cigar and/or pipe'),
        ('1_15', '15 or less cigarettes per day'),
        ('16_25', '16 to 25 cigarettes per day'),
        ('26_35', '26 to 35 cigarettes per day'),
        ('35_plus', 'More than 35 cigarettes per day'),
    ]
    smoking_status = models.CharField(max_length=20, choices=SMOKING_CHOICES, null=True, blank=True)
    smoking_quit_date = models.DateField(null=True, blank=True)
    
    # Musculoskeletal Information
    head_neck_issues = models.TextField(max_length=500, null=True, blank=True)
    upper_back_issues = models.TextField(max_length=500, null=True, blank=True)
    shoulder_clavicle_issues = models.TextField(max_length=500, null=True, blank=True)
    arm_elbow_issues = models.TextField(max_length=500, null=True, blank=True)
    wrist_hand_issues = models.TextField(max_length=500, null=True, blank=True)
    lower_back_issues = models.TextField(max_length=500, null=True, blank=True)
    hip_pelvis_issues = models.TextField(max_length=500, null=True, blank=True)
    thigh_knee_issues = models.TextField(max_length=500, null=True, blank=True)
    arthritis_details = models.TextField(max_length=500, null=True, blank=True)
    hernia_details = models.TextField(max_length=300, null=True, blank=True)
    surgeries_details = models.TextField(max_length=1000, null=True, blank=True)
    other_musculoskeletal = models.TextField(max_length=500, null=True, blank=True)
    
    # Nutritional Information
    on_diet_plan = models.BooleanField(default=False)
    diet_plan_details = models.TextField(max_length=500, null=True, blank=True)
    
    taking_supplements = models.BooleanField(default=False)
    supplements_list = models.TextField(max_length=500, null=True, blank=True)
    
    weight_fluctuations = models.BooleanField(default=False)
    recent_weight_change = models.BooleanField(default=False)
    weight_change_amount = models.CharField(max_length=100, null=True, blank=True)
    weight_change_duration = models.CharField(max_length=100, null=True, blank=True)
    
    caffeine_beverages_daily = models.IntegerField(null=True, blank=True)
    nutritional_habits_description = models.TextField(max_length=1000, null=True, blank=True)
    food_allergies_issues = models.TextField(max_length=500, null=True, blank=True)
    
    # Work and Exercise Habits
    WORK_EXERCISE_CHOICES = [
        ('intense_both', 'Intense occupational and recreational exertion'),
        ('moderate_both', 'Moderate occupational and recreational exertion'),
        ('sedentary_intense', 'Sedentary occupational and intense recreational exertion'),
        ('sedentary_moderate', 'Sedentary occupational and moderate recreational exertion'),
        ('sedentary_light', 'Sedentary occupational and light recreational exertion'),
        ('no_exertion', 'Complete lack of all exertion'),
    ]
    work_exercise_habits = models.CharField(max_length=30, choices=WORK_EXERCISE_CHOICES, null=True, blank=True)
    
    STRESS_LEVEL_CHOICES = [
        ('minimal', 'Minimal'),
        ('moderate', 'Moderate'),
        ('average', 'Average'),
        ('extremely', 'Extremely'),
    ]
    work_stress_level = models.CharField(max_length=15, choices=STRESS_LEVEL_CHOICES, null=True, blank=True)
    home_stress_level = models.CharField(max_length=15, choices=STRESS_LEVEL_CHOICES, null=True, blank=True)
    
    works_over_40_hours = models.BooleanField(default=False)
    additional_comments = models.TextField(max_length=2000, null=True, blank=True)

    # Health Conditions Risky for Gym Workouts
    has_risky_heart_conditions = models.BooleanField(
        default=False, 
        help_text="Heart disease, uncontrolled high blood pressure, irregular heartbeat, history of heart attack/stroke"
    )
    risky_heart_conditions_details = models.TextField(
        max_length=1000, 
        null=True, 
        blank=True,
        help_text="Explain specific heart/cardiovascular conditions"
    )

    has_risky_health_conditions = models.BooleanField(
        default=False,
        help_text="Respiratory issues, joint problems, metabolic conditions, neurological disorders, etc."
    )
    risky_health_conditions_details = models.TextField(
        max_length=1000, 
        null=True, 
        blank=True,
        help_text="Explain specific health conditions that may be risky for gym workouts"
    ) 
        
    # Form completion
    date_completed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Health History"
        verbose_name_plural = "Health Histories"
    
    def __str__(self):
        return f"Health History - {self.member.First_Name} {self.member.Last_Name or ''}"


class Medication(models.Model):
    health_history = models.ForeignKey(HealthHistory, on_delete=models.CASCADE, related_name='medications')
    medication_type = models.CharField(max_length=255)
    dosage_frequency = models.CharField(max_length=255)
    reason_for_taking = models.CharField(max_length=500)
    
    def __str__(self):
        return f"{self.medication_type} - {self.health_history.member.First_Name}"


class ParqForm(models.Model):
    member = models.OneToOneField('MemberData', on_delete=models.CASCADE, related_name='health_history_parque')
    
    # Contact Details
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_mobile = models.CharField(max_length=15, blank=True, null=True)
    
    # PAR-Q Questions (YES/NO)
    heart_condition = models.BooleanField(default=False, help_text="Has your doctor ever said that you have a heart condition?")
    chest_pain_activity = models.BooleanField(default=False, help_text="Do you have chest pain brought on by physical activity?")
    chest_pain_last_month = models.BooleanField(default=False, help_text="Have you developed chest pain in the last month?")
    lose_consciousness = models.BooleanField(default=False, help_text="Do you tend to lose consciousness or fall over as a result of dizziness?")
    bone_joint_problem = models.BooleanField(default=False, help_text="Do you have a bone or joint problem that could be aggravated by physical activity?")
    medical_conditions = models.BooleanField(default=False, help_text="Do you suffer from asthma, diabetes, high blood pressure, epilepsy or a heart condition?")
    medical_conditions_specify = models.TextField(blank=True, null=True, help_text="Please specify medical conditions")
    current_treatment = models.BooleanField(default=False, help_text="Do you have any current conditions or injuries being treated by a doctor?")
    current_treatment_specify = models.TextField(blank=True, null=True, help_text="Please specify current treatment")
    other_reason = models.BooleanField(default=False, help_text="Do you know of any other reason why you should not take part in exercise?")
    other_reason_specify = models.TextField(blank=True, null=True, help_text="Please specify other reasons")
    
    # Signatures
    participant_signature = models.TextField(blank=True, null=True, help_text="Participant signature data (base64)")
    parent_guardian_signature = models.TextField(blank=True, null=True, help_text="Parent/Guardian signature data (base64)")
    tutor_signature = models.TextField(blank=True, null=True, help_text="Tutor signature data (base64)")
    
    # Dates
    form_date = models.DateField(auto_now_add=True)
    participant_signature_date = models.DateField(blank=True, null=True)
    parent_guardian_signature_date = models.DateField(blank=True, null=True)
    tutor_signature_date = models.DateField(blank=True, null=True)
    
    # Form status
    requires_doctor_consent = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Check if doctor's consent is required (if any question is answered YES)
        self.requires_doctor_consent = any([
            self.heart_condition,
            self.chest_pain_activity,
            self.chest_pain_last_month,
            self.lose_consciousness,
            self.bone_joint_problem,
            self.medical_conditions,
            self.current_treatment,
            self.other_reason
        ])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"PAR-Q Form - {self.member.First_Name}"
    
    class Meta:
        verbose_name = "PAR-Q Form"
        verbose_name_plural = "PAR-Q Forms"





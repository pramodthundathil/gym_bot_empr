from django.db import models

class EnquiryData(models.Model):
    date_created =  models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    name = models.CharField(max_length=250)
    phone_number = models.BigIntegerField()
    email = models.EmailField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    number_of_followup = models.IntegerField(default=0)

    last_follow_up_date = models.DateField(null=True, blank=True)
    next_follow_up_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('not_required', 'Not Required'),
        ('rejected', 'rejected'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    conversion = models.BooleanField(default=False)
    health_history_json = models.TextField(null=True, blank=True)

    def __str__(self):

        return f"Enquire - {self.name} "



class EnquiryStatus(models.Model):
    enquiry = models.ForeignKey(EnquiryData, on_delete=models.CASCADE)
    date_of_status = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('not_required', 'Not Required'),
        ('rejected', 'rejected'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    LEAD_STATUS_CHOICES = [
        ('rnr', 'RNR'),
        ('callback', 'Callback'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('converted', 'Converted'),
        ('follow_up', 'Follow Up'),
        ('closed', 'Closed'),
    ]
    call_status = models.CharField(max_length=30, choices=LEAD_STATUS_CHOICES, default='rnr')


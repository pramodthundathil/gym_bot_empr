from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import EnquiryData, EnquiryStatus
from django.core.paginator import Paginator
from .forms import EnquiryDataForm, EnquiryStatusForm, EnquiryFilterForm
from Members.models import MemberData




def enquiries(request):
    """Dashboard view with comprehensive statistics"""
    
    # Basic counts
    total_enquiries = EnquiryData.objects.count()
    converted_enquiries = EnquiryData.objects.filter(conversion=True).count()
    pending_enquiries = EnquiryData.objects.filter(conversion=False).count()
    
    # Status breakdown
    status_breakdown = EnquiryData.objects.values('status').annotate(
        count=Count('status')
    ).order_by('-count')
    
    # Recent enquiries (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_enquiries = EnquiryData.objects.filter(
        date_created__gte=thirty_days_ago
    ).count()
    
    # This month's enquiries
    current_month = timezone.now().replace(day=1).date()
    this_month_enquiries = EnquiryData.objects.filter(
        date_created__gte=current_month
    ).count()
    
    # Today's enquiries
    today = timezone.now().date()
    today_enquiries = EnquiryData.objects.filter(
        date_created=today
    ).count()
    
    # Conversion rate
    conversion_rate = (converted_enquiries / total_enquiries * 100) if total_enquiries > 0 else 0
    
    # Follow-up statistics
    total_followups = EnquiryStatus.objects.count()
    avg_followups = (total_followups / total_enquiries) if total_enquiries > 0 else 0
    
    # Enquiries needing follow-up (next_follow_up_date is today or past)
    needs_followup = EnquiryData.objects.filter(
        Q(next_follow_up_date__lte=today) & Q(conversion=False)
    ).exclude(status__in=['completed', 'rejected', 'not_required']).count()
    
    # Overdue follow-ups (past due)
    overdue_followups = EnquiryData.objects.filter(
        Q(next_follow_up_date__lt=today) & Q(conversion=False)
    ).exclude(status__in=['completed', 'rejected', 'not_required']).count()
    
    # Today's follow-ups (due today)
    today_followups = EnquiryData.objects.filter(
        Q(next_follow_up_date=today) & Q(conversion=False)
    ).exclude(status__in=['completed', 'rejected', 'not_required']).count()
    
    # Recent enquiries for display
    recent_enquiries_list = EnquiryData.objects.order_by('-date_created')[:5]
    
    # Recent follow-ups
    recent_followups = EnquiryStatus.objects.select_related('enquiry').order_by('-date_of_status')[:5]
    
    # Call status breakdown for recent follow-ups
    call_status_breakdown = EnquiryStatus.objects.values('call_status').annotate(
        count=Count('call_status')
    ).order_by('-count')
    
    # Today's pending follow-ups for quick display (top 5)
    todays_pending_followups = EnquiryData.objects.filter(
        Q(next_follow_up_date__lte=today) & Q(conversion=False)
    ).exclude(status__in=['completed', 'rejected', 'not_required']).order_by('next_follow_up_date')[:5]
    
    # Monthly trend data (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = (timezone.now().replace(day=1) - timedelta(days=32*i)).replace(day=1).date()
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        month_enquiries = EnquiryData.objects.filter(
            date_created__gte=month_start,
            date_created__lt=next_month
        ).count()
        
        month_conversions = EnquiryData.objects.filter(
            date_created__gte=month_start,
            date_created__lt=next_month,
            conversion=True
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'enquiries': month_enquiries,
            'conversions': month_conversions
        })
    
    context = {
        # Basic stats
        'total_enquiries': total_enquiries,
        'converted_enquiries': converted_enquiries,
        'pending_enquiries': pending_enquiries,
        'conversion_rate': round(conversion_rate, 1),
        
        # Time-based stats
        'recent_enquiries_count': recent_enquiries,
        'this_month_enquiries': this_month_enquiries,
        'today_enquiries': today_enquiries,
        
        # Follow-up stats
        'total_followups': total_followups,
        'avg_followups': round(avg_followups, 1),
        'needs_followup': needs_followup,
        'overdue_followups': overdue_followups,
        'today_followups': today_followups,
        
        # Breakdowns
        'status_breakdown': status_breakdown,
        'call_status_breakdown': call_status_breakdown,
        
        # Recent data
        'recent_enquiries_list': recent_enquiries_list,
        'recent_followups': recent_followups,
        'monthly_data': monthly_data,
        'todays_pending_followups': todays_pending_followups,
        
        # Current date for template
        'today': today,
    }
    
    return render(request, "enquiries/index.html", context)


def todays_followups(request):
    """View for today's and pending follow-ups"""
    today = timezone.now().date()
    
    # Get all enquiries that need follow-up (today or overdue)
    followup_enquiries = EnquiryData.objects.filter(
        Q(next_follow_up_date__lte=today) & Q(conversion=False)
    ).exclude(status__in=['completed', 'rejected', 'not_required']).order_by('next_follow_up_date', 'name')
    
    # Separate today's and overdue
    todays_followups = followup_enquiries.filter(next_follow_up_date=today)
    overdue_followups = followup_enquiries.filter(next_follow_up_date__lt=today)
    
    # Get upcoming follow-ups (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_followups = EnquiryData.objects.filter(
        Q(next_follow_up_date__gt=today) & 
        Q(next_follow_up_date__lte=next_week) & 
        Q(conversion=False)
    ).exclude(status__in=['completed', 'rejected', 'not_required']).order_by('next_follow_up_date', 'name')
    
    # Statistics
    total_due = followup_enquiries.count()
    today_count = todays_followups.count()
    overdue_count = overdue_followups.count()
    upcoming_count = upcoming_followups.count()
    
    # Handle quick status updates via AJAX/form submission
    if request.method == 'POST' and 'enquiry_id' in request.POST:
        enquiry_id = request.POST.get('enquiry_id')
        quick_status = request.POST.get('quick_status')
        quick_notes = request.POST.get('quick_notes', '')
        
        try:
            enquiry = EnquiryData.objects.get(id=enquiry_id)
            
            # Create new status update
            status_update = EnquiryStatus.objects.create(
                enquiry=enquiry,
                description=quick_notes or f"Quick update: {quick_status}",
                status=enquiry.status,  # Keep current status
                call_status=quick_status
            )
            
            # Update enquiry
            enquiry.number_of_followup += 1
            enquiry.last_follow_up_date = today
            
            # Set next follow-up based on status
            if quick_status == 'callback':
                enquiry.next_follow_up_date = today + timedelta(days=1)
            elif quick_status == 'follow_up':
                enquiry.next_follow_up_date = today + timedelta(days=3)
            elif quick_status == 'converted':
                enquiry.conversion = True
                enquiry.next_follow_up_date = None
                enquiry.status = 'completed'
            elif quick_status == 'not_interested':
                enquiry.status = 'rejected'
                enquiry.next_follow_up_date = None
            elif quick_status == 'closed':
                enquiry.status = 'not_required'
                enquiry.next_follow_up_date = None
            else:
                enquiry.next_follow_up_date = today + timedelta(days=2)
            
            enquiry.save()
            messages.success(request, f"Quick update added for {enquiry.name}")
            
        except EnquiryData.DoesNotExist:
            messages.error(request, "Enquiry not found")
        
        return redirect('todays_followups')
    
    context = {
        'todays_followups': todays_followups,
        'overdue_followups': overdue_followups,
        'upcoming_followups': upcoming_followups,
        'total_due': total_due,
        'today_count': today_count,
        'overdue_count': overdue_count,
        'upcoming_count': upcoming_count,
        'today': today,
    }
    
    return render(request, 'enquiries/todays_followups.html', context)


# ... existing views (enquiry_list, enquiry_detail, etc.) ...



def enquiry_list(request):
    """View to list all enquiries with filtering options"""
    enquiries = EnquiryData.objects.all().order_by('-date_created')
    filter_form = EnquiryFilterForm(request.GET or None)
    
    # Apply filters
    if filter_form.is_valid():
        conversion = filter_form.cleaned_data.get('conversion')
        status = filter_form.cleaned_data.get('status')
        search = filter_form.cleaned_data.get('search')
        
        # Filter by conversion status
        if conversion:
            conversion_bool = conversion == 'True'
            enquiries = enquiries.filter(conversion=conversion_bool)
        
        # Filter by status
        if status:
            enquiries = enquiries.filter(status=status)
        
        # Search filter
        if search:
            enquiries = enquiries.filter(
                Q(name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search)
            )
    
    # Default filter: show only non-converted enquiries if no filter is applied
    if not request.GET:
        enquiries = enquiries.filter(conversion=False)
    
    # Pagination
    paginator = Paginator(enquiries, 10)  # Show 10 enquiries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_enquiries': enquiries.count()
    }
    
    return render(request, 'enquiries/enquiry_list.html', context)


def enquiry_detail(request, pk):
    """View to display single enquiry details with all follow-up statuses"""
    enquiry = get_object_or_404(EnquiryData, pk=pk)
    statuses = EnquiryStatus.objects.filter(enquiry=enquiry).order_by('-date_of_status')
    
    health_history = None
    if enquiry.health_history_json:
        import json
        try:
            health_history = json.loads(enquiry.health_history_json)
        except Exception:
            pass
            
    context = {
        'enquiry': enquiry,
        'statuses': statuses,
        'health_history': health_history,
    }
    
    return render(request, 'enquiries/enquiry_detail.html', context)


def enquiry_update(request, pk):
    """View to update enquiry details"""
    enquiry = get_object_or_404(EnquiryData, pk=pk)
    
    if request.method == 'POST':
        form = EnquiryDataForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry updated successfully!')
            return redirect('enquiry_detail', pk=pk)
    else:
        form = EnquiryDataForm(instance=enquiry)
    
    context = {
        'form': form,
        'enquiry': enquiry,
    }
    
    return render(request, 'enquiries/enquiry_update.html', context)


def add_status_update(request, pk):
    """View to add new status update to an enquiry"""
    enquiry = get_object_or_404(EnquiryData, pk=pk)
    
    if request.method == 'POST':
        form = EnquiryStatusForm(request.POST)
        next_followup = request.POST.get('next_followup',None)
        if form.is_valid():
            status = form.save(commit=False)
            status.enquiry = enquiry
            status.save()
            
            # Update enquiry's status and follow-up count
            enquiry.status = status.status
            enquiry.number_of_followup += 1
            enquiry.last_follow_up_date = timezone.now().date()
            
            # Update conversion status if call_status is 'converted'
            if status.call_status == 'converted':
                enquiry.conversion = True
                member = MemberData.objects.create(
                    First_Name=enquiry.name,
                    Mobile_Number=enquiry.phone_number,
                    Email=enquiry.email,
                    Registration_Date=timezone.now(),
                    Active_status=False,
                    Access_status=False
                )
                member.save()
                
                # Check for health history json
                if enquiry.health_history_json:
                    import json
                    from Members.models import HealthHistory, Medication, ParqForm
                    try:
                        hh_data = json.loads(enquiry.health_history_json)
                        
                        # Create HealthHistory
                        health_history = HealthHistory.objects.create(
                            member=member,
                            emergency_contact_name=hh_data.get('emergency_contact_name', ''),
                            emergency_contact_relationship=hh_data.get('emergency_contact_relationship', ''),
                            emergency_contact_phone=hh_data.get('emergency_contact_phone', ''),
                            emergency_contact_address=hh_data.get('emergency_contact_address', ''),
                            current_weight=float(hh_data.get('current_weight', 0) or 0),
                            current_height=float(hh_data.get('current_height', 0) or 0),
                            fitness_goal=hh_data.get('fitness_goal', 'Loss Weight'),
                            fitness_goal_details=hh_data.get('fitness_goal_details', ''),
                            pt_availability=hh_data.get('pt_availability', 'Morning'),
                            preferred_days=hh_data.get('preferred_days', ''),
                            under_medical_care=bool(hh_data.get('under_medical_care', False)),
                            medical_care_reason=hh_data.get('medical_care_reason', ''),
                            taking_medications=bool(hh_data.get('taking_medications', False)),
                            allergies=hh_data.get('allergies', ''),
                            high_blood_pressure=bool(hh_data.get('high_blood_pressure', False)),
                            bone_joint_problems=bool(hh_data.get('bone_joint_problems', False)),
                            over_65=bool(hh_data.get('over_65', False)),
                            unaccustomed_exercise=bool(hh_data.get('unaccustomed_exercise', False)),
                            has_risky_heart_conditions=bool(hh_data.get('has_risky_heart_conditions', False)),
                            risky_heart_conditions_details=hh_data.get('risky_heart_conditions_details', ''),
                            has_risky_health_conditions=bool(hh_data.get('has_risky_health_conditions', False)),
                            risky_health_conditions_details=hh_data.get('risky_health_conditions_details', '')
                        )
                        
                        # Set risk_medical flag on member if heart or health risk is checked
                        if health_history.has_risky_heart_conditions or health_history.has_risky_health_conditions:
                            member.risk_medical = True
                            member.save()
                        
                        # Create Medications
                        medications = hh_data.get('medications', [])
                        for med in medications:
                            if med.get('name'):
                                Medication.objects.create(
                                    health_history=health_history,
                                    name=med.get('name'),
                                    dosage=med.get('dosage', ''),
                                    frequency=med.get('frequency', '')
                                )

                        # Create PAR-Q Form
                        ParqForm.objects.create(
                            member=member,
                            emergency_contact_name=hh_data.get('emergency_contact_name', ''),
                            emergency_contact_phone=hh_data.get('emergency_contact_phone', ''),
                            emergency_contact_mobile=hh_data.get('emergency_contact_phone', ''),
                            heart_condition=bool(hh_data.get('heart_condition', False)),
                            chest_pain_activity=bool(hh_data.get('chest_pain_activity', False)),
                            chest_pain_last_month=bool(hh_data.get('chest_pain_last_month', False)),
                            lose_consciousness=bool(hh_data.get('lose_consciousness', False)),
                            bone_joint_problem=bool(hh_data.get('bone_joint_problem', False)),
                            medical_conditions=bool(hh_data.get('medical_conditions', False)),
                            medical_conditions_specify=hh_data.get('medical_conditions_specify', ''),
                            current_treatment=bool(hh_data.get('current_treatment', False)),
                            current_treatment_specify=hh_data.get('current_treatment_specify', ''),
                            other_reason=bool(hh_data.get('other_reason', False)),
                            other_reason_specify=hh_data.get('other_reason_specify', ''),
                            is_completed=True
                        )
                    except Exception as e:
                        print("Error restoring health history during conversion:", e)

            if next_followup:
                enquiry.next_follow_up_date = next_followup
            enquiry.save()
            
            messages.success(request, 'Status update added successfully!')
            return redirect('enquiry_detail', pk=pk)
    else:
        form = EnquiryStatusForm()
    
    context = {
        'form': form,
        'enquiry': enquiry,
    }
    
    return render(request, 'enquiries/add_status_update.html', context)


def enquiry_create(request):
    """View to create new enquiry"""
    if request.method == 'POST':
        form = EnquiryDataForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            messages.success(request, 'New enquiry created successfully!')
            return redirect('enquiry_detail', pk=enquiry.pk)
    else:
        form = EnquiryDataForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'enquiries/enquiry_create.html', context)


def public_enrolment(request):
    """Public view for new walk-in customer self-enrolment"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        age = request.POST.get('age')
        
        # Phone validation & safe conversion
        try:
            phone_val = int(phone_number)
            if phone_val > 9223372036854775807:
                phone_val = 9223372036854775807
        except (ValueError, TypeError):
            phone_val = 0
            
        try:
            age_val = int(age)
        except (ValueError, TypeError):
            age_val = None

        if not name or not phone_number:
            messages.error(request, "Name and Phone Number are required fields.")
            return render(request, 'enquiries/public_enrolment.html')

        if len(phone_number.strip()) < 10:
            messages.error(request, "Phone number must be at least 10 digits.")
            return render(request, 'enquiries/public_enrolment.html')

        # Gather health history fields & PAR-Q fields
        health_history_dict = {
            # Emergency Contact
            'emergency_contact_name': request.POST.get('emergency_contact_name', ''),
            'emergency_contact_relationship': request.POST.get('emergency_contact_relationship', ''),
            'emergency_contact_phone': request.POST.get('emergency_contact_phone', ''),
            'emergency_contact_address': request.POST.get('emergency_contact_address', ''),
            
            # Physical Info
            'current_weight': request.POST.get('current_weight', 0),
            'current_height': request.POST.get('current_height', 0),
            'fitness_goal': request.POST.get('fitness_goal', 'Loss Weight'),
            'fitness_goal_details': request.POST.get('fitness_goal_details', ''),
            'pt_availability': request.POST.get('pt_availability', 'Morning'),
            'preferred_days': ', '.join(request.POST.getlist('preferred_days')),
            
            # Health History Questions
            'under_medical_care': request.POST.get('under_medical_care') == 'true',
            'medical_care_reason': request.POST.get('medical_care_reason', ''),
            'taking_medications': request.POST.get('taking_medications') == 'true',
            'allergies': request.POST.get('allergies', ''),
            'high_blood_pressure': request.POST.get('high_blood_pressure') == 'true',
            'bone_joint_problems': request.POST.get('bone_joint_problems') == 'true',
            'over_65': request.POST.get('over_65') == 'true',
            'unaccustomed_exercise': request.POST.get('unaccustomed_exercise') == 'true',
            'has_risky_heart_conditions': request.POST.get('has_risky_heart_conditions') == 'true',
            'risky_heart_conditions_details': request.POST.get('risky_heart_conditions_details', ''),
            'has_risky_health_conditions': request.POST.get('has_risky_health_conditions') == 'true',
            'risky_health_conditions_details': request.POST.get('risky_health_conditions_details', ''),
            
            # PAR-Q Questionnaire Questions
            'heart_condition': request.POST.get('heart_condition') == 'true',
            'chest_pain_activity': request.POST.get('chest_pain_activity') == 'true',
            'chest_pain_last_month': request.POST.get('chest_pain_last_month') == 'true',
            'lose_consciousness': request.POST.get('lose_consciousness') == 'true',
            'bone_joint_problem': request.POST.get('bone_joint_problem') == 'true',
            'medical_conditions': request.POST.get('medical_conditions') == 'true',
            'medical_conditions_specify': request.POST.get('medical_conditions_specify', ''),
            'current_treatment': request.POST.get('current_treatment') == 'true',
            'current_treatment_specify': request.POST.get('current_treatment_specify', ''),
            'other_reason': request.POST.get('other_reason') == 'true',
            'other_reason_specify': request.POST.get('other_reason_specify', ''),
            
            'medications': []
        }
        
        # Gather medications
        med_names = request.POST.getlist('med_name[]')
        med_dosages = request.POST.getlist('med_dosage[]')
        med_frequencies = request.POST.getlist('med_frequency[]')
        
        for i in range(len(med_names)):
            if i < len(med_names) and med_names[i].strip():
                health_history_dict['medications'].append({
                    'name': med_names[i],
                    'dosage': med_dosages[i] if i < len(med_dosages) else '',
                    'frequency': med_frequencies[i] if i < len(med_frequencies) else ''
                })

        # Save EnquiryData with serialized JSON
        import json
        enquiry = EnquiryData.objects.create(
            name=name,
            phone_number=phone_val,
            email=email,
            age=age_val,
            status='pending',
            health_history_json=json.dumps(health_history_dict)
        )
        enquiry.save()
        
        return render(request, 'enquiries/public_enrolment_success.html', {'name': name})
        
    return render(request, 'enquiries/public_enrolment.html')


def download_qr_pdf(request):
    """Generate a PDF flyer with Empire Fitness logo and registration QR code"""
    import base64
    import requests
    from Index.models import Logo
    from django.template.loader import get_template
    from django.http import HttpResponse
    
    # 1. Get Logo
    logo_base64 = ""
    import os
    from django.conf import settings
    logo_path = os.path.join(settings.BASE_DIR, 'static/assets/images/empr.png')
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as f:
                logo_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            pass
        
    # 2. Get QR Code
    registration_url = request.build_absolute_uri('/enquiries/register/')
    qr_base64 = ""
    try:
        api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={registration_url}"
        qr_response = requests.get(api_url)
        if qr_response.status_code == 200:
            qr_base64 = base64.b64encode(qr_response.content).decode('utf-8')
    except Exception:
        pass
        
    context = {
        'logo_base64': logo_base64,
        'qr_base64': qr_base64,
        'registration_url': registration_url
    }
    
    # Render PDF template
    template = get_template('enquiries/qr_pdf.html')
    html = template.render(context)
    
    # Compile PDF
    try:
        from weasyprint import HTML
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="empire_fitness_registration_qr.pdf"'
        pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
        response.write(pdf)
        return response
    except ImportError:
        from xhtml2pdf import pisa
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="empire_fitness_registration_qr.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating PDF flyer <pre>" + html + "</pre>")
        return response


from django.contrib.auth.decorators import login_required

@login_required(login_url='SignIn')
def convert_to_member(request, pk):
    """Directly convert an enquiry to a member (setting all statuses to False)"""
    enquiry = get_object_or_404(EnquiryData, pk=pk)
    
    if enquiry.conversion:
        messages.info(request, f"{enquiry.name} is already converted to a member.")
        return redirect('enquiry_detail', pk=pk)
        
    enquiry.conversion = True
    enquiry.status = 'completed'
    enquiry.save()
    
    # Create Member with False statuses
    member = MemberData.objects.create(
        First_Name=enquiry.name,
        Mobile_Number=enquiry.phone_number,
        Email=enquiry.email,
        Registration_Date=timezone.now(),
        Active_status=False,
        Access_status=False
    )
    member.save()
    
    # Check for health history json
    if enquiry.health_history_json:
        import json
        from Members.models import HealthHistory, Medication, ParqForm
        try:
            hh_data = json.loads(enquiry.health_history_json)
            
            # Create HealthHistory
            health_history = HealthHistory.objects.create(
                member=member,
                emergency_contact_name=hh_data.get('emergency_contact_name', ''),
                emergency_contact_relationship=hh_data.get('emergency_contact_relationship', ''),
                emergency_contact_phone=hh_data.get('emergency_contact_phone', ''),
                emergency_contact_address=hh_data.get('emergency_contact_address', ''),
                current_weight=float(hh_data.get('current_weight', 0) or 0),
                current_height=float(hh_data.get('current_height', 0) or 0),
                fitness_goal=hh_data.get('fitness_goal', 'Loss Weight'),
                fitness_goal_details=hh_data.get('fitness_goal_details', ''),
                pt_availability=hh_data.get('pt_availability', 'Morning'),
                preferred_days=hh_data.get('preferred_days', ''),
                under_medical_care=bool(hh_data.get('under_medical_care', False)),
                medical_care_reason=hh_data.get('medical_care_reason', ''),
                taking_medications=bool(hh_data.get('taking_medications', False)),
                allergies=hh_data.get('allergies', ''),
                high_blood_pressure=bool(hh_data.get('high_blood_pressure', False)),
                bone_joint_problems=bool(hh_data.get('bone_joint_problems', False)),
                over_65=bool(hh_data.get('over_65', False)),
                unaccustomed_exercise=bool(hh_data.get('unaccustomed_exercise', False)),
                has_risky_heart_conditions=bool(hh_data.get('has_risky_heart_conditions', False)),
                risky_heart_conditions_details=hh_data.get('risky_heart_conditions_details', ''),
                has_risky_health_conditions=bool(hh_data.get('has_risky_health_conditions', False)),
                risky_health_conditions_details=hh_data.get('risky_health_conditions_details', '')
            )
            
            # Set risk_medical flag on member if heart or health risk is checked
            if health_history.has_risky_heart_conditions or health_history.has_risky_health_conditions:
                member.risk_medical = True
                member.save()
            
            # Create Medications
            medications = hh_data.get('medications', [])
            for med in medications:
                if med.get('name'):
                    Medication.objects.create(
                        health_history=health_history,
                        name=med.get('name'),
                        dosage=med.get('dosage', ''),
                        frequency=med.get('frequency', '')
                    )

            # Create PAR-Q Form
            ParqForm.objects.create(
                member=member,
                emergency_contact_name=hh_data.get('emergency_contact_name', ''),
                emergency_contact_phone=hh_data.get('emergency_contact_phone', ''),
                emergency_contact_mobile=hh_data.get('emergency_contact_phone', ''),
                heart_condition=bool(hh_data.get('heart_condition', False)),
                chest_pain_activity=bool(hh_data.get('chest_pain_activity', False)),
                chest_pain_last_month=bool(hh_data.get('chest_pain_last_month', False)),
                lose_consciousness=bool(hh_data.get('lose_consciousness', False)),
                bone_joint_problem=bool(hh_data.get('bone_joint_problem', False)),
                medical_conditions=bool(hh_data.get('medical_conditions', False)),
                medical_conditions_specify=hh_data.get('medical_conditions_specify', ''),
                current_treatment=bool(hh_data.get('current_treatment', False)),
                current_treatment_specify=hh_data.get('current_treatment_specify', ''),
                other_reason=bool(hh_data.get('other_reason', False)),
                other_reason_specify=hh_data.get('other_reason_specify', ''),
                is_completed=True
            )
        except Exception as e:
            print("Error restoring health history during conversion:", e)
            
    messages.success(request, f"{enquiry.name} converted to Member successfully! (Access & Subscription pending payment)")
    return redirect('MembersSingleView', pk=member.pk)
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from Members.models import Subscription_Period, Subscription, Batch_DB, TypeSubsription,MemberData,Payment, AccessToGate, Discounts
from Members.forms import Subscription_PeriodForm, BatchForm, TypeSubsriptionForm
from datetime import datetime, timedelta
from django.utils import timezone
from .models import ConfigarationDB, Support
from Members.views import ScheduledTask
from .decorator import unautenticated_user, allowed_users
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string



this_month = timezone.now().month
end_date = timezone.now()
start_date = end_date + timedelta(days=-7)

from datetime import datetime
from django.db.models import Sum

@login_required(login_url='SignIn')
def Home(request):
    # Get the first 8 subscribers in reverse order directly
    subscribers = Subscription.objects.order_by('-id')[:8]
    subscribers_pending = Subscription.objects.filter(Payment_Status = False).order_by('-id')
    members = MemberData.objects.all()
    month = datetime.now().strftime('%B')
    
    # Assuming start_date and end_date are defined elsewhere in your code
    notification_payments = Payment.objects.filter(Payment_Date__gte=start_date, Payment_Date__lte=end_date)
    disc = Discounts.objects.filter(Till_Date__lte=end_date)

    # Bulk update Payment_Status and AccessToGate status
    subscrib = Subscription.objects.filter(Subscription_End_Date__lte=end_date)
    subscrib.update(Payment_Status=False)

    # access_ids = subscrib.values_list('AccessToGate__id', flat=True)
    AccessToGate.objects.filter(Subscription__in=list(subscrib)).update(Status=False)

    access = AccessToGate.objects.filter(Validity_Date__lte=end_date)
    access.update(Status=False)

    # Aggregate collected amount
    this_month = datetime.now().month
    # collected_amount = Payment.objects.filter(Payment_Date__month=this_month).aggregate(Sum('Amount'))['Amount__sum'] or 0
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    collected_amount = Payment.objects.filter(
        Payment_Date__month=current_month,
        Payment_Date__year=current_year
    ).aggregate(Sum('Amount'))['Amount__sum'] or 0
    # Delete discounts and update member discounts in bulk
    disc.delete()
    members.update(Discount=0)
    
    print("return... the task")
    # Count active members
    active_count = MemberData.objects.filter(Active_status=True).count()

    # Count inactive members
    inactive_count = MemberData.objects.filter(Active_status=False).count()

    context = {
        "subscribers": subscribers,
        "subscribers_pending":subscribers_pending,
        "membercount": members.count(),
        "feepending": Subscription.objects.filter(Payment_Status=False).count(),
        "month": month,
        "collected_amount": collected_amount,
        "notification_payments": notification_payments,
        "notificationcount": notification_payments.count(),
        "current_year":current_year,
        "active_count": active_count,
        "inactive_count": inactive_count,
    }

    return render(request, "index.html", context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def trigger_scheduled_task(request):
    if request.method == 'POST':
        try:
            ScheduledTask()  # Call your function here
            return JsonResponse({'status': 'success', 'message': 'Task executed successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



@login_required(login_url='SignIn')
def Setting_Module(request):

    form = BatchForm()
    sub_form = Subscription_PeriodForm()
    typesub_form = TypeSubsriptionForm()

    batch = Batch_DB.objects.all()
    speriod = Subscription_Period.objects.all()
    Sub_type = TypeSubsription.objects.all()
    try:
        config = ConfigarationDB.objects.all()[0]
    except:
        config = ConfigarationDB.objects.create(
                JWT_IP="192.168.1.1",
                JWT_PORT="8080",
                Call_Back_IP="192.168.1.2",
                Call_Back_Port="9090",
                Admin_Username="admin_user",
                Admin_Password="securepassword123"
            )
        config.save()


    context = {
        "form":form,
        "sub_form":sub_form,
        "batch":batch,
        "speriod":speriod,
        "typesub_form":typesub_form,
        "Sub_type":Sub_type,
        "config":config
    }
    return  render(request, "settings.html",context)

@login_required(login_url='SignIn')
def BatchSave(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Batch Data Saved")
            return redirect("Setting_Module")
        else:
            messages.error(request,"Something Went wrong")
            return redirect("Setting_Module")
    return redirect("Setting_Module")

def Batch_Delete(request,pk):
    batch = Batch_DB.objects.get(id = pk).delete()
    messages.success(request,"Batch Data Deleted")
    return redirect("Setting_Module")


@login_required(login_url='SignIn')
def SubscriptionPeriodSave(request):
    if request.method == "POST":
        form = Subscription_PeriodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Subscription Period Saved")
            return redirect("Setting_Module")
        else:
            messages.error(request,"Something Went wrong")
            return redirect("Setting_Module")
    return redirect("Setting_Module")

@login_required(login_url='SignIn')
def SubScriptionPeriod_Delete(request,pk):
    batch = Subscription_Period.objects.get(id = pk).delete()
    messages.success(request,"Subscription period Data Deleted")
    return redirect("Setting_Module")

def SubscriptionTypeSave(request):
    if request.method == "POST":
        form = TypeSubsriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Subscription Type Saved")
            return redirect("Setting_Module")
        else:
            messages.error(request,"Something Went wrong")
            return redirect("Setting_Module")
    return redirect("Setting_Module")

@login_required(login_url='SignIn')
def SubScriptionType_Delete(request,pk):
    batch = TypeSubsription.objects.get(id = pk).delete()
    messages.success(request,"Subscription Type Deleted")
    return redirect("Setting_Module")


@login_required(login_url='SignIn')
def ChangePassword(request):
    if request.method == "POST":
        oldpass = request.POST["oldpassword"]
        newpass1 = request.POST['newpassword1']
        newpass2 = request.POST['newpassword2']
        user1 = authenticate(request,username = request.user.username,password = oldpass)
        if user1 is not None:
            if newpass1 == newpass2:
                user  = request.user 
                user.set_password(newpass1)
                user.save()
                messages.success(request, "Password Change Success Please Login To Continue..")
                return redirect("SignIn")
            else:
                messages.error(request, "Password not Matching..")
                return redirect("Setting_Module")
        else:
            messages.error(request, "Password is incorrect")
            return redirect("Setting_Module")

    return redirect("Setting_Module")

@login_required(login_url='SignIn')
def DeviceConfig(request,pk):
    conf = ConfigarationDB.objects.get(id = pk)
    if request.method == "POST":
        jwt = request.POST["jwtip"]
        jwt_port = request.POST["jwtport"]
        callip = request.POST["callip"]
        callport = request.POST["callport"]
        adminusr = request.POST["adminusr"]
        adminpswd = request.POST["adminpswd"]

        conf.JWT_IP = jwt
        conf.JWT_PORT = jwt_port
        conf.Call_Back_IP = callip
        conf.Call_Back_Port = callport
        conf.Admin_Username = adminusr
        conf.Admin_Password = adminpswd

        conf.save()
        messages.success(request,"Configuration data updated..")
        return redirect("Setting_Module")

    return redirect("Setting_Module")

    
    

@unautenticated_user
def SignIn(request):
    if request.method == "POST":
        uname = request.POST['uname']
        pswd = request.POST['pswd']
        user = authenticate(request, username=uname, password = pswd)
        if user is not None:
            login(request, user)
            return redirect("Home")
        else:
            messages.error(request, "User Name or Password Incorrect")
            return redirect("SignIn")
    return render(request,"login.html")

def SignOut(request):
    logout(request)
    return redirect(SignIn)

@login_required(login_url='SignIn')
def Search(request):
    if request.method == "POST":
        key = request.POST["key"]
        members1 = MemberData.objects.filter(First_Name__contains=key)
        members2 = MemberData.objects.filter(Last_Name__contains=key)
        members3 = MemberData.objects.filter(Mobile_Number__contains=key)
        
        # Combine all querysets
        all_members = list(members1) + list(members2) + list(members3)
        
        # Remove duplicates
        member = list(set(all_members))
        
        print(member)
        context = {
            "member": member
        }
        return render(request, "search.html", context)
    return render(request, "search.html")

def ViewAllActivities(request):
    notification_payments = Payment.objects.filter(Payment_Date__gte = start_date,Payment_Date__lte = end_date )
    context = {
        "notification_payments":notification_payments,
        "notificationcount":notification_payments.count(),

    }
    return render(request,'viewallactivities.html',context)
    
def EditBatch(request,pk):
    if request.method == "POST":
        batch = request.POST["batch"]
        time = request.POST["time"]

        bat = Batch_DB.objects.get(id = pk)
        bat.Batch_Name = batch
        bat.Batch_Time = time
        bat.save()
        messages.success(request, "Batch updated")
        return redirect("Setting_Module")


    return render(request,"editbatch.html")

def EditsubscriptionPeriod(request,pk):
    if request.method == "POST":
        Period = request.POST["peri"]
        Category = request.POST["ten"]

        bat = Subscription_Period.objects.get(id = pk)
        bat.Period = Period
        bat.Category = Category
        bat.save()
        messages.success(request, "Subscription Period Updated")
        return redirect("Setting_Module")

    return render(request,"editsubperiod.html")

def EditSub(request,pk):
    if request.method == "POST":
        sub = request.POST["sub"]
       
        bat = TypeSubsription.objects.get(id = pk)
        bat.Type = sub
        
        bat.save()
        messages.success(request, "Subscription  Updated")
        return redirect("Setting_Module")
     
    return render(request,"editsubscription.html")



# add new staff 

@allowed_users(allowed_roles=["admin",])
@login_required(login_url='SignIn')
def StaffDetails(request):
    users = User.objects.filter(groups__name='staff')
    if request.method == "POST":
        fname = request.POST['fname']
        uname = request.POST['uname']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request,"Password Do not matching....")
            return redirect("StaffDetails")
        elif User.objects.filter(username = uname).exists():
            messages.error(request,"Username already exists please try different username..")
            return redirect("StaffDetails")
        else:
            user = User.objects.create_user(first_name = fname, username = uname, password = password1)
            user.save()
            group = Group.objects.get(name='staff')
            user.groups.add(group)
            messages.success(request,"New Staff Created Please save password {}".format(password1))
            return redirect("StaffDetails")
    context = {
        "users":users
    } 
        
    return render(request,'usermanagement.html',context)

@allowed_users(allowed_roles=["admin",])
@login_required(login_url='SignIn')
def DeleteStaffUser(request,pk):
    User.objects.get(id = pk).delete()
    messages.info(request,"User Deleted...")
    return redirect("StaffDetails")


# support for users 

def Supports(request):
    if request.method == "POST":
        name = request.POST['name']
        quary = request.POST['qury']

        support = Support.objects.create(name = name,Quary = quary)
        support.save()

        mail_subject = 'Ticket Generated - EMMY- FITNESS'
        message = render_to_string('emailbody.html', {'name': name,
                                                      "email":quary,
                                                      "date":datetime.now(),
                                                      "message":quary,
                                                      "id":support.id
                                                      })

        email = EmailMessage(mail_subject, message, to=['gopinath.pramod@gmail.com','support@reddefend.ae'])
        email.send(fail_silently=True)
        
        messages.info(request,"Support mail Sent")
        return redirect("Supports")

    return render(request,"support.html")


# bulk upadte validated data 

# Additional view for template download
import pandas as pd
import io
from django.http import HttpResponse
from django.views import View

class DownloadTemplateView(View):
    def get(self, request):
        # Create a template DataFrame with column headers
        columns = [
            'First_Name', 'Last_Name', 'Date_Of_Birth', 'Gender', 
            'Mobile_Number', 'Discount', 'Special_Discount', 'Email',
            'Address', 'Medical_History', 'Registration_Date',
            'Active_status', 'Access_status', 'Access_Token_Id'
        ]
        
        # Create an empty DataFrame with just the headers
        df = pd.DataFrame(columns=columns)
        
        # Add one example row (optional)
        example_data = {
            'First_Name': 'John',  # Required
            'Last_Name': 'Doe',
            'Date_Of_Birth': '1990-01-01',
            'Gender': 'Male',
            'Mobile_Number': '1234567890',  # Required
            'Discount': 10.0,
            'Special_Discount': False,
            'Email': 'john.doe@example.com',
            'Address': '123 Main St',
            'Medical_History': 'None',
            'Registration_Date': '2023-01-01',  # Required
            'Active_status': True,
            'Access_status': False,
            'Access_Token_Id': ''
        }
        df = pd.concat([df, pd.DataFrame([example_data])], ignore_index=True)
        
        # Create a buffer for the Excel file
        buffer = io.BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Template', index=False)
            
            # Get the workbook and the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Template']
            
            # Add formats for highlighting required fields
            required_format = workbook.add_format({'bold': True, 'bg_color': '#FFC7CE'})
            
            # Apply formats to required columns
            for col_num, column in enumerate(df.columns):
                if column in ['First_Name', 'Mobile_Number', 'Registration_Date']:
                    worksheet.set_column(col_num, col_num, 15, required_format)
                else:
                    worksheet.set_column(col_num, col_num, 15)
        
        # Reset buffer position
        buffer.seek(0)
        
        # Create response
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=member_data_template.xlsx'
        
        return response

# Add to urls.py
# ,
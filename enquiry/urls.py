from django.urls import path 
from .import views

urlpatterns = [
    path("enquiry/dashboard", views.enquiries,name="enquiries"),
    path('todays-followups/', views.todays_followups, name='todays_followups'),
     path('', views.enquiry_list, name='enquiry_list'),
    path('create/', views.enquiry_create, name='enquiry_create'),
    path('<int:pk>/', views.enquiry_detail, name='enquiry_detail'),
    path('<int:pk>/update/', views.enquiry_update, name='enquiry_update'),
    path('<int:pk>/add-status/', views.add_status_update, name='add_status_update'),
    path('register/', views.public_enrolment, name='public_enrolment'),
    path('download-qr-pdf/', views.download_qr_pdf, name='download_qr_pdf'),
    path('<int:pk>/convert/', views.convert_to_member, name='convert_to_member'),
]
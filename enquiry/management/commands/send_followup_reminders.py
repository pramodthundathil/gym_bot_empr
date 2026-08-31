from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ...models import EnquiryData # Replace 'your_app' with your actual app name
from Members.models import Subscription, MemberData  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Send follow-up emails for enquiries and subscription expiry reminders for members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--enquiry-only',
            action='store_true',
            help='Send only enquiry follow-ups',
        )
        parser.add_argument(
            '--subscription-only',
            action='store_true',
            help='Send only subscription reminders',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Starting Automated Reminder System'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Run both by default, or specific ones based on arguments
        run_enquiry = not options['subscription_only']
        run_subscription = not options['enquiry_only']
        
        total_sent = 0
        
        if run_enquiry:
            self.stdout.write('\n' + self.style.WARNING('>>> Processing Enquiry Follow-ups...'))
            enquiry_count = self.process_enquiry_followups()
            total_sent += enquiry_count
            self.stdout.write(self.style.SUCCESS(f'✓ Enquiry follow-ups sent: {enquiry_count}\n'))
        
        if run_subscription:
            self.stdout.write(self.style.WARNING('>>> Processing Subscription Reminders...'))
            subscription_count = self.process_subscription_reminders()
            total_sent += subscription_count
            self.stdout.write(self.style.SUCCESS(f'✓ Subscription reminders sent: {subscription_count}\n'))
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'TOTAL REMINDERS SENT: {total_sent}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
    
    # ============================================================================
    # ENQUIRY FOLLOW-UP SECTION
    # ============================================================================
    
    def process_enquiry_followups(self):
        """Process and send enquiry follow-ups"""
        today = timezone.now().date()
        pending_enquiries = EnquiryData.objects.filter(status='pending')
        
        sent_count = 0
        skipped_count = 0
        
        for enquiry in pending_enquiries:
            days_since_creation = (today - enquiry.date_created).days
            
            # Skip if more than 30 days old
            if days_since_creation > 30:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⊘ Skipping {enquiry.name} - More than 30 days old'
                    )
                )
                skipped_count += 1
                continue
            
            # Determine if we should send follow-up today
            should_send = False
            
            if enquiry.last_follow_up_date is None:
                if days_since_creation >= 3:
                    should_send = True
            else:
                days_since_last_followup = (today - enquiry.last_follow_up_date).days
                if days_since_last_followup >= 3:
                    should_send = True
            
            if should_send:
                # Send email
                if enquiry.email:
                    self.send_enquiry_email(enquiry)
                
                # Send SMS
                self.send_enquiry_sms(enquiry)
                
                # Update follow-up information
                enquiry.number_of_followup += 1
                enquiry.last_follow_up_date = today
                enquiry.next_follow_up_date = today + timedelta(days=3)
                enquiry.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Sent follow-up #{enquiry.number_of_followup} to {enquiry.name}'
                    )
                )
                sent_count += 1
            else:
                skipped_count += 1
        
        return sent_count
    
    def send_enquiry_email(self, enquiry):
        """Send follow-up email to enquiry"""
        subject = f'Your Fitness Journey Awaits - Follow-up #{enquiry.number_of_followup + 1}'
        
        # Plain text version
        text_content = f"""
                Hi {enquiry.name},

                We noticed you showed interest in joining Strength Base Fitness Center on {enquiry.date_created.strftime('%B %d, %Y')}.

                This is your Follow-up #{enquiry.number_of_followup + 1}, and we're here to answer any questions you might have.

                Why Choose Us?
                - State-of-the-art equipment
                - Certified personal trainers
                - Customized workout plans
                - Flexible membership options
                - Group fitness classes

                Visit us at:
                28/1613, Opp Heera Apartments
                Tank Bund Road, Chilavannur Rd
                Kochi, Kerala 682020

                Call us: +91 89214 07268

                Best regards,
                Strength Base Fitness Center Team
                        """
                        
        # HTML version
        html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
                    <table role="presentation" style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td align="center" style="padding: 20px 0;">
                                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    <tr>
                                        <td style="background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); padding: 40px 30px; text-align: center;">
                                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">
                                                STRENGTH BASE<br>FITNESS CENTER
                                            </h1>
                                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 14px; font-weight: 300;">
                                                Transform Your Body. Transform Your Life.
                                            </p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 40px 30px;">
                                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">
                                                Hi {enquiry.name},
                                            </h2>
                                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                                We noticed you showed interest in joining <strong>Strength Base Fitness Center</strong> on <strong>{enquiry.date_created.strftime('%B %d, %Y')}</strong>. We wanted to follow up and see if you're still interested in starting your fitness journey with us!
                                            </p>
                                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                                This is your <strong>Follow-up #{enquiry.number_of_followup + 1}</strong>, and we're here to answer any questions you might have.
                                            </p>
                                            <table role="presentation" style="width: 100%; margin: 30px 0; border-collapse: collapse; background-color: #fff8f0; border-left: 4px solid #ff6b35;">
                                                <tr>
                                                    <td style="padding: 20px;">
                                                        <h3 style="margin: 0 0 10px 0; color: #ff6b35; font-size: 18px;">
                                                            🎯 Why Choose Us?
                                                        </h3>
                                                        <ul style="margin: 0; padding-left: 20px; color: #666666; font-size: 15px; line-height: 1.8;">
                                                            <li>State-of-the-art equipment</li>
                                                            <li>Certified personal trainers</li>
                                                            <li>Customized workout plans</li>
                                                            <li>Flexible membership options</li>
                                                            <li>Group fitness classes</li>
                                                        </ul>
                                                    </td>
                                                </tr>
                                            </table>
                                            <table role="presentation" style="margin: 0 auto;">
                                                <tr>
                                                    <td align="center" style="border-radius: 5px; background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);">
                                                        <a href="tel:+918921407268" style="display: inline-block; padding: 15px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; text-transform: uppercase;">
                                                            Call Us Now
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="background-color: #f8f8f8; padding: 30px; border-top: 1px solid #e0e0e0;">
                                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.6; text-align: center;">
                                                📍 28/1613, Opp Heera Apartments, Tank Bund Road<br>
                                                Chilavannur Rd, Kochi, Kerala 682020
                                            </p>
                                            <p style="margin: 10px 0 0 0; color: #666666; font-size: 14px; text-align: center;">
                                                📞 <a href="tel:+918921407268" style="color: #ff6b35; text-decoration: none; font-weight: bold;">+91 89214 07268</a>
                                            </p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="background-color: #333333; padding: 20px 30px; text-align: center;">
                                            <p style="margin: 0; color: #ffffff; font-size: 12px;">
                                                © 2025 Strength Base Fitness Center. All rights reserved.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                        """
        
        try:
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [enquiry.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'  ✗ Failed to send email to {enquiry.email}: {str(e)}'
                )
            )
    
    def send_enquiry_sms(self, enquiry):
        """Send SMS to enquiry"""
        message_text = f"""Hi {enquiry.name},

                        Your fitness journey awaits at Strength Base Fitness Center! 

                        We're following up on your enquiry from {enquiry.date_created.strftime('%b %d')}.

                        Ready to transform? Call us: +91 89214 07268

                        Visit: Tank Bund Road, Chilavannur, Kochi

                        - Strength Base Fitness Center"""
        
        try:
            # SMS integration (uncomment and configure):
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message_text,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=f'+91{enquiry.phone_number}'
            # )
            pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'  ✗ Failed to send SMS to {enquiry.phone_number}: {str(e)}'
                )
            )
    
    # ============================================================================
    # SUBSCRIPTION REMINDER SECTION
    # ============================================================================
    
    def process_subscription_reminders(self):
        """Process and send subscription expiry reminders"""
        today = timezone.now().date()
        
        # Define reminder dates
        two_days_before = today + timedelta(days=2)
        same_day = today
        two_days_after = today - timedelta(days=2)
        
        sent_count = 0
        
        # Get subscriptions for each reminder type
        subscriptions_before = Subscription.objects.filter(
            Subscription_End_Date=two_days_before,
            Member__Active_status=True,
            Member__Email__isnull=False
        ).exclude(Member__Email='')
        
        subscriptions_today = Subscription.objects.filter(
            Subscription_End_Date=same_day,
            Member__Active_status=True,
            Member__Email__isnull=False
        ).exclude(Member__Email='')
        
        subscriptions_after = Subscription.objects.filter(
            Subscription_End_Date=two_days_after,
            Member__Active_status=True,
            Member__Email__isnull=False
        ).exclude(Member__Email='')
        
        # Send reminders 2 days before expiry
        for subscription in subscriptions_before:
            self.send_subscription_email(subscription, 'before')
            self.send_subscription_sms(subscription, 'before')
            sent_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Sent "2 days before" reminder to {subscription.Member.First_Name}'
                )
            )
        
        # Send reminders on expiry day
        for subscription in subscriptions_today:
            self.send_subscription_email(subscription, 'today')
            self.send_subscription_sms(subscription, 'today')
            sent_count += 1
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠ Sent "expiry today" reminder to {subscription.Member.First_Name}'
                )
            )
        
        # Send reminders 2 days after expiry
        for subscription in subscriptions_after:
            self.send_subscription_email(subscription, 'after')
            self.send_subscription_sms(subscription, 'after')
            sent_count += 1
            self.stdout.write(
                self.style.ERROR(
                    f'  ✗ Sent "2 days after expiry" reminder to {subscription.Member.First_Name}'
                )
            )
        
        return sent_count
    
    def send_subscription_email(self, subscription, reminder_type):
        """Send subscription expiry reminder email"""
        member = subscription.Member
        
        # Customize subject and content based on reminder type
        if reminder_type == 'before':
            subject = '⚠️ Your Gym Membership Expires in 2 Days!'
            urgency_message = 'Your membership will expire in just <strong>2 days</strong>.'
            action_text = 'Renew now to avoid any interruption in your fitness journey!'
            urgency_color = '#ff9800'
        elif reminder_type == 'today':
            subject = '🚨 Your Gym Membership Expires Today!'
            urgency_message = 'Your membership <strong>expires today</strong>.'
            action_text = 'Renew immediately to continue your access!'
            urgency_color = '#f44336'
        else:  # after
            subject = '❌ Your Gym Membership Has Expired'
            urgency_message = 'Your membership expired <strong>2 days ago</strong>.'
            action_text = 'Renew now to regain access to the gym!'
            urgency_color = '#d32f2f'
        
        # Plain text version
        text_content = f"""
        Hi {member.First_Name},

        {urgency_message.replace('<strong>', '').replace('</strong>', '')}

        Subscription Details:
        - Type: {subscription.Type_Of_Subscription}
        - Period: {subscription.Period_Of_Subscription}
        - End Date: {subscription.Subscription_End_Date.strftime('%B %d, %Y')}
        - Amount: ₹{subscription.Amount}

        {action_text}

        Visit us or call: +91 89214 07268

        Best regards,
        Strength Base Fitness Center
        28/1613, Opp Heera Apartments, Tank Bund Road
        Chilavannur Rd, Kochi, Kerala 682020
                """
                
                # HTML version
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 20px 0;">
                        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); padding: 40px 30px; text-align: center;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">
                                        STRENGTH BASE<br>FITNESS CENTER
                                    </h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: {urgency_color}; padding: 20px 30px; text-align: center;">
                                    <p style="margin: 0; color: #ffffff; font-size: 18px; font-weight: bold;">
                                        {urgency_message}
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">
                                        Hi {member.First_Name},
                                    </h2>
                                    <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                        {action_text}
                                    </p>
                                    <table role="presentation" style="width: 100%; margin: 30px 0; border-collapse: collapse; background-color: #f8f8f8; border-radius: 8px;">
                                        <tr>
                                            <td style="padding: 25px;">
                                                <h3 style="margin: 0 0 15px 0; color: #ff6b35; font-size: 18px;">
                                                    📋 Your Subscription Details
                                                </h3>
                                                <table style="width: 100%; border-collapse: collapse;">
                                                    <tr>
                                                        <td style="padding: 8px 0; color: #666666; font-size: 15px;">
                                                            <strong>Type:</strong>
                                                        </td>
                                                        <td style="padding: 8px 0; color: #333333; font-size: 15px;">
                                                            {subscription.Type_Of_Subscription}
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 8px 0; color: #666666; font-size: 15px;">
                                                            <strong>Period:</strong>
                                                        </td>
                                                        <td style="padding: 8px 0; color: #333333; font-size: 15px;">
                                                            {subscription.Period_Of_Subscription}
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 8px 0; color: #666666; font-size: 15px;">
                                                            <strong>End Date:</strong>
                                                        </td>
                                                        <td style="padding: 8px 0; color: #d32f2f; font-size: 15px; font-weight: bold;">
                                                            {subscription.Subscription_End_Date.strftime('%B %d, %Y')}
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 8px 0; color: #666666; font-size: 15px;">
                                                            <strong>Amount:</strong>
                                                        </td>
                                                        <td style="padding: 8px 0; color: #333333; font-size: 15px;">
                                                            ₹{subscription.Amount}
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    <table role="presentation" style="margin: 30px auto;">
                                        <tr>
                                            <td align="center" style="border-radius: 5px; background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);">
                                                <a href="tel:+918921407268" style="display: inline-block; padding: 15px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; text-transform: uppercase;">
                                                    Renew Now
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    <p style="margin: 25px 0 0 0; color: #999999; font-size: 14px; line-height: 1.6; text-align: center;">
                                        Don't let your fitness goals take a break!<br>
                                        Contact us today to renew your membership.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f8f8f8; padding: 30px; border-top: 1px solid #e0e0e0;">
                                    <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.6; text-align: center;">
                                        📍 28/1613, Opp Heera Apartments, Tank Bund Road<br>
                                        Chilavannur Rd, Kochi, Kerala 682020
                                    </p>
                                    <p style="margin: 10px 0 0 0; color: #666666; font-size: 14px; text-align: center;">
                                        📞 <a href="tel:+918921407268" style="color: #ff6b35; text-decoration: none; font-weight: bold;">+91 89214 07268</a>
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #333333; padding: 20px 30px; text-align: center;">
                                    <p style="margin: 0; color: #ffffff; font-size: 12px;">
                                        © 2025 Strength Base Fitness Center. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
                """
        
        try:
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [member.Email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'  ✗ Failed to send email to {member.Email}: {str(e)}'
                )
            )
    
    def send_subscription_sms(self, subscription, reminder_type):
        """Send subscription expiry reminder SMS"""
        member = subscription.Member
        
        # Customize message based on reminder type
        if reminder_type == 'before':
            message_text = f"""Hi {member.First_Name},

                            Your gym membership expires in 2 DAYS on {subscription.Subscription_End_Date.strftime('%d %b %Y')}.

                            Renew now: ₹{subscription.Amount}

                            Call: +91 89214 07268

                            - Strength Base Fitness Center"""
        elif reminder_type == 'today':
            message_text = f"""URGENT: Hi {member.First_Name},

                            Your gym membership EXPIRES TODAY!

                            Renew immediately to continue access.
                            Amount: ₹{subscription.Amount}

                            Call NOW: +91 89214 07268

                            - Strength Base Fitness Center"""
        else:  # after
            message_text = f"""Hi {member.First_Name},

                            Your gym membership EXPIRED on {subscription.Subscription_End_Date.strftime('%d %b %Y')}.

                            Renew now to regain access.
                            Amount: ₹{subscription.Amount}

                            Call: +91 89214 07268

                            - Strength Base Fitness Center"""
        
        try:
            # SMS integration (uncomment and configure):
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message_text,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=member.Mobile_Number
            # )
            pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'  ✗ Failed to send SMS to {member.Mobile_Number}: {str(e)}'
                )
            )
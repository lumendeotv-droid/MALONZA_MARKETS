
from django.http import response
from django.shortcuts import render
import requests
from django.core.mail import send_mail
from dict import settings
import logging
from .models import SiteUsers,ServicePayments,Course,CoursePayments
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import os
import json
from .notifications import sendsms
from dotenv import load_dotenv
load_dotenv()



# Create your views here.
def index(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        courses = Course.objects.all()
        return render(request,'index.html',{'courses': courses})
    courses = Course.objects.all()
    purchased_course_ids = CoursePayments.objects.filter(
        userId=user_id, 
        payment_status='completed'
    ).values_list('courseId', flat=True)
    return render(request,'index.html',{'courses': courses,'purchased_course_ids': purchased_course_ids})

def register(request):
    return render(request,'register.html')

def login(request):
    return render(request,"login.html")

def forgot(request):
    return render(request,"forgot.html")


def create_account(request):

    password1= request.POST.get('password1', False)
    password = request.POST.get('password', False)
    email = request.POST.get('email', False)
    phone = request.POST.get('phone', False)
    username = request.POST.get('username', False)
   


    if  password1 != password:
        message="the two passwords are diffrent."
        return render(request, "register.html", {"message": message})

        # Check if email and password are provided
    if not email or not password1:
        message="Email and password are required."
        return render(request, "register.html", {"message": message})

        # Check if user already exists
    if SiteUsers.objects.filter(email=email).exists():
        
        message="User with this email already exists.."
        return render(request, "register.html", {"message": message})

        # Create user
    user = SiteUsers.objects.create(email=email, password=password1,phone=phone,username=username)
    try:
        if phone.startswith('0'):
                phone = '254' + phone[1:]
                print(phone)
                sendsms(phone,"Thank you for registering  to MalonzoFx website. Explore to find more forex content. ")
        return redirect("/login")
    except Exception as e:
        print(f"Failed to send email. Error message: {str(e)}")
        return redirect("/login") 


def auth_login(request):
    email = request.POST.get('email',False)
    password = request.POST.get('password',False)

        # Check if an email and password are provided
    if not email or not password:
        
        message= "Email and password are required."
        return render(request, "login.html", {"message": message})

    try:
            # Check if user exists
        user = SiteUsers.objects.get(email=email,password=password)
    except SiteUsers.DoesNotExist:
        
        message= "User does not exist.You need to sign up please."
        return render(request, "login.html", {"message": message})

        # Check if password is correct
    if user.password != password:
        
        message= "You provided an incorrect password."
        return render(request, "login.html", {"message": message})

        # If everything is correct, respond with user details
    # Store the user ID in the session
    request.session['user_id'] = user.id
    print(user.id)
    return redirect('index')

def logout(request):
    user_id=request.session.get('user_id')
    if user_id is  not None:
        del request.session['user_id']
        return redirect("/index")
    else:
        return redirect("/index")
    
def payments(request,amount):
    user_id=request.session.get('user_id')
    

    if user_id is not None:

        usdprice=amount
        keprice=int(amount*130)
            
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        return render(request,"payments.html",{"usdprice":usdprice,"keprice":keprice})
    else:
        return redirect("/login")
    
def mpesa_checkout(request):
     #getting user id from session
    user_id=request.session.get('user_id')
    if user_id is not None:
        

        #getting saf number from form
        phone = request.POST.get('phone', False)
        #email of the user
        email = SiteUsers.objects.get(id=user_id).email
        #cost of course
        amountkes = request.session.get('keprice')
        usdprice = request.session.get('usdprice')
        print(amountkes)
       
        #print(amount)
        if phone.startswith('0'):
                phone = '254' + phone[1:]
                print(phone)
        if usdprice == 40:
            service = "SignalsPlan"
        elif usdprice == 150:
            service = "VirtualMentorshipPlan"
        elif usdprice == 250:
            service = "PhysicalMentorshipPlan"
        else:
            service = "UnknownPlan"
        payment_instance=ServicePayments.objects.create(mpesa_number=phone,email=email,amountkes=amountkes,service=service,userId=user_id)
        payment_instance.save()
        

        try:
                # Initialize the APIService
            token ="ISSecretKey_live_70f557a0-e944-4081-ba6e-6b8d9a6e2a9d"
            publishable_key = "ISPubKey_live_30463dc3-f15a-46e1-9a5c-851410a8882c"
            service = APIService(token=token, publishable_key=publishable_key, test=False)

                # Trigger M-Pesa STK Push
            response = service.collect.mpesa_stk_push(phone_number=phone, email=email,narrative="sendingcash", amount=amountkes,api_ref="servicepayments")
            print(response)
            
            
            

                # Return the response from the M-Pesa STK Push
            return render(request,"loading.html")

        except Exception as e:
                # Return an error if there's an exception
            return render(request,"index.html",{"error": "try again later "})
    else:
        return redirect('/login')

def CardPayments(request):
    #getting user id from session
    user_id=request.session.get('user_id')
    if user_id is not None:
       

        #getting saf number from form
       
        #email of the user
        email = SiteUsers.objects.get(id=user_id).email
        #cost of course
        usdprice = request.session.get('usdprice')
        

        if usdprice == 40:
            service = "SignalsPlan"
        elif usdprice == 150:
            service = "VirtualMentorshipPlan"
        elif usdprice == 250:
            service = "PhysicalMentorshipPlan"
        else:
            service = "UnknownPlan"
        
        
                
        payment_instance=ServicePayments.objects.create(email=email,amountusd=usdprice,service=service,userId=user_id)
        payment_instance.save()
        

        
        try:
            token ="ISSecretKey_live_70f557a0-e944-4081-ba6e-6b8d9a6e2a9d"
            publishable_key = "ISPubKey_live_30463dc3-f15a-46e1-9a5c-851410a8882c"
            
            service = APIService(token=token, publishable_key=publishable_key, test=False)

            response = service.collect.checkout(email=email, amount=usdprice, currency="USD", narrative="sendingcash",comment="Service Fees", redirect_url="https://mofreydigiversity.com/loading",api_ref="servicepayments")
            url=response.get("url")
            print(url)
            
            return redirect(url)

        except:
            return redirect("/index")
    else:
        return redirect("/login")
    
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  
def PaymentCallback(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data in the request."}, status=400)
    print(data)
    

        # Check if transaction state is complete
    if data["state"] == "COMPLETE"  and data["api_ref"] =="servicepayments":
        account = data["account"]  # Get the account information from data

        # Initialize phone and email variables with None
        phone = None
        email = None

        try:
            int_account = int(account)  # Try converting account to an integer
            phone = (int_account)    # Convert the integer to a character (assuming this is intended for phone number processing)
            print(phone)
        except ValueError:
            # If account is not an integer, treat it as an email
            email = account
            print(email)

        if phone is not None:
            # Process payments based on phone number
            try:
                payment_instance = ServicePayments.objects.filter(mpesa_number=phone).latest('id')
                payment_instance.payment_status = 'completed'
                payment_instance.save()

                keprice=payment_instance.amountkes
                service=payment_instance.service
                try:
                    if service == "SignalsPlan":
                        sendsms(phone, f"We have received your payment of {keprice} KES. Join the signals group using this link https://chat.whatsapp.com/EMTiQagGOkE5WErjXlczmR.")
                    if service == "VirtualMentorshipPlan":
                        sendsms(phone, f"We have received your payment of {keprice} KES. Join the virtual mentorship group using this link https://chat.whatsapp.com/EUOwIYg8su74r7dYo9nB3w.")
                    if service=='PhysicalMentorshipPlan':
                        # Send link to the physical classes link
                        sendsms(phone, f"We have received your payment of {keprice} KES. Join the physical class group and get all the info here https://chat.whatsapp.com/DfDCqerHYg3HHWqABV8c1j.")
                except Exception as e:
                    print(f"The error {e} occurred when sending the SMS.")
                
                

            except ServicePayments.DoesNotExist:
                return JsonResponse({"message": "No payment found for this phone number."})

        elif email is not None:
            # Process payments based on email
            try:
                payment_instance = ServicePayments.objects.filter(email=email).latest('id')
                payment_instance.payment_status = 'completed'
                payment_instance.payment_method = 'card'
                payment_instance.save()

                usdprice=payment_instance.amountusd
                service=payment_instance.service
                try:
                    phone = SiteUsers.objects.get(email=email).phone
                    if phone.startswith('0'):
                        phone = '254' + phone[1:]
                        print(phone)
                        
                    if service == "SignalsPlan":
                        sendsms(phone, f"We have received your payment of {usdprice} $ - join the signals group using this link https://chat.whatsapp.com/EMTiQagGOkE5WErjXlczmR.")
                    elif service == "VirtualMentorshipPlan":
                        sendsms(phone, f"We have received your payment of {usdprice} $ - join the virtual mentorship group using this link https://chat.whatsapp.com/EUOwIYg8su74r7dYo9nB3w.")
                    else:
                        # Send link to the physical classes link
                        sendsms(phone, f"We have received your payment of {usdprice} $ - join the physical class group and get all the info here https://chat.whatsapp.com/DfDCqerHYg3HHWqABV8c1j.")
                except Exception as e:
                    print(f"The error {e} occurred when sending SMS")
                

                
                
                

            except ServicePayments.DoesNotExist:
                return JsonResponse({"message": "No payment found for this email."})

        else:
            return JsonResponse({"message": "No email or phone provided."})
    elif data["state"] == "COMPLETE" and data["api_ref"] =="coursepayments":
        account = data["account"]  # Get the account information from data

        # Initialize phone and email variables with None
        phone = None
        email = None

        try:
            int_account = int(account)  # Try converting account to an integer
            phone = (int_account)    # Convert the integer to a character (assuming this is intended for phone number processing)
            print(phone)
        except ValueError:
            # If account is not an integer, treat it as an email
            email = account
            print(email)

        if phone is not None:
            # Process payments based on phone number
            try:
                payment_instance = CoursePayments.objects.filter(mpesa_number=phone).latest('id')
                payment_instance.payment_status = 'completed'
                payment_instance.save()

                try:
                    keprice=payment_instance.amountkes
                    sendsms(phone,f"you have paid {keprice} KES you can now download the pdf from the website")
                except Exception as e:
                    print("this error ",e,"occured when sending email")
                

            except CoursePayments.DoesNotExist:
                return JsonResponse({"message": "No payment found for this phone number."})

        elif email is not None:
            # Process payments based on email
            try:
                payment_instance = CoursePayments.objects.filter(email=email).latest('id')
                payment_instance.payment_status = 'completed'
                payment_instance.payment_method = 'card'
                payment_instance.save()
                try:
                    usdprice=payment_instance.amountusd
                    phone=SiteUsers.objects.get(email=email).phone
                    if phone.startswith('0'):
                        phone = '254' + phone[1:]
                        print(phone)
                    sendsms(phone,f"we have received your payment of {usdprice} $ you can now download the resource from the website")
                except Exception as e:
                    print("got error ",e,"when sending sms")

                

            except CoursePayments.DoesNotExist:
                return JsonResponse({"message": "No payment found for this email."})

        else:
            return JsonResponse({"message": "No email or phone provided."})

        
    

        
    else:
        return JsonResponse({"message": "Transaction state is not complete."})
    

def coursepayments(request,amount,course_id):
    user_id=request.session.get('user_id')
    

    if user_id is not None:

        usdprice=amount
        keprice=int(amount*130)
            
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['courseId']= course_id
        return render(request,"payment.html",{"usdprice":usdprice,"keprice":keprice})
    else:
        return redirect("/login")


def course_mpesa_checkout(request):
     #getting user id from session
    user_id=request.session.get('user_id')
    if user_id is not None:
        

        #getting saf number from form
        phone = request.POST.get('phone', False)
        #email of the user
        email = SiteUsers.objects.get(id=user_id).email
        #cost of course
        amountkes = request.session.get('keprice')
        print(amountkes)
        courseid = request.session.get('courseId')
        print("course id is ",courseid)
        #print(amount)
        if phone.startswith('0'):
                phone = '254' + phone[1:]
                print(phone)
                
        try:
            payment_instance = CoursePayments.objects.create(
                mpesa_number=phone,
                email=email,
                amountkes=amountkes,
                courseId=courseid,
                userId=user_id
            )
            payment_instance.save()
            print("Payment instance saved successfully")
        except Exception as e:
            print(f"Error saving payment instance: {e}")

        

        try:
                # Initialize the APIService
            print("test1")
            token ="ISSecretKey_live_70f557a0-e944-4081-ba6e-6b8d9a6e2a9d"
            publishable_key = "ISPubKey_live_30463dc3-f15a-46e1-9a5c-851410a8882c"
            service = APIService(token=token, publishable_key=publishable_key, test=False)
            print("test2")

                # Trigger M-Pesa STK Push
            response = service.collect.mpesa_stk_push(phone_number=phone, email=email, amount=amountkes,narrative="sendingcash", api_ref="coursepayments")
            print(response)
            
            
            

                # Return the response from the M-Pesa STK Push
            return render(request,"loading.html")

        except Exception as e:
                # Return an error if there's an exception
            return render(request,"index.html",{"error": "try again later "})
    else:
        return redirect('/login')



def course_cardPayments(request):
    #getting user id from session
    user_id=request.session.get('user_id')
    if user_id is not None:
       

        #getting saf number from form
        #phone = request.POST.get('phone', False)
        #email of the user
        email = SiteUsers.objects.get(id=user_id).email
        #cost of course
        amountusd = request.session.get('usdprice')
      
        courseid = request.session.get('courseId')
        
        
                
        payment_instance=CoursePayments.objects.create(email=email,amountusd=amountusd,courseId=courseid,userId=user_id,narrative="sendcash")
        payment_instance.save()
        

        
        try:
            publishable_key = os.getenv('publishable_key')
            
            token = os.getenv('token')
            
            service = APIService(token=token, publishable_key=publishable_key, test=False)

            response = service.collect.checkout(email=email, amount=amountusd, currency="USD", comment="Service Fees", redirect_url="https://mofreydigiversity.com/loading",api_ref="coursepayments")
            url=response.get("url")
            print(url)
            
            return redirect(url)

        except:
            return redirect("/index")
    else:
        return redirect("/login")
 
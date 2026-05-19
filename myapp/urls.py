from django.urls import path, register_converter
from.import views
from .converter import FloatConverter
register_converter(FloatConverter, 'float')

urlpatterns = [
    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('forgot',views.forgot,name='forgot'),
    path('create_account',views.create_account,name='create_account'),
    path('auth_login',views.auth_login,name='auth_login'),
    path('logout',views.logout,name='logout'),
    path('payments/<float:amount>', views.payments, name='payments'),
    path('mpesa_checkout',views.mpesa_checkout,name='mpesa_checkout'),
    path('card_checkout',views.CardPayments,name="card_checkout"),
    path('paymentProcessing',views.PaymentCallback,name='paymentProcessing'),
    path('coursepayments/<float:amount>/<int:course_id>/', views.coursepayments, name='coursepayments'),
    path('course_mpesa_checkout',views.course_mpesa_checkout,name='course_mpesa_checkout'),
    path('course_card_checkout',views.course_cardPayments,name="course_card_checkout"),
   
   
]

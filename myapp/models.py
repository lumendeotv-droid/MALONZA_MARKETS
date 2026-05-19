
from django.db import models
from django.utils.timezone import now

class SiteUsers (models.Model):
    email=models.EmailField()
    password=password = models.TextField() 
    username=models.CharField(max_length=30)
    phone=models.CharField(max_length=30)

    def __str__(self):
        return f'{self.email} :{self.username}'
    
class ServicePayments(models.Model):
    email=models.EmailField()
    service=models.CharField(max_length=100)
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20,default='initialized')
    payment_method = models.CharField(max_length=20,default='mpesa')

class CoursePayments(models.Model):
    email=models.EmailField()
    courseId=models.IntegerField()
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20,default='initialized')
    payment_method = models.CharField(max_length=20,default='mpesa')

class Course(models.Model):
    title = models.CharField(max_length=255)
    priceusd=models.FloatField(default=0.0)
    image = models.ImageField(upload_to='images/')
    pdf = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.title




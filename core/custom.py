# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.db.models.signals import post_save
# from django.dispatch import receiver 

# # Create your models here.

# class CustomUser(AbstractUser):
# 	user_type_choice = ((1,"Administrator"), (2,"Manager"), (3,"User"))
# 	user_type = models.CharField(default=1, choices=user_type_choice, max_length=14)

# class Admin(models.Model):
# 	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
# 	firstname = models.CharField(max_length=30)
# 	lastname = models.CharField(max_length=30)
# 	telephone = models.IntegerField()
# 	address = models.TextField()
# 	zipcode = models.IntegerField()
# 	city = models.CharField(max_length=20)
# 	region = models.CharField(max_length=20)
# 	country = models.CharField(max_length=20)
# 	additional_address = models.CharField(max_length=30)
# 	email = models.EmailField()
# 	picture = models.ImageField(upload_to='images/admin')
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)

# 	def __str__(self):
# 		return self.email

# class Manager(models.Model):
# 	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
# 	firstname = models.CharField(max_length=30)
# 	lastname = models.CharField(max_length=30)
# 	telephone = models.IntegerField()
# 	address = models.TextField()
# 	zipcode = models.IntegerField()
# 	city = models.CharField(max_length=20)
# 	region = models.CharField(max_length=20)
# 	country = models.CharField(max_length=20)
# 	additional_address = models.CharField(max_length=30)
# 	email = models.EmailField()
# 	picture = models.ImageField(upload_to='images/manager')
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)

# 	def __str__(self):
# 		return self.email

# class Station(models.Model):

# 	STATION_STATUS = (
# 			(1, "pending"),
# 			(2, "declined"),
# 			(3, "active"),
# 			(4, "blocked")
# 		)

# 	name = models.CharField(max_length=20)
# 	description = models.TextField()
# 	address = models.TextField()
# 	zipcode = models.IntegerField()
# 	city = models.CharField(max_length=20)
# 	region = models.CharField(max_length=20)
# 	country = models.CharField(max_length=20)
# 	ipaddress = models.CharField(max_length=20)
# 	macaddress = models.CharField(max_length=20)
# 	cigarettecounter = models.IntegerField()
# 	status = models.CharField(default=1, choices=STATION_STATUS, max_length=10)

# 	def __str__(self):
# 		return self.name

# class Transaction(models.Model):

# 	TRANSACTION_STATUS = (
# 			(1, "pending"),
# 			(1, "declined"),
# 			(1, "completed")
# 		)

# 	cigarettecounter = models.IntegerField()
# 	price = models.FloatField()
# 	videolink = models.URLField()
# 	status = models.CharField(default=1 ,choices=TRANSACTION_STATUS, max_length=10)
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)
# 	station = models.ForeignKey(Station, on_delete=models.CASCADE)
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)

# 	def __str__(self):
# 		return self.id

# class Error(models.Model):

# 	ERROR_CHOICE = (
# 			(1, "unsolved"),
# 			(1, "solved"),
# 		)

# 	code = models.CharField(max_length=10)
# 	description = models.TextField()
# 	status = models.CharField(default=1, choices=ERROR_CHOICE, max_length=10)
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)
# 	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
# 	station = models.ForeignKey(Station, on_delete=models.CASCADE)
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)

# 	def __str__(self):
# 		return self.code

# class Solution(models.Model):
# 	description = models.TextField()
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	error = models.ForeignKey(Error, on_delete=models.CASCADE)

# 	def __str__(self):
# 		self.id 

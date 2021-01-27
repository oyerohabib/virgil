from django import forms
from django.forms import ModelForm
from .models import *
from crispy_forms.helper import FormHelper

class StationForm(ModelForm):
	class Meta:
		model = Station
		fields = '__all__'

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['firstname', 'lastname', 'email', 'password', 'telephone', 'address', 
		'zipcode', 'city', 'region', 'country', 'additional_address', 'picture']
		widgets = {
			'password': forms.PasswordInput()
		}

class ProfileForm(ModelForm):
	class Meta:
		model = User
		fields = ['firstname', 'lastname', 'telephone', 'address', 
		'zipcode', 'city', 'region', 'country', 'additional_address', 'picture']

class UpdateErrorForm(ModelForm):
	class Meta:
		model = Error
		fields = ['status', 'description']

class UpdateSolutionForm(ModelForm):
	class Meta:
		model = Solution
		fields = ['description']

class UpdateTransactionForm(ModelForm):
	class Meta:
		model = Transaction
		fields = ['comment', 'status']
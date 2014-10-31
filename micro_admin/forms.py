from django import forms
from django.forms import ModelForm
from micro_admin.models import Branch, User

class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ['name', 'opening_date', 'country', 'state', 'district', 'city', 'area', 'phone_number', 'pincode']


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'gender', 'branch', 'user_roles', 'username', 'password']


class EditbranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ['country', 'state', 'district', 'city', 'area', 'phone_number', 'pincode']

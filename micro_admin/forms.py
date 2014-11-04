from django import forms
from django.forms import ModelForm
from micro_admin.models import Branch, User, Group, Client


class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ["name", "opening_date", "country", "state", "district", "city", "area", "phone_number", "pincode"]


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", "first_name", "gender", "branch", "user_roles", "username", "password"]


class EditbranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ["country", "state", "district", "city", "area", "phone_number", "pincode"]


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["name", "account_type", "account_number", "activation_date", "branch"]


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "account_type", "date_of_birth", "joined_date", "branch", "account_number", "gender", "client_role", "occupation", "annual_income", "country", "state","district", "city", "area"]


class EditclientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["client_role", "occupation", "annual_income", "country", "state","district", "city", "area"]
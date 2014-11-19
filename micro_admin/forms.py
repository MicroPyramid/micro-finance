from django import forms
from django.forms import ModelForm
from micro_admin.models import Branch, User, Group, Client, SavingsAccount, LoanAccount


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
        fields = ["name", "account_number", "activation_date", "branch"]


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "date_of_birth", "joined_date", "branch", "account_number", "gender", "client_role", "occupation", "annual_income", "country", "state","district", "city", "area"]


class AddMemberForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["clients"]


class EditclientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["client_role", "occupation", "annual_income", "country", "state","district", "city", "area"]


class GroupSavingsAccountForm(forms.ModelForm):

    class Meta:
        model = SavingsAccount
        fields = ["account_no", "opening_date", "min_required_balance", "savings_balance", "annual_interest_rate"]


class GroupLoanAccountForm(forms.ModelForm):

    class Meta:
        model = LoanAccount
        fields = ["account_no", "loan_amount", "loan_repayment_period", "loan_repayment_every", "annual_interest_rate", "loanpurpose_description"]
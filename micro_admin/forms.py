from django import forms
from micro_admin.models import (
    Branch, User, Group, Client, SavingsAccount, LoanAccount, FixedDeposits, Receipts, Payments, RecurringDeposits, GroupMeetings,
    ClientBranchTransfer)
# from django.core.exceptions import ObjectDoesNotExist
# import datetime
import decimal

d = decimal.Decimal


class UpdateClientProfileForm(forms.Form):
    photo = forms.FileField()
    signature = forms.FileField()

    def __init__(self, instance, *args, **kwargs):
        super(UpdateClientProfileForm, self).__init__(*args, **kwargs)


class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ["name", "opening_date", "country", "state", "district",
                  "city", "area", "phone_number", "pincode"]

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            try:
                if int(pincode):
                    check_pin = str(pincode)
                    if not len(check_pin) == 6:
                        raise forms.ValidationError(
                            'Please enter a valid 6 digit pincode')
            except ValueError:
                raise forms.ValidationError(
                    'Please enter a valid pincode')
        return pincode

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        try:
            if phone_number is not None:
                if int(phone_number):
                    check_phone = str(phone_number)
                    if not phone_number or not(len(check_phone) == 10):
                        raise forms.ValidationError(
                            'Please enter a valid 10 digit phone number')
                    return phone_number
        except ValueError:
            raise forms.ValidationError('Please enter a valid phone number')


class UserForm(forms.ModelForm):

    date_of_birth = forms.DateField(
        required=False,
        input_formats=['%m/%d/%Y'])
    password = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", 'last_name', "gender", "branch",
                  "user_roles", "username", 'country', 'state',
                  'district', 'city', 'area', 'mobile', 'pincode']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['gender'].widget.attrs\
            .update({
                'placeholder': 'Gender',
                'class': 'text-box wid-form select-box-pad'
            })
        not_required_fields = ['country', 'state', 'district',
                               'city', 'area', 'mobile',
                               'pincode', 'last_name']
        for field in not_required_fields:
            self.fields[field].required = False
        if not self.instance.pk:
            self.fields['password'].required = True

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 5:
                raise forms.ValidationError(
                    'Password must be at least 5 characters long!')
        return password

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            try:
                if int(pincode):
                    check_pin = str(pincode)
                    if not len(check_pin) == 6:
                        raise forms.ValidationError(
                            'Please enter a valid 6 digit pincode')
            except ValueError:
                raise forms.ValidationError(
                    'Please enter a valid pincode')
        return pincode

    def clean_mobile(self):
        phone_number = self.cleaned_data.get('mobile')
        try:
            if phone_number is not None:
                if int(phone_number):
                    check_phone = str(phone_number)
                    if not phone_number or not(len(check_phone) == 10):
                        raise forms.ValidationError(
                            'Please enter a valid 10 digit phone number')
                    return phone_number
        except ValueError:
            raise forms.ValidationError('Please enter a valid phone number')

    def save(self, commit=True, *args, **kwargs):
        instance = super(UserForm, self).save(commit=False, *args, **kwargs)
        if not instance.id:
            instance.pincode = self.cleaned_data.get('pincode')
            instance.set_password(self.cleaned_data.get('password'))
        if commit:
            instance.save()
        return instance


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["name", "account_number", "activation_date", "branch"]


class ClientForm(forms.ModelForm):
    created_by = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "date_of_birth", "joined_date",
                  "account_number", "gender", "client_role", "occupation",
                  "annual_income", "country", "state", "district", "city",
                  "area", "mobile", "pincode", "branch", 'blood_group',
                  'email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.client = kwargs.pop('client', None)
        super(ClientForm, self).__init__(*args, **kwargs)
        not_required = ['blood_group', 'email']
        for field in not_required:
            self.fields[field].required = False

    def clean_mobile(self):
        phone_number = self.cleaned_data.get('mobile')
        try:
            if int(phone_number):
                check_phone = str(phone_number)
                if not phone_number or not(len(check_phone) == 10):
                    raise forms.ValidationError(
                        'Please enter a valid 10 digit phone number')
                return phone_number
        except ValueError:
            raise forms.ValidationError('Please enter a valid phone number')

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            try:
                if int(pincode):
                    check_pin = str(pincode)
                    if not len(check_pin) == 6:
                        raise forms.ValidationError(
                            'Please enter a valid 6 digit pincode')
            except ValueError:
                raise forms.ValidationError(
                    'Please enter a valid pincode')
        return pincode

    def clean_branch(self):
        if self.instance.id:
            if self.instance.branch != self.cleaned_data.get('branch'):
                loan_account_filter = LoanAccount.objects.filter(client=self.instance).exclude(status='Closed').exclude(status='Withdrawn')
                group_account_filter = Group.objects.filter(clients=self.instance)
                if group_account_filter:
                    group_account = group_account_filter.first()
                    group_loan_accounts = LoanAccount.objects.filter(group=group_account).exclude(status='Closed').exclude(status='Withdrawn')
                    if group_loan_accounts:
                        loan_account = group_loan_accounts.first()
                        if loan_account.status == 'Applied':
                            raise forms.ValidationError(
                                "This client has a Group loan A/C in Applied status. So, can't be moved to another branch until it is withdrawn/closed.")
                        elif loan_account.status == 'Approved':
                            raise forms.ValidationError(
                                "This client has a Group loan A/C in Approved status. So, can't be moved to another branch until it is withdrawn/closed.")
                        elif loan_account.status == 'Rejected':
                            raise forms.ValidationError(
                                "This client has a Group loan A/C in Rejected status. So, can't be moved to another branch until it is withdrawn/closed.")
                        raise forms.ValidationError(
                            "This client has a Group loan A/C. So, can't be moved to another branch until it is withdrawn/closed.")

                if loan_account_filter:
                    loan_account = loan_account_filter.first()
                    if loan_account.status == 'Applied':
                        raise forms.ValidationError(
                            "This client has a Personal loan A/C in Applied status. So, can't be moved to another branch until it is withdrawn/closed.")
                    elif loan_account.status == 'Approved':
                        raise forms.ValidationError(
                            "This client has a Personal loan A/C in Approved status. So, can't be moved to another branch until it is withdrawn/closed.")
                    elif loan_account.status == 'Rejected':
                        raise forms.ValidationError(
                            "This client has a Personal loan A/C in Rejected status. So, can't be moved to another branch until it is withdrawn/closed.")
                    raise forms.ValidationError(
                        "This client has a Personal loan A/C. So, can't be moved to another branch until it is withdrawn/closed.")
        return self.cleaned_data.get('branch')

    def save(self, commit=True, *args, **kwargs):
        instance = super(ClientForm, self).save(commit=False, *args, **kwargs)
        # instance.created_by = User.objects.filter(
        #     username=self.cleaned_data.get('created_by')).first()

        if instance.id:
            if self.client.branch != self.cleaned_data.get('branch'):
                ClientBranchTransfer.objects.create(
                    client=instance, from_branch=self.client.branch,
                    to_branch=self.cleaned_data.get('branch'),
                    changed_by=self.user)
        if commit:
            instance.save()
        return instance


class AddMemberForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["clients"]


class SavingsAccountForm(forms.ModelForm):

    class Meta:
        model = SavingsAccount
        fields = ["account_no", "opening_date", "min_required_balance",
                  "annual_interest_rate"]


class LoanAccountForm(forms.ModelForm):

    class Meta:
        model = LoanAccount
        fields = ["account_no", "interest_type", "loan_amount",
                  "loan_repayment_period", "loan_repayment_every",
                  "annual_interest_rate", "loanpurpose_description"]

    def clean_loan_repayment_period(self):
        if self.data.get("loan_repayment_period") and self.data.get("loan_repayment_every"):
            if int(self.data.get("loan_repayment_period")) > int(self.data.get("loan_repayment_every")):
                return self.data.get("loan_repayment_period")
            else:
                raise forms.ValidationError("Loan Repayment Period should be greater than Loan Repayment Every")


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipts
        fields = ["date", "branch", "receipt_number"]


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payments
        fields = ["branch", "voucher_number", "payment_type", "amount", "interest", "total_amount", "totalamount_in_words"]


class FixedDepositForm(forms.ModelForm):

    client_name = forms.CharField(max_length=50, required=True)
    client_account_no = forms.CharField(max_length=50, required=True)

    class Meta:
        model = FixedDeposits
        fields = ["nominee_firstname", "nominee_lastname",
                  "nominee_occupation", "fixed_deposit_number",
                  "deposited_date", "fixed_deposit_amount",
                  "fixed_deposit_period", "fixed_deposit_interest_rate",
                  "relationship_with_nominee", "nominee_photo",
                  "nominee_signature", "nominee_gender",
                  "nominee_date_of_birth"]

    def clean_client_account_no(self):
        self.client = Client.objects.filter(
            first_name__iexact=self.cleaned_data.get("client_name"),
            account_number=self.cleaned_data.get("client_account_no")
        ).first()
        if not self.client:
            raise forms.ValidationError("No Member exist with this First Name and Account Number.")
        return self.cleaned_data.get("client_account_no")


class ReccuringDepositForm(forms.ModelForm):

    client_name = forms.CharField(max_length=50, required=True)
    client_account_no = forms.CharField(max_length=50, required=True)

    class Meta:
        model = RecurringDeposits
        fields = ["nominee_firstname", "nominee_lastname",
                  "nominee_occupation", "nominee_gender",
                  "reccuring_deposit_number", "deposited_date",
                  "recurring_deposit_amount", "recurring_deposit_period",
                  "recurring_deposit_interest_rate",
                  "relationship_with_nominee",
                  "nominee_photo", "nominee_signature",
                  "nominee_date_of_birth"]

    def clean_client_account_no(self):
        self.client = Client.objects.filter(
            first_name__iexact=self.cleaned_data.get("client_name"),
            account_number=self.cleaned_data.get("client_account_no")
        ).first()
        if not self.client:
            raise forms.ValidationError("No Member exist with this First Name and Account Number.")
        return self.cleaned_data.get("client_account_no")


class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(max_length=50, required=True)
    new_password = forms.CharField(max_length=50, required=True)
    confirm_new_password = forms.CharField(max_length=50, required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password")
        if not self.user.check_password(current):
            raise forms.ValidationError("Current Password is Invalid")
        return current

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if len(password) < 5:
            raise forms.ValidationError("Password must be at least 5 characters")
        return password

    def clean_confirm_new_password(self):
        password = self.cleaned_data.get("new_password")
        confirm = self.cleaned_data.get("confirm_new_password")
        if password != confirm:
            raise forms.ValidationError("Passwords does not match")
        return confirm


class GroupMeetingsForm(forms.ModelForm):

    class Meta:
        model = GroupMeetings
        fields = ["meeting_date", "meeting_time"]

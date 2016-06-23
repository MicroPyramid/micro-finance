from django import forms
from micro_admin.models import Branch, User, Group, Client, SavingsAccount,\
    LoanAccount, FixedDeposits, Receipts, Payments, RecurringDeposits


class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ["name", "opening_date", "country", "state", "district",
                  "city", "area", "phone_number", "pincode"]


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", "first_name", "gender", "branch", "user_roles",
                  "username", "password"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget.attrs\
            .update({
                'placeholder': 'Gender',
                'class': 'text-box wid-form select-box-pad'
            })


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["name", "account_number", "activation_date", "branch"]


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "date_of_birth", "joined_date",
                  "account_number", "gender", "client_role", "occupation",
                  "annual_income", "country", "state", "district", "city",
                  "area", "mobile", "pincode", "branch"]


class AddMemberForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["clients"]


class SavingsAccountForm(forms.ModelForm):

    class Meta:
        model = SavingsAccount
        fields = ["account_no", "opening_date", "min_required_balance",
                  "annual_interest_rate"]


class ClientLoanAccountForm(forms.ModelForm):

    class Meta:
        model = LoanAccount
        fields = ["account_no", "loan_amount", "interest_type",
                  "loan_repayment_period", "loan_repayment_every",
                  "annual_interest_rate", "loanpurpose_description"]


class LoanAccountForm(forms.ModelForm):

    class Meta:
        model = LoanAccount
        fields = ["account_no", "interest_type", "loan_amount",
                  "loan_repayment_period", "loan_repayment_every",
                  "annual_interest_rate", "loanpurpose_description"]


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipts
        fields = ["date", "branch", "receipt_number"]


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payments
        fields = ["date", "branch", "voucher_number", "payment_type",
                  "amount", "interest", "total_amount", "totalamount_in_words"]


class FixedDepositForm(forms.ModelForm):

    class Meta:
        model = FixedDeposits
        fields = ["nominee_firstname", "nominee_lastname",
                  "nominee_occupation", "fixed_deposit_number",
                  "deposited_date", "fixed_deposit_amount",
                  "fixed_deposit_period", "fixed_deposit_interest_rate",
                  "relationship_with_nominee", "nominee_photo",
                  "nominee_signature", "nominee_gender",
                  "nominee_date_of_birth"]


class ReccuringDepositForm(forms.ModelForm):

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

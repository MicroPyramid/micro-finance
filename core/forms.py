from micro_admin.models import (User, Client, Receipts, Payments, LoanAccount, Group,
                                SavingsAccount, FixedDeposits, RecurringDeposits, GroupMemberLoanAccount)
from django import forms
from django.core.validators import MinValueValidator
from django.forms.utils import ErrorList
import decimal
import datetime
import calendar
from django.conf import settings
from core.utils import send_email_template

d = decimal.Decimal


class ClientLoanAccountsForm(forms.Form):
    # fee
    loanprocessingfee_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    loanprinciple_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    loaninterest_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    # a/c
    name = forms.CharField(max_length=100, required=False)
    account_number = forms.CharField(max_length=100, required=False)

    def clean(self):
        self.client = None
        if not(self.cleaned_data.get("name") and self.cleaned_data.get("account_number")):
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please provide both  member first name, account number")
            raise forms.ValidationError(errors)
        self.client = Client.objects.filter(
            first_name__iexact=self.cleaned_data.get("name"),
            account_number=self.cleaned_data.get("account_number")
        ).last()
        if not self.client:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("No Client exists with this First Name and Account number.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class GetLoanDemandsForm(forms.Form):

    loan_account_no = forms.CharField(max_length=100, required=False)
    group_loan_account_no = forms.CharField(max_length=100, required=False)
    name = forms.CharField(max_length=100, required=False)

    def clean(self):
        if not (self.cleaned_data.get("loan_account_no") or self.cleaned_data.get("group_loan_account_no")):
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please provide personal/group loan account number")
            raise forms.ValidationError(errors)
        elif (self.cleaned_data.get("loan_account_no") and self.cleaned_data.get("group_loan_account_no")):
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please choose only one a/c (personal/group)")
            raise forms.ValidationError(errors)
        if self.cleaned_data.get("loan_account_no"):
            self.loan_account = LoanAccount.objects.filter(account_no=self.cleaned_data.get("loan_account_no")).last()
        elif self.cleaned_data.get("group_loan_account_no"):
            self.group_loan_account = LoanAccount.objects.filter(account_no=self.cleaned_data.get("group_loan_account_no")).last()
            self.loan_account = GroupMemberLoanAccount.objects.get(client__first_name=self.cleaned_data.get("name"), group_loan_account=self.group_loan_account)
        if not self.loan_account:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Account not found with given a/c number")
            raise forms.ValidationError(errors)
        if self.loan_account.status == "Approved":
            if not (
                self.loan_account.total_loan_balance or
                self.loan_account.interest_charged or
                self.loan_account.loan_repayment_amount or
                self.loan_account.principle_repayment
            ):
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("Loan has been cleared sucessfully.")
                raise forms.ValidationError(errors)
        else:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Member Loan is under pending for approval.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class GetFixedDepositsForm(forms.Form):

    fixed_deposit_account_no = forms.CharField(max_length=100, required=False)

    def clean(self):
        if self.cleaned_data.get("fixed_deposit_account_no"):
            self.fixed_deposit_account = FixedDeposits.objects.filter(
                fixed_deposit_number=self.cleaned_data.get("fixed_deposit_account_no")).last()
        if not self.fixed_deposit_account:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("No Fixed Deposit Accounts found with given a/c number")
            raise forms.ValidationError(errors)
        if self.fixed_deposit_account.status == "Paid":
            errors = self.errors.setdefault('message1', ErrorList())
            errors.append('Member Fixed Deposit already paid')
            raise forms.ValidationError(errors)
        elif self.fixed_deposit_account.status == 'Closed':
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Member Fixed Deposit is Closed.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class GetRecurringDepositsForm(forms.Form):

    recurring_deposit_account_no = forms.CharField(max_length=100, required=False)

    def clean(self):

        if self.cleaned_data.get("recurring_deposit_account_no"):
            self.recurring_deposit_account = RecurringDeposits.objects.filter(
                reccuring_deposit_number=self.cleaned_data.get("recurring_deposit_account_no")).last()
        if not self.recurring_deposit_account:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("No Recurring Deposit Accounts found with given a/c number")
            raise forms.ValidationError(errors)
        if self.recurring_deposit_account.status == "Paid":
            errors = self.errors.setdefault('message1', ErrorList())
            errors.append('Member Recurring Deposit already paid')
            raise forms.ValidationError(errors)
        elif self.recurring_deposit_account.status == 'Closed':
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Member Recurring Deposit is Closed.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class ReceiptForm(forms.ModelForm):

    date = forms.DateField(input_formats=["%Y-%m-%d"], required=True)
    name = forms.CharField(max_length=100, required=True)
    account_number = forms.CharField(max_length=100, required=True)
    savingsdeposit_thrift_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    fixeddeposit_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    recurringdeposit_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    insurance_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    # group
    group_name = forms.CharField(max_length=100, required=False)
    group_account_number = forms.CharField(max_length=100, required=False)
    # loan
    loan_account_no = forms.CharField(max_length=100, required=False)
    group_loan_account_no = forms.CharField(max_length=100, required=False)
    loanprocessingfee_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    demand_loanprinciple = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    demand_loaninterest = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    loanprinciple_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    loaninterest_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    # fees
    sharecapital_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    bookfee_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    entrancefee_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    membershipfee_amount = forms.DecimalField(required=False, validators=[MinValueValidator(0)])
    fixed_deposit_account_no = forms.CharField(max_length=100, required=False)
    recurring_deposit_account_no = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Receipts
        fields = ("date", "branch", "receipt_number")

    def clean_receipt_number(self):
        receipt_number = self.cleaned_data.get("receipt_number")
        is_receipt_number_exist = Receipts.objects.filter(receipt_number=receipt_number)
        if is_receipt_number_exist:
            raise forms.ValidationError("Receipts with this Receipt number already exists.")
        return receipt_number

    def verify_loan(self, loan_account):
        if loan_account.status == "Applied":
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Loan is under pending for approval.")
            raise forms.ValidationError(errors)
        elif loan_account.status == "Approved":
            if not loan_account.loan_issued_date:
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("Loan Payment has not yet done.")
                raise forms.ValidationError(errors)
            else:
                if not ((loan_account.total_loan_balance) or
                        (loan_account.interest_charged) or
                        (loan_account.loan_repayment_amount) or
                        (loan_account.principle_repayment)):
                    errors = self._errors.setdefault("message1", ErrorList())
                    errors.append("Loan has been cleared sucessfully.")
                    raise forms.ValidationError(errors)
                else:
                    if not ((self.cleaned_data.get("loanprinciple_amount", 0) or d('0.00')) <= (loan_account.total_loan_balance)):
                        errors = self._errors.setdefault("message1", ErrorList())
                        errors.append("Amount is greater than loan balance.")
                        raise forms.ValidationError(errors)
                    else:
                        if (self.cleaned_data.get("loaninterest_amount", 0) or d('0.00')) > (loan_account.interest_charged):
                            errors = self._errors.setdefault("message1", ErrorList())
                            errors.append("Entered interest amount is greater than interest charged.")
                            raise forms.ValidationError(errors)
                        elif (self.cleaned_data.get("loanprinciple_amount", 0) or d('0.00')) > (loan_account.principle_repayment):
                            errors = self._errors.setdefault("message1", ErrorList())
                            errors.append("Entered principle amount is greater than demand amount.")
                            raise forms.ValidationError(errors)
                        elif((self.cleaned_data.get("loaninterest_amount", 0) or d('0.00')) >
                                (loan_account.loan_amount) or
                                (self.cleaned_data.get("loanprinciple_amount", 0) or d('0.00')) >
                                (loan_account.loan_amount)):
                            errors = self._errors.setdefault("message1", ErrorList())
                            errors.append("Amount is greater than issued loan amount. Transaction can't be done.")
                            raise forms.ValidationError(errors)
                        else:
                            if self.cleaned_data.get("loanprinciple_amount", 0):
                                loan_account.total_loan_amount_repaid += (self.cleaned_data.get("loanprinciple_amount", 0))
                            if self.cleaned_data.get("loaninterest_amount", 0):
                                loan_account.total_interest_repaid += (self.cleaned_data.get("loaninterest_amount", 0))
                            loan_account.total_loan_paid = (loan_account.total_loan_amount_repaid + loan_account.total_interest_repaid)
                            if self.cleaned_data.get("loanprinciple_amount", 0):
                                loan_account.total_loan_balance -= (self.cleaned_data.get("loanprinciple_amount", 0))
                            try:
                                if not loan_account.group:
                                    loan_account.no_of_repayments_completed += loan_account.loan_repayment_every
                            except:
                                loan_account.no_of_repayments_completed += loan_account.loan_repayment_every
                            if ((loan_account.total_loan_amount_repaid == loan_account.loan_amount) and
                                    loan_account.total_loan_balance == 0):
                                if (self.cleaned_data.get("loanprinciple_amount", 0)) > (loan_account.principle_repayment):
                                    errors = self._errors.setdefault("message1", ErrorList())
                                    errors.append("Amount is greater than issued loan amount. Transaction can't be done.")
                                    raise forms.ValidationError(errors)

        elif loan_account.status == "Rejected":
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Loan has been Rejected.")
            raise forms.ValidationError(errors)
        elif loan_account.status == "Closed":
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Loan has been Closed.")
            raise forms.ValidationError(errors)

    def clean(self):
        self.savings_account = None
        self.loan_account = None
        self.group_savings_account = None
        self.group_loan_account = None
        self.group = None
        self.group_member_loan_account = None
        name = self.cleaned_data.get("name")
        account_number = self.cleaned_data.get("account_number")
        if name and account_number:
            self.client = Client.objects.filter(first_name__iexact=name, account_number=account_number).last()
            if not self.client:
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("No Client exists with this First Name and Account number.")
                raise forms.ValidationError(errors)
        else:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please provide both First Name and Account number.")
            raise forms.ValidationError(errors)
        if not(self.cleaned_data.get("sharecapital_amount") or
           self.cleaned_data.get("entrancefee_amount") or
           self.cleaned_data.get("membershipfee_amount") or
           self.cleaned_data.get("bookfee_amount") or
           self.cleaned_data.get("loanprocessingfee_amount") or
           self.cleaned_data.get("savingsdeposit_thrift_amount") or
           self.cleaned_data.get("fixeddeposit_amount") or
           self.cleaned_data.get("recurringdeposit_amount") or
           self.cleaned_data.get("loanprinciple_amount") or
           self.cleaned_data.get("insurance_amount") or
           (self.cleaned_data.get("loaninterest_amount") or 0 > 0)):
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Empty Receipt can't be generated.")
            raise forms.ValidationError(errors)
        # client loan a/c
        loan_account_no = self.cleaned_data.get("loan_account_no")
        group_loan_account_no = self.cleaned_data.get("group_loan_account_no")
        if loan_account_no:
            self.loan_account = LoanAccount.objects.filter(client=self.client, account_no=loan_account_no).last()
            if not self.loan_account:
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("Loan does not exists with this Loan Account Number for this Member.")
                raise forms.ValidationError(errors)
        elif (
            (
                self.cleaned_data.get("loanprinciple_amount") or
                self.cleaned_data.get("loanprocessingfee_amount") or
                self.cleaned_data.get("loaninterest_amount")
            ) and not (loan_account_no or group_loan_account_no)
        ):
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please select personal/group loan account number")
            raise forms.ValidationError(errors)
        # client group
        self.client_group = self.client.group_set.first()
        group_name = self.cleaned_data.get("group_name")
        group_account_number = self.cleaned_data.get("group_account_number")
        if group_name and group_account_number:
            self.group = Group.objects.filter(name__iexact=group_name, clients=self.client, account_number=group_account_number).last()
            if not self.group:
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("No Group exists with given client, name and account number.")
                raise forms.ValidationError(errors)
        elif group_name or group_account_number:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please enter both Group Name and Account Number.")
            raise forms.ValidationError(errors)
        # client group a/c
        if group_loan_account_no and self.group:
            self.group_loan_account = LoanAccount.objects.filter(group=self.group,
                                                                 account_no=group_loan_account_no).last()
            if not self.group_loan_account:
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("Loan does not exists with this Loan Account Number for this Group.")
                raise forms.ValidationError(errors)
        # cannot pay both loans at once
        if self.group_loan_account and self.loan_account:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Unable pay personal loan and group loan at once.")
            raise forms.ValidationError(errors)
        # check personal savings a/c
        if (self.cleaned_data.get("savingsdeposit_thrift_amount")):
            self.savings_account = SavingsAccount.objects.filter(client=self.client).last()
            if not self.savings_account:
                errors = self._errors.setdefault("message1", ErrorList())
                errors.append("Member does not have savings account")
                raise forms.ValidationError(errors)
        # check group savings a/c
        if self.cleaned_data.get("savingsdeposit_thrift_amount") and self.client_group:
            self.group_savings_account = SavingsAccount.objects.filter(group=self.client_group).last()
        # verify loan
        if self.cleaned_data.get("loanprinciple_amount") or self.cleaned_data.get("loaninterest_amount") != 0:
            if self.loan_account:
                self.verify_loan(self.loan_account)
            elif self.group_loan_account:
                self.group_member_loan_account = GroupMemberLoanAccount.objects.filter(group_loan_account=self.group_loan_account, client=self.client).first()
                if self.group_member_loan_account:
                    if self.group_member_loan_account.status == "Approved":
                        self.verify_loan(self.group_member_loan_account)
                        self.group_loan_account.no_of_repayments_completed = 0
                        self.group_loan_account.total_loan_balance -= self.cleaned_data.get("loanprinciple_amount", 0)
                        self.group_loan_account.save()
                    else:
                        errors = self._errors.setdefault("message1", ErrorList())
                        errors.append("Group Loan is not yet Approved.")
                        raise forms.ValidationError(errors)
                else:
                    errors = self._errors.setdefault("message1", ErrorList())
                    errors.append("Member in this group does not exists.")
                    raise forms.ValidationError(errors)
        if self.cleaned_data.get('fixed_deposit_account_no'):
            fixed_deposit_account = FixedDeposits.objects.filter(
                fixed_deposit_number=self.cleaned_data.get('fixed_deposit_account_no')
            ).first()
            if fixed_deposit_account:
                savings_account = SavingsAccount.objects.filter(client=fixed_deposit_account.client)
                if savings_account:
                    self.savings_account = savings_account.last()
                    if fixed_deposit_account.status == 'Opened':
                        if not Receipts.objects.filter(fixed_deposit_account=fixed_deposit_account).exists():
                            if self.cleaned_data.get('fixeddeposit_amount') >= 0:
                                if d(fixed_deposit_account.fixed_deposit_amount) != d(self.cleaned_data.get('fixeddeposit_amount')):
                                    errors = self._errors.setdefault('message1', ErrorList())
                                    errors.append('Entered fixed amount is not equal to the actual amount.')
                                    raise forms.ValidationError(errors)
                            else:
                                errors = self._errors.setdefault('fixeddeposit_amount', ErrorList())
                                errors.append('Please enter the Fixed amount for the Fixed Deposit A/C.')
                                raise forms.ValidationError(errors)
                        else:
                            errors = self._errors.setdefault('fixeddeposit_amount', ErrorList())
                            errors.append('This Amount is already deposited.')
                            raise forms.ValidationError(errors)
                    else:
                        errors = self._errors.setdefault('fixeddeposit_amount', ErrorList())
                        errors.append('This Amount is already deposited.')
                        raise forms.ValidationError(errors)
                else:
                    errors = self._errors.setdefault('fixed_deposit_account_no', ErrorList())
                    errors.append('Please Create a Savings A/C first to store the Fixed amount for the Fixed Deposit A/C.')
                    raise forms.ValidationError(errors)
        elif not self.cleaned_data.get('fixed_deposit_account_no'):
            if self.cleaned_data.get("fixeddeposit_amount"):
                errors = self._errors.setdefault('fixeddeposit_amount', ErrorList())
                errors.append('Please, select the fixed deposit before you enter the amount or clear the amount.')
                raise forms.ValidationError(errors)

        if self.cleaned_data.get('recurring_deposit_account_no'):
            recurring_deposit_account = RecurringDeposits.objects.filter(
                reccuring_deposit_number=self.cleaned_data.get('recurring_deposit_account_no')
            ).first()
            if recurring_deposit_account:
                savings_account = SavingsAccount.objects.filter(client=recurring_deposit_account.client)
                if savings_account:
                    self.savings_account = savings_account.last()
                    if recurring_deposit_account.status == 'Opened':
                        if self.cleaned_data.get('recurringdeposit_amount') >= 0:
                            if (
                                int(recurring_deposit_account.number_of_payments) <= int(
                                    recurring_deposit_account.recurring_deposit_period)
                            ):
                                if (
                                    d(recurring_deposit_account.recurring_deposit_amount) != d(
                                        self.cleaned_data.get('recurringdeposit_amount'))
                                ):
                                    errors = self._errors.setdefault('message1', ErrorList())
                                    errors.append('Entered recurring amount is not equal to the actual amount.')
                                    raise forms.ValidationError(errors)
                            else:
                                raise forms.ValidationError('You have exceeded the recurring deposit reciepts adding to this A/C.')
                        else:
                            errors = self._errors.setdefault('recurringdeposit_amount', ErrorList())
                            errors.append('Please enter the Recurring amount for the Recurring Deposit A/C.')
                            raise forms.ValidationError(errors)
                else:
                    errors = self._errors.setdefault('recurring_deposit_account_no', ErrorList())
                    errors.append('Please Create a Savings A/C first to store the Recurring amount for the Recurring Deposit A/C.')
                    raise forms.ValidationError(errors)
        elif not self.cleaned_data.get('recurring_deposit_account_no'):
            if self.cleaned_data.get("recurringdeposit_amount"):
                errors = self._errors.setdefault('recurringdeposit_amount', ErrorList())
                errors.append('Please, select the recurring deposit before you enter the amount or clear the amount.')
                raise forms.ValidationError(errors)

        return self.cleaned_data


class ClientDepositsAccountsForm(forms.Form):
    payment_type = forms.CharField(max_length=100, required=False)
    client_name = forms.CharField(max_length=100, required=False)
    client_account_number = forms.CharField(max_length=100, required=False)

    def clean(self):
        self.client = None
        self.pay_type = self.cleaned_data.get('payment_type')
        if not(self.cleaned_data.get("client_name") and self.cleaned_data.get("client_account_number")):
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Please provide both  member first name, account number")
            raise forms.ValidationError(errors)
        self.client = Client.objects.filter(
            first_name__iexact=self.cleaned_data.get("client_name"),
            account_number=self.cleaned_data.get("client_account_number")
        ).last()
        if not self.client:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("No Client exists with this First Name and Account number.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class GetFixedDepositsPaidForm(forms.Form):
    fixed_deposit_account_no = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        self.client = kwargs['initial'].pop('client', None)
        super(GetFixedDepositsPaidForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get("fixed_deposit_account_no"):
            self.fixed_deposit_account = FixedDeposits.objects.filter(
                client=self.client,
                fixed_deposit_number=self.cleaned_data.get("fixed_deposit_account_no")).last()
        if not self.fixed_deposit_account:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("No Fixed Deposit Accounts found with given a/c number")
            raise forms.ValidationError(errors)
        if self.fixed_deposit_account.status == "Opened":
            errors = self.errors.setdefault('message1', ErrorList())
            errors.append('Member Fixed Deposit is Opened')
            raise forms.ValidationError(errors)
        elif self.fixed_deposit_account.status == 'Closed':
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Member Fixed Deposit is Closed.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class GetRecurringDepositsPaidForm(forms.Form):

    recurring_deposit_account_no = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        self.client = kwargs['initial'].pop('client', None)
        super(GetRecurringDepositsPaidForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get("recurring_deposit_account_no"):
            self.recurring_deposit_account = RecurringDeposits.objects.filter(
                client=self.client,
                reccuring_deposit_number=self.cleaned_data.get("recurring_deposit_account_no")
            ).last()
        if not self.recurring_deposit_account:
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append(
                "No Recurring Deposit Accounts found with given a/c number")
            raise forms.ValidationError(errors)
        elif self.recurring_deposit_account.status == 'Closed':
            errors = self._errors.setdefault("message1", ErrorList())
            errors.append("Member Recurring Deposit is Closed.")
            raise forms.ValidationError(errors)
        return self.cleaned_data


class PaymentForm(forms.ModelForm):
    date = forms.DateField(input_formats=["%m/%d/%Y"], required=True)
    # group
    group_name = forms.CharField(max_length=100, required=False)
    group_account_number = forms.CharField(max_length=100, required=False)
    # member
    client_name = forms.CharField(max_length=100, required=False)
    client_account_number = forms.CharField(max_length=100, required=False)
    staff_username = forms.CharField(max_length=100, required=False)
    group_loan_account_no = forms.CharField(max_length=100, required=False)
    member_loan_account_no = forms.CharField(max_length=100, required=False)
    interest = forms.DecimalField(required=False)
    fixed_deposit_account_no = forms.CharField(max_length=100, required=False)
    recurring_deposit_account_no = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Payments
        fields = ["date", "branch", "voucher_number", "payment_type", "amount", "interest", "total_amount", "totalamount_in_words"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PaymentForm, self).__init__(*args, **kwargs)

    def clean_date(self):
        datestring_format = datetime.datetime.strptime(self.data.get("date"), "%m/%d/%Y").strftime("%Y-%m-%d")
        if self.data.get("payment_type") == "Loans":
            loan = None
            if self.data.get("member_loan_account_no"):
                loan = LoanAccount.objects.filter(id=self.data.get("member_loan_account_no")).first()
            elif self.data.get("group_loan_account_no"):
                loan = LoanAccount.objects.filter(id=self.data.get("group_loan_account_no")).first()
            if loan:
                if str(datestring_format) < str(loan.opening_date):
                    raise forms.ValidationError("Payment date should be greater than Loan Application date")
        return self.cleaned_data.get("date")

    def clean_voucher_number(self):
        voucher_number = self.cleaned_data.get("voucher_number")
        is_voucher_number_exist = Payments.objects.filter(voucher_number=voucher_number)
        if is_voucher_number_exist:
            raise forms.ValidationError("Payslip with this Voucher number already exists.")
        return voucher_number

    def clean(self):
        if not (self.cleaned_data.get("amount") != 0 and self.cleaned_data.get("total_amount") != 0):
            raise forms.ValidationError("Voucher can't be generated with amount/total amount zero")

        if not (self.cleaned_data.get("amount") and self.cleaned_data.get("total_amount")):
            return

        if self.cleaned_data.get("payment_type") == "TravellingAllowance" or self.cleaned_data.get("payment_type") == "Paymentofsalary":
            if not self.cleaned_data.get("staff_username"):
                raise forms.ValidationError("Please enter Employee Username")
            else:
                self.staff = User.objects.filter(username__iexact=self.cleaned_data.get("staff_username")).first()
                if not self.staff:
                    raise forms.ValidationError("Entered Employee Username is incorrect")
                if self.cleaned_data.get("interest"):
                    raise forms.ValidationError("Interest must be empty for TA and Payment of salary Voucher.")
        elif self.cleaned_data.get("payment_type") == "PrintingCharges" or \
                self.cleaned_data.get("payment_type") == "StationaryCharges" or \
                self.cleaned_data.get("payment_type") == "OtherCharges":
            if self.cleaned_data.get("interest"):
                raise forms.ValidationError("Interest must be empty for Charges Voucher.")
            else:
                if not (self.cleaned_data.get("total_amount") == self.cleaned_data.get("amount")):
                    raise forms.ValidationError("Entered total amount is not equal to amount.")
        elif self.cleaned_data.get("payment_type") == "SavingsWithdrawal":
            total_amount = d(self.cleaned_data.get("amount"))
            if self.cleaned_data.get("interest"):
                total_amount += d(self.cleaned_data.get("interest"))
                if d(self.cleaned_data.get("total_amount")) != \
                        d(d(self.cleaned_data.get("amount")) + d(self.cleaned_data.get("interest"))):
                    raise forms.ValidationError("Entered total amount is incorrect.")
            else:
                if d(self.cleaned_data.get("total_amount")) != d(self.cleaned_data.get("amount")):
                    raise forms.ValidationError("Entered total amount is not equal to amount.")

            if not (self.cleaned_data.get("client_name") or self.cleaned_data.get('group_name')):
                raise forms.ValidationError("Please enter the Member First Name or Group Name")
            elif self.cleaned_data.get("client_name"):
                if not self.cleaned_data.get("client_account_number"):
                    raise forms.ValidationError("Please enter the Member Account number")
                if self.cleaned_data.get("client_name") and self.cleaned_data.get('client_account_number'):
                    client_filter = Client.objects.filter(
                        first_name__iexact=self.cleaned_data.get("client_name"),
                        account_number=self.cleaned_data.get("client_account_number"))
                    if client_filter:
                        client = client_filter.first()
                        savings_account = SavingsAccount.objects.filter(client=client)
                        if savings_account:
                            savings_account = savings_account.first()
                            if self.cleaned_data.get("amount"):
                                if d(savings_account.savings_balance) >= total_amount:
                                    client_group = client.group_set.first()
                                    if client_group:
                                        group_savings_account = SavingsAccount.objects.filter(group=client_group)
                                        if group_savings_account:
                                            group_savings_account = group_savings_account.first()
                                            if d(group_savings_account.savings_balance) >= total_amount:
                                                if self.cleaned_data.get("group_name"):
                                                    if self.cleaned_data.get("group_name").lower() == client_group.name.lower():
                                                        if self.cleaned_data.get("group_account_number"):
                                                            if not self.cleaned_data.get("group_account_number") == \
                                                                    client_group.account_number:
                                                                raise forms.ValidationError("Entered Group A/C Number is incorrect.")
                                                        else:
                                                            raise forms.ValidationError("Please enter the Group A/C Number.")
                                                    else:
                                                        raise forms.ValidationError("Member does not belong to the entered Group Name.")
                                            elif d(group_savings_account.savings_balance) < total_amount:
                                                raise forms.ValidationError("Group Savings A/C does not have sufficient balance.")
                                        else:
                                            raise forms.ValidationError(
                                                "The Group which the Member belongs to does not have Savings Account.")
                                    else:
                                        if self.cleaned_data.get("group_name") or self.cleaned_data.get("group_account_number"):
                                            raise forms.ValidationError(
                                                "Member does not assigned to any Group. Please clear Group details")
                                elif d(savings_account.savings_balance) < total_amount:
                                    raise forms.ValidationError("Member Savings Account does not have sufficient balance.")
                        else:
                            raise forms.ValidationError("Member does not have Savings Account to withdraw amount.")
                    else:
                        raise forms.ValidationError(
                            "Member does not exists with this First Name and A/C Number. Please enter correct details.")
            elif self.cleaned_data.get("group_name") and not self.cleaned_data.get('client_name'):
                if self.cleaned_data.get("group_account_number"):
                    group_filter = Group.objects.filter(
                        name__iexact=self.cleaned_data.get("group_name"),
                        account_number=self.cleaned_data.get("group_account_number"))
                    if group_filter:
                        group = group_filter.first()
                        group_savings_account_filter = SavingsAccount.objects.filter(group=group)
                        if group_savings_account_filter:
                            group_savings_account = group_savings_account_filter.first()
                            if d(group_savings_account.savings_balance) >= total_amount:
                                client_group = group.clients.all()
                                savings_accounts_filter = SavingsAccount.objects.filter(client__in=[client for client in client_group])
                                if savings_accounts_filter:
                                    deduct_amount = total_amount / d(len(savings_accounts_filter))
                                    if savings_accounts_filter:
                                        for savings_account in savings_accounts_filter:
                                            if (savings_account.savings_balance) <= d(deduct_amount):
                                                raise forms.ValidationError(
                                                    'The deduction amount higher than the group member savings account.')
                            else:
                                raise forms.ValidationError('Entered amount is higher than the savings amount.')
                        else:
                            raise forms.ValidationError('Savings A/C not existed with the entered group.')
                    else:
                        raise forms.ValidationError("Group with given details doesn't exist.")
                else:
                    raise forms.ValidationError("Please provide the group A/C number to proceed with Group Savings Withdrawal.")
        elif self.cleaned_data.get('payment_type') == 'FixedWithdrawal':
            if not self.cleaned_data.get('client_name'):
                raise forms.ValidationError('Please enter the Member First Name')
            if (
                self.cleaned_data.get('group_name') or self.cleaned_data.get('group_name') and
                self.cleaned_data.get('group_account_number')
            ):
                raise forms.ValidationError("Don't include group details while processing FixedWithdrawal")
            elif self.cleaned_data.get('client_name'):
                if not self.cleaned_data.get("client_account_number"):
                    raise forms.ValidationError("Please enter the Member Account number")
                if self.cleaned_data.get("client_name") and self.cleaned_data.get('client_account_number'):
                    client_filter = Client.objects.filter(
                        first_name__iexact=self.cleaned_data.get("client_name"),
                        account_number=self.cleaned_data.get("client_account_number"))
                    if client_filter:
                        self.client = client_filter.first()
                        if self.cleaned_data.get("fixed_deposit_account_no"):
                            self.fixed_deposit_account_filter = FixedDeposits.objects.filter(
                                client=self.client,
                                fixed_deposit_number=self.cleaned_data.get("fixed_deposit_account_no")
                            ).exclude(status="Closed")
                            if self.fixed_deposit_account_filter:
                                self.fixed_deposit_account = self.fixed_deposit_account_filter.first()
                                if self.fixed_deposit_account:
                                    fixed_deposit = self.fixed_deposit_account
                                    fixed_deposit_amount = fixed_deposit.fixed_deposit_amount
                                    # interest_charged = (fixed_deposit.fixed_deposit_amount * (
                                    #     fixed_deposit.fixed_deposit_interest_rate / 12)) / 100
                                    # fixed_deposit_interest_charged = interest_charged * d(
                                    #     fixed_deposit.fixed_deposit_period)
                                    # total_amount = \
                                    #     fixed_deposit.fixed_deposit_amount + fixed_deposit_interest_charged
                                    current_date = datetime.datetime.now().date()
                                    year_days = 366 if calendar.isleap(current_date.year) else 365
                                    interest_charged = (fixed_deposit.fixed_deposit_amount * fixed_deposit.fixed_deposit_interest_rate) / (d(year_days) * 100)
                                    days_to_calculate = (current_date - fixed_deposit.deposited_date).days
                                    calculated_interest_money_till_date = interest_charged * days_to_calculate
                                    fixed_deposit_interest_charged = calculated_interest_money_till_date
                                    total_amount = fixed_deposit.fixed_deposit_amount + calculated_interest_money_till_date
                                    if self.cleaned_data.get("amount"):
                                        if d(fixed_deposit_amount) > d(self.cleaned_data.get("amount")):
                                            raise forms.ValidationError("Entered amount is less than the Member Fixed Deposit amount.")
                                        elif d(fixed_deposit_amount) < d(self.cleaned_data.get("amount")):
                                            raise forms.ValidationError("Entered amount is greater than the Member Fixed Deposit amount.")
                                        elif d(fixed_deposit_amount) != d(self.cleaned_data.get("amount")):
                                            raise forms.ValidationError("Entered amount is not equals to the Member Fixed Deposit amount.")
                                    if self.cleaned_data.get("interest"):
                                        if round(d(fixed_deposit_interest_charged), 6) > round(d(self.cleaned_data.get("interest")), 6):
                                            raise forms.ValidationError(
                                                "Entered interest amount is less than the Member Fixed Deposit interest amount.")
                                        elif round(d(fixed_deposit_interest_charged), 6) < round(d(self.cleaned_data.get("interest")), 6):
                                            raise forms.ValidationError(
                                                "Entered interest amount is greater than the Member Fixed Deposit interest amount.")
                                        elif round(d(fixed_deposit_interest_charged), 6) != round(d(self.cleaned_data.get("interest")), 6):
                                            raise forms.ValidationError(
                                                "Entered interest amount is not equals to the Member Fixed Deposit interest amount.")
                                    else:
                                        raise forms.ValidationError("Interest Amount field is required for Fixed Deposit Wirthdrawl.")
                                    if self.cleaned_data.get('total_amount'):
                                        if round(d(total_amount), 6) > round(d(self.cleaned_data.get("total_amount")), 6):
                                            raise forms.ValidationError(
                                                "Entered total amount is less than the Member Fixed Deposit total amount.")
                                        elif round(d(total_amount), 6) < round(d(self.cleaned_data.get("total_amount")), 6):
                                            raise forms.ValidationError(
                                                "Entered total amount is greater than the Member Fixed Deposit total amount.")
                                        elif round(d(total_amount), 6) != round(d(self.cleaned_data.get("total_amount")), 6):
                                            raise forms.ValidationError(
                                                "Entered total amount is not equals to the Member Fixed Deposit total amount.")
                            else:
                                errors = self._errors.setdefault("message1", ErrorList())
                                errors.append("No Fixed Deposit Accounts found with given a/c number")
                                raise forms.ValidationError(errors)
                        else:
                            raise forms.ValidationError("Member does not have Fixed Deposit Account to withdraw amount.")
                    else:
                        raise forms.ValidationError(
                            "Member does not exists with this First Name and A/C Number. Please enter correct details.")
        elif self.cleaned_data.get('payment_type') == 'RecurringWithdrawal':
            if not self.cleaned_data.get('client_name'):
                raise forms.ValidationError('Please enter the Member First Name')
            if (
                self.cleaned_data.get('group_name') or self.cleaned_data.get('group_name') and
                self.cleaned_data.get('group_account_number')
            ):
                raise forms.ValidationError("Don't include group details while processing RecurringWithdrawal")
            elif self.cleaned_data.get('client_name'):
                if not self.cleaned_data.get("client_account_number"):
                    raise forms.ValidationError("Please enter the Member Account number")
                if self.cleaned_data.get("client_name") and self.cleaned_data.get('client_account_number'):
                    client_filter = Client.objects.filter(
                        first_name__iexact=self.cleaned_data.get("client_name"),
                        account_number=self.cleaned_data.get("client_account_number"))
                    if client_filter:
                        self.client = client_filter.first()
                        if self.cleaned_data.get("recurring_deposit_account_no"):
                            self.recurring_deposit_account_filter = RecurringDeposits.objects.filter(
                                client=self.client,
                                reccuring_deposit_number=self.cleaned_data.get("recurring_deposit_account_no")
                            ).exclude(status="Closed", number_of_payments=0)
                            if self.recurring_deposit_account_filter:
                                self.recurring_deposit_account = self.recurring_deposit_account_filter.first()
                                if self.recurring_deposit_account:
                                    recurring_deposit = self.recurring_deposit_account
                                    recurring_deposit_amount = d(recurring_deposit.recurring_deposit_amount) * recurring_deposit.number_of_payments
                                    # interest_charged = (recurring_deposit_amount * (
                                    #     recurring_deposit.recurring_deposit_interest_rate / 12)) / 100
                                    # recurring_deposit_interest_charged = interest_charged * d(
                                    #     recurring_deposit.recurring_deposit_period)
                                    # total_amount = \
                                    #     recurring_deposit_amount + recurring_deposit_interest_charged
                                    current_date = datetime.datetime.now().date()
                                    year_days = 366 if calendar.isleap(current_date.year) else 365
                                    interest_charged = (recurring_deposit_amount * recurring_deposit.recurring_deposit_interest_rate) / (d(year_days) * 100)
                                    days_to_calculate = (current_date - recurring_deposit.deposited_date).days
                                    recurring_deposit_interest_charged = interest_charged * days_to_calculate
                                    total_amount = recurring_deposit_amount + recurring_deposit_interest_charged
                                    if self.cleaned_data.get("amount"):
                                        if d(recurring_deposit_amount) > d(self.cleaned_data.get("amount")):
                                            raise forms.ValidationError(
                                                "Entered amount is less than the Member Recurring Deposit amount.")
                                        elif d(recurring_deposit_amount) < d(self.cleaned_data.get("amount")):
                                            raise forms.ValidationError(
                                                "Entered amount is greater than the Member Recurring Deposit amount.")
                                        elif d(recurring_deposit_amount) != d(self.cleaned_data.get("amount")):
                                            raise forms.ValidationError(
                                                "Entered amount is not equals to the Member Recurring Deposit amount.")
                                    if self.cleaned_data.get("interest"):
                                        if round(d(recurring_deposit_interest_charged), 6) < \
                                                round(d(self.cleaned_data.get("interest")), 6):
                                            raise forms.ValidationError(
                                                "Entered interest amount is greater than the Member Recurring Deposit interest amount.")
                                        elif round(d(recurring_deposit_interest_charged), 6) > \
                                                round(d(self.cleaned_data.get("interest")), 6):
                                            raise forms.ValidationError(
                                                "Entered interest amount is less than the Member Recurring Deposit interest amount.")
                                        elif round(d(recurring_deposit_interest_charged), 6) != \
                                                round(d(self.cleaned_data.get("interest")), 6):
                                            raise forms.ValidationError(
                                                "Entered interest amount is not equals to the Member Recurring Deposit interest amount.")
                                    else:
                                        raise forms.ValidationError(
                                            "This Interest Amount field is required for Recurring Deposit Wirthdrawl.")
                                    if self.cleaned_data.get('total_amount'):
                                        if round(d(total_amount), 6) < round(d(self.cleaned_data.get("total_amount")), 6):
                                            raise forms.ValidationError(
                                                "Entered total amount is greater than the Member Recurring Deposit total amount.")
                                        elif round(d(total_amount), 6) > round(d(self.cleaned_data.get("total_amount")), 6):
                                            raise forms.ValidationError(
                                                "Entered total amount is less than the Member Recurring Deposit total amount.")
                                        elif round(d(total_amount), 6) != round(d(self.cleaned_data.get("total_amount")), 6):
                                            raise forms.ValidationError(
                                                "Entered total amount is not equals to the Member Recurring Deposit total amount.")

                            else:
                                errors = self._errors.setdefault("message1", ErrorList())
                                errors.append("No Recurring Deposit Accounts found with given a/c number")
                                raise forms.ValidationError(errors)
                        else:
                            raise forms.ValidationError("Member does not have Recurring Deposits Account to withdraw amount.")
                    else:
                        raise forms.ValidationError(
                            "Member does not exists with this First Name and A/C Number. Please enter correct details.")
        elif self.cleaned_data.get("payment_type") == "Loans":
            if self.cleaned_data.get("interest"):
                raise forms.ValidationError("Interest amount must be empty while issuing Loans.")

            if not (self.cleaned_data.get("group_name") or self.cleaned_data.get("client_name")):
                raise forms.ValidationError("Please enter Group Name or Client Name.")
            elif self.cleaned_data.get("group_name"):

                if (
                    self.cleaned_data.get('client_name') or self.cleaned_data.get('client_account_number') or
                    (self.cleaned_data.get('client_name') and self.cleaned_data.get('client_account_number'))
                ):
                    raise forms.ValidationError("Please Choose either Group or Client but not both. "
                                                "Please clear the Client details to proceed with Group and vice versa.")

                if not self.cleaned_data.get("group_account_number"):
                    raise forms.ValidationError("Please enter Group Account Number.")

                elif self.cleaned_data.get("group_account_number"):
                    group_filter = Group.objects.filter(
                        name__iexact=self.cleaned_data.get("group_name"),
                        account_number=self.cleaned_data.get("group_account_number"))
                    if group_filter:
                        group = group_filter.first()
                        if not self.cleaned_data.get("group_loan_account_no"):
                            raise forms.ValidationError("Please enter the Group Loan Account Number.")
                        else:
                            loan_account_filter = LoanAccount.objects.filter(id=self.cleaned_data.get("group_loan_account_no"))
                            if loan_account_filter:
                                loan_account = loan_account_filter.first()
                                if not Payments.objects.filter(loan_account=loan_account, group=group):
                                    if loan_account.status == "Approved":
                                        if (self.cleaned_data.get("total_amount") and self.cleaned_data.get("amount")):
                                            if d(self.cleaned_data.get("total_amount")) == d(self.cleaned_data.get("amount")):
                                                if d(loan_account.loan_amount) == d(self.cleaned_data.get("total_amount")):
                                                    clients_list = group.clients.all()
                                                    if clients_list:
                                                        if len(clients_list) == 0:
                                                            raise forms.ValidationError("Group does not contain members inorder to issue Loan.")
                                                    else:
                                                        raise forms.ValidationError("Group does not contain members inorder to issue Loan.")
                                                else:
                                                    raise forms.ValidationError("Amount is not equal to the applied loan amount.")
                                            else:
                                                raise forms.ValidationError("Entered total amount is not equal to amount.")
                                    else:
                                        raise forms.ValidationError("Group Loan Account is not yet Approved.")
                                else:
                                    raise forms.ValidationError("Group Loan Account is already Issued.")
                            else:
                                raise forms.ValidationError("Group does not have any Loan with this Loan A/C Number.")
                    else:
                        raise forms.ValidationError("Group does not exists with this Name and A/C Number. Please enter correct details.")
            elif self.cleaned_data.get("client_name"):
                if (
                    self.cleaned_data.get('group_name') or self.cleaned_data.get('group_account_number') or
                    (self.cleaned_data.get('group_name') and self.cleaned_data.get('group_account_number'))
                ):
                    raise forms.ValidationError(
                        "Please Choose either Group or Client but not both. "
                        "Please clear the Group details to proceed with Client and vice versa.")

                if not self.cleaned_data.get("client_account_number"):
                    raise forms.ValidationError("Please enter Client Account Number.")
                elif self.cleaned_data.get("client_account_number"):
                    member_filter = Client.objects.filter(
                        first_name__iexact=self.cleaned_data.get("client_name"),
                        account_number=self.cleaned_data.get("client_account_number"))
                    if member_filter:
                        client = member_filter.first()
                        if not self.cleaned_data.get("member_loan_account_no"):
                            raise forms.ValidationError("Please enter the Member Loan Account Number.")
                        else:
                            loan_account_filter = LoanAccount.objects.filter(id=self.cleaned_data.get("member_loan_account_no"))
                            if loan_account_filter:
                                loan_account = loan_account_filter.first()
                                if not Payments.objects.filter(loan_account=loan_account, client=client):
                                    if loan_account.status == "Approved":
                                        if (self.cleaned_data.get("total_amount") and self.cleaned_data.get("amount")):
                                            if d(self.cleaned_data.get("total_amount")) == d(self.cleaned_data.get("amount")):
                                                if d(loan_account.loan_amount) != d(self.cleaned_data.get("total_amount")):
                                                    raise forms.ValidationError("Amount is not equal to the applied loan amount.")
                                            else:
                                                raise forms.ValidationError("Entered total amount is not equal to amount.")
                                    else:
                                        raise forms.ValidationError("Loan account is not yet approved")
                                else:
                                    raise forms.ValidationError("Loan account is already issued.")
                            else:
                                raise forms.ValidationError("Client does not have any Loan with this Loan A/C Number.")
                    else:
                        raise forms.ValidationError("No Member exists with this First Name and A/C number. Please enter correct details.")

        return self.cleaned_data

    def save(self, commit=True):
        instance = super(PaymentForm, self).save(commit=False)
        if not instance.id:
            if (
                self.cleaned_data.get("payment_type") == "TravellingAllowance" or
                self.cleaned_data.get("payment_type") == "Paymentofsalary"
            ):
                staff = User.objects.get(username__iexact=self.cleaned_data.get("staff_username"))
                instance.staff = staff
            elif self.cleaned_data.get("payment_type") == "SavingsWithdrawal":
                total_amount = d(self.cleaned_data.get("amount"))
                if self.cleaned_data.get("interest"):
                    instance.interest = d(self.cleaned_data.get("interest"))
                    total_amount += d(self.cleaned_data.get("interest"))

                if self.cleaned_data.get("client_name") and self.cleaned_data.get('client_account_number'):
                    client = Client.objects.filter(
                        first_name__iexact=self.cleaned_data.get("client_name"),
                        account_number=self.cleaned_data.get("client_account_number")).first()
                    if client:
                        savings_account = SavingsAccount.objects.filter(client=client).first()
                        if savings_account:
                            client_group = client.group_set.first()
                            if client_group:
                                group_savings_account = SavingsAccount.objects.filter(group=client_group).first()
                                if group_savings_account:
                                    instance.client = client
                                    instance.group = client_group

                                    # Deduct the balance from saving accounts.
                                    savings_account.savings_balance -= total_amount
                                    savings_account.total_withdrawals += total_amount
                                    savings_account.save()

                                    group_savings_account.savings_balance -= total_amount
                                    group_savings_account.total_withdrawals += total_amount
                                    group_savings_account.save()
                            else:
                                instance.client = client

                                savings_account.savings_balance -= total_amount
                                savings_account.total_withdrawals += total_amount
                                savings_account.save()
                else:
                    if self.cleaned_data.get("group_name"):
                        if self.cleaned_data.get("group_account_number"):
                            group = Group.objects.filter(
                                name__iexact=self.cleaned_data.get("group_name"),
                                account_number=self.cleaned_data.get("group_account_number")).first()
                            if group:
                                group_savings_account = SavingsAccount.objects.filter(group=group).first()
                                if group_savings_account:
                                    if d(group_savings_account.savings_balance) >= total_amount:
                                        client_group = group.clients.all()
                                        savings_accounts_filter = SavingsAccount.objects.filter(
                                            client__in=[client for client in client_group])
                                        if savings_accounts_filter:
                                            deduct_amount = total_amount / d(len(savings_accounts_filter))
                                            for savings_account in savings_accounts_filter:
                                                savings_account.savings_balance -= d(deduct_amount)
                                                savings_account.total_withdrawals += d(deduct_amount)
                                                savings_account.save()

                                    instance.group = group

                                    group_savings_account.savings_balance -= total_amount
                                    group_savings_account.total_withdrawals += total_amount
                                    group_savings_account.save()

            elif self.cleaned_data.get("payment_type") == "Loans":
                if self.cleaned_data.get("group_name") and not self.cleaned_data.get("client_name"):
                    group = Group.objects.filter(
                        name__iexact=self.cleaned_data.get("group_name"),
                        account_number=self.cleaned_data.get("group_account_number")).first()
                    if group:
                        loan_account = LoanAccount.objects.filter(
                            id=self.cleaned_data.get("group_loan_account_no")).first()
                        if loan_account:
                            clients_list = group.clients.all()
                            if len(clients_list) != 0:
                                instance.group = group
                                instance.loan_account = loan_account
                                loan_account.loan_issued_date = datetime.datetime.now().date()
                                loan_account.loan_issued_by = self.user
                                loan_account.save()
                                for client in clients_list:
                                    if client.email and client.email.strip():
                                        send_email_template(
                                            subject="Group Loan (ID: %s) application amount has been Issued."
                                                    % loan_account.account_no,
                                            template_name="emails/group/loan_issued.html",
                                            receipient=client.email,
                                            ctx={
                                                "client": client,
                                                "loan_account": loan_account,
                                                "link_prefix": settings.SITE_URL,
                                            },
                                        )
                if self.cleaned_data.get("client_name") and not self.cleaned_data.get("group_name"):
                    if self.cleaned_data.get("client_account_number"):
                        client = Client.objects.filter(
                            first_name__iexact=self.cleaned_data.get("client_name"),
                            account_number=self.cleaned_data.get("client_account_number")).first()
                        if client:
                            loan_account = LoanAccount.objects.filter(id=self.cleaned_data.get("member_loan_account_no")).first()
                            if loan_account:
                                instance.client = client
                                instance.loan_account = loan_account
                                loan_account.loan_issued_date = datetime.datetime.now().date()
                                loan_account.loan_issued_by = self.user
                                loan_account.save()
                                if loan_account.client:
                                    if loan_account.client.email and loan_account.client.email.strip():
                                        send_email_template(
                                            subject="Your application for the Personal Loan (ID: %s) amount has been Issued." % loan_account.account_no,
                                            template_name="emails/client/loan_issued.html",
                                            receipient=loan_account.client.email,
                                            ctx={
                                                "client": loan_account.client,
                                                "loan_account": loan_account,
                                                "link_prefix": settings.SITE_URL,
                                            },
                                        )
            elif self.cleaned_data.get('payment_type') == 'FixedWithdrawal':
                if self.cleaned_data.get("client_name") and not self.cleaned_data.get("group_name"):
                    if self.cleaned_data.get("client_account_number"):
                        client = Client.objects.filter(
                            first_name__iexact=self.cleaned_data.get("client_name"),
                            account_number=self.cleaned_data.get("client_account_number")).first()
                        if client:
                            if self.cleaned_data.get('fixed_deposit_account_no'):
                                fixed_deposits_account = FixedDeposits.objects.filter(
                                    client=client,
                                    fixed_deposit_number=self.cleaned_data.get('fixed_deposit_account_no')
                                ).exclude(status='Closed').first()
                                if fixed_deposits_account:
                                    instance.client = client
                                    instance.fixed_deposit_account = fixed_deposits_account
                                    fixed_deposits_account.total_withdrawal_amount_principle = self.cleaned_data.get('total_amount')
                                    fixed_deposits_account.total_withdrawal_amount_interest = self.cleaned_data.get('interest')
                                    fixed_deposits_account.status = 'Closed'
                                    fixed_deposits_account.save()
            elif self.cleaned_data.get('payment_type') == 'RecurringWithdrawal':
                if self.cleaned_data.get("client_name") and not self.cleaned_data.get("group_name"):
                    if self.cleaned_data.get("client_account_number"):
                        client = Client.objects.filter(
                            first_name__iexact=self.cleaned_data.get("client_name"),
                            account_number=self.cleaned_data.get("client_account_number")).first()
                        if client:
                            if self.cleaned_data.get('recurring_deposit_account_no'):
                                recurring_deposits_account = RecurringDeposits.objects.filter(
                                    client=client,
                                    reccuring_deposit_number=self.cleaned_data.get('recurring_deposit_account_no')
                                ).exclude(status='Closed', number_of_payments=0).first()
                                if recurring_deposits_account:
                                    instance.client = client
                                    instance.recurring_deposit_account = recurring_deposits_account
                                    recurring_deposits_account.total_withdrawal_amount_principle = self.cleaned_data.get('total_amount')
                                    recurring_deposits_account.total_withdrawal_amount_interest = self.cleaned_data.get('interest')
                                    recurring_deposits_account.status = 'Closed'
                                    recurring_deposits_account.save()
        if commit:
            instance.save()
        return instance


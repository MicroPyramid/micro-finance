from django import forms
from django.core.validators import MinValueValidator
from django.forms.utils import ErrorList

from micro_admin.models import User, Client, Receipts, Payments, LoanAccount, Group, SavingsAccount


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
            self.loan_account = LoanAccount.objects.filter(account_no=self.cleaned_data.get("group_loan_account_no")).last()
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
                    if not ((self.cleaned_data.get("loanprinciple_amount", 0)) <= (loan_account.total_loan_balance)):
                        errors = self._errors.setdefault("message1", ErrorList())
                        errors.append("Amount is greater than loan balance.")
                        raise forms.ValidationError(errors)
                    else:
                        if (self.cleaned_data.get("loaninterest_amount", 0)) > (loan_account.interest_charged):
                            errors = self._errors.setdefault("message1", ErrorList())
                            errors.append("Entered interest amount is greater than interest charged.")
                            raise forms.ValidationError(errors)
                        elif((self.cleaned_data.get("loaninterest_amount", 0)) >
                                (loan_account.loan_amount) or
                                (self.cleaned_data.get("loanprinciple_amount", 0)) >
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
                            if not loan_account.group:
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
           self.cleaned_data.get("loaninterest_amount") > 0):
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
        elif (self.cleaned_data.get("loanprinciple_amount") or
              self.cleaned_data.get("loanprocessingfee_amount") or
              self.cleaned_data.get("loaninterest_amount")) and\
                not (loan_account_no or group_loan_account_no):
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
            self.group_loan_account = LoanAccount.objects.filter(group=self.group, client=self.client,
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
        if self.cleaned_data.get("savingsdeposit_thrift_amount") or self.cleaned_data.get("recurringdeposit_amount"):
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
                self.verify_loan(self.group_loan_account)
        return self.cleaned_data


# partially done
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
    interest = forms.DecimalField(required=False)

    class Meta:
        model = Payments
        fields = ["date", "branch", "voucher_number", "payment_type", "amount", "interest", "total_amount", "totalamount_in_words"]

    def clean(self):
        errors = self._errors.setdefault("message1", ErrorList())
        if not (self.cleaned_data.get("amount") != 0 and self.cleaned_data.get("total_amount") != 0):
            errors.append("Voucher can't be generated with amount/total amount zero")
            raise forms.ValidationError(errors)
        if self.cleaned_data.get("payment_type") == "TravellingAllowance" or self.cleaned_data.get("payment_type") == "Paymentofsalary":
            if not self.cleaned_data.get("staff_username"):
                errors.append("Please enter Employee Username")
                raise forms.ValidationError(errors)
            else:
                self.staff = User.objects.filter(username__iexact=self.cleaned_data.get("staff_username")).first()
                if not self.staff:
                    errors.append("Entered Employee Username is incorrect")
                if self.cleaned_data.get("interest"):
                    errors.append("Interest must be empty for TA and Payment of salary Voucher.")
                    raise forms.ValidationError(errors)
        elif self.cleaned_data.get("payment_type") == "PrintingCharges" or \
                self.cleaned_data.get("payment_type") == "StationaryCharges" or \
                self.cleaned_data.get("payment_type") == "OtherCharges":
            if self.cleaned_data.get("interest"):
                errors.append("Interest must be empty for Charges Voucher.")
                raise forms.ValidationError(errors)
            else:
                if not (self.cleaned_data.get("total_amount") == self.cleaned_data.get("amount")):
                    errors.append("Entered total amount is not equal to amount.")
                    raise forms.ValidationError(errors)
        elif self.cleaned_data.get("payment_type") == "SavingsWithdrawal":
            if not self.cleaned_data.get("client_name"):
                errors.append("Please enter the Member First Name")
                raise forms.ValidationError(errors)
            if not self.cleaned_data.get("client_account_number"):
                errors.append("Please enter the Member Account number")
                raise forms.ValidationError(errors)
            self.client = Client.objects.get(first_name__iexact=self.cleaned_data.get("client_name"),
                                             account_number=self.cleaned_data.get("client_account_number"))

        elif self.cleaned_data.get("payment_type") == "Loans":
            pass

        return self.cleaned_data

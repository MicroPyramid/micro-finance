from decimal import Decimal

from django import forms
from django.forms.utils import ErrorList

from micro_admin.models import(
    Client,
    Receipts,
    LoanAccount,
    Group,
    SavingsAccount,
)


class ReceiptForm(forms.ModelForm):

    date = forms.DateField(input_formats=["%m/%d/%Y"], required=True)
    name = forms.CharField(max_length=100, required=True)
    account_number = forms.CharField(max_length=100, required=True)
    savingsdeposit_thrift_amount = forms.DecimalField(required=False)
    fixeddeposit_amount = forms.DecimalField(required=False)
    recurringdeposit_amount = forms.DecimalField(required=False)
    insurance_amount = forms.DecimalField(required=False)
    # group
    group_name = forms.CharField(max_length=100, required=False)
    group_account_number = forms.CharField(max_length=100, required=False)
    # loan
    loan_account_no = forms.CharField(max_length=100, required=False)
    group_loan_account_no = forms.CharField(max_length=100, required=False)
    loanprocessingfee_amount = forms.DecimalField(required=False)
    demand_loanprinciple = forms.DecimalField(required=False)
    demand_loaninterest = forms.DecimalField(required=False)
    loanprinciple_amount = forms.DecimalField(required=False)
    loaninterest_amount = forms.DecimalField(required=False)
    # fees
    sharecapital_amount = forms.DecimalField(required=False)
    bookfee_amount = forms.DecimalField(required=False)
    entrancefee_amount = forms.DecimalField(required=False)
    membershipfee_amount = forms.DecimalField(required=False)

    class Meta:
        model = Receipts
        fields = ("date",
                  "branch",
                  "receipt_number")

    def clean(self):
        self.savings_account = None
        self.loan_account = None
        self.group_savings_account = None
        self.group_loan_account = None
        errors = self._errors.setdefault("message1", ErrorList())
        self.client = Client.objects.filter(
            first_name__iexact=self.data.get("name"),
            account_number=self.data.get("account_number")
        ).last()
        if not self.client:
            errors.append(
                "No Client exists with this First Name and Account number."
            )
            raise forms.ValidationError(errors)
        # client loan a/c
        loan_account_no = self.data.get("loan_account_no")
        if loan_account_no:
            self.loan_account = LoanAccount.objects.filter(
                client=self.client,
                account_no=loan_account_no
            ).last()
            if not self.loan_account:
                errors.append(
                    """
                    Loan does not exists with this
                    Loan Account Number for this Member.
                    """
                )
                raise forms.ValidationError(errors)
        # client group
        self.client_group = self.client.group_set.first()
        group_name = self.data.get("group_name")
        group_account_number = self.data.get("group_account_number")
        if group_name and group_account_number:
            self.group = Group.objects.filter(
                name__iexact=group_name,
                account_number=group_account_number
            ).last()
            if not self.group:
                    errors.append(
                        """
                        No Group exists with given name and account number.
                        """
                    )
                    raise forms.ValidationError(errors)
        if group_name or group_account_number:
            errors.append(
                """
                Please enter both Group Name and Account Number.
                """
            )
            raise forms.ValidationError(errors)
        # client group a/c
        group_loan_account_no = self.data.get("group_loan_account_no")
        if group_loan_account_no:
            self.group_loan_account = LoanAccount.objects.filter(
                group=self.group,
                account_no=group_loan_account_no
            ).last()
            if not self.group_loan_account:
                errors.append(
                    """
                    Loan does not exists with this Loan Account Number for this Group.
                    """
                )
            raise forms.ValidationError(errors)
        # cannot pay both loans at once
        if self.group_loan_account and self.loan_account:
            errors.append(
                """
                Unable pay personal loan and group loan at once.
                """
            )
            raise forms.ValidationError(errors)
        # check personal savings a/c
        if self.data.get("savingsdeposit_thrift_amount") or self.data.get("recurringdeposit_amount"):
            self.savings_account = SavingsAccount.objects.filter(
                client=self.client
            ).last()
            if not self.savings_account:
                errors.append(
                    """
                    Member does not have savings account
                    """
                )
                raise forms.ValidationError(errors)
        # check group savings a/c
        if self.data.get("savingsdeposit_thrift_amount"):
            self.group_savings_account = SavingsAccount.objects.filter(
                group=self.client_group
            ).last()

        if self.data.get("loanprinciple_amount") \
           or Decimal(self.data.get("loaninterest_amount")) != 0:
            if self.loan_account and self.group_loan_account:
                if self.loan_account.status == "Approved" and \
                   self.group_loan_account.status == "Approved":
                    if not self.group_loan_account.loan_issued_date:
                        errors.append(
                            """
                            Loan Payment has not yet done.
                            """
                        )
                        raise forms.ValidationError(errors)
                    else:
                        if not (Decimal(self.loan_account.total_loan_balance) or
                                Decimal(self.loan_account.interest_charged) or
                                Decimal(self.loan_account.loan_repayment_amount) or
                                Decimal(self.loan_account.principle_repayment)):
                            errors.append(
                                """
                                Loan has been cleared sucessfully.
                                """
                            )
                            raise forms.ValidationError(errors)
                        else:
                            if not (Decimal(self.data.get("loanprinciple_amount")) <=
                                    Decimal(self.loan_account.total_loan_balance)):
                                errors.append(
                                    """
                                    Amount is greater than loan balance.
                                    """
                                )
                                raise forms.ValidationError(errors)
                            else:
                                if Decimal(self.data.get("loaninterest_amount")) >\
                                   Decimal(self.loan_account.interest_charged):
                                    errors.append(
                                        """
                                        Entered interest amount is greater than interest charged.
                                        """
                                    )
                                    raise forms.ValidationError(errors)
                                elif(Decimal(self.data.get("loaninterest_amount")) >
                                        Decimal(self.loan_account.loan_amount) or
                                        Decimal(self.data.get("loanprinciple_amount")) >
                                        Decimal(self.loan_account.loan_amount)):
                                    errors.append(
                                        """
                                        Amount is greater than issued loan amount. Transaction can't be done.
                                        """
                                    )
                                    raise forms.ValidationError(errors)
                                else:
                                    self.loan_account.total_loan_amount_repaid += Decimal(self.data.get("loanprinciple_amount"))
                                    self.loan_account.total_interest_repaid += Decimal(self.data.get("loaninterest_amount"))
                                    self.loan_account.total_loan_paid = Decimal(self.loan_account.total_loan_amount_repaid) + \
                                        Decimal(self.loan_account.total_interest_repaid)
                                    self.loan_account.total_loan_balance -= Decimal(self.data.get("loanprinciple_amount"))
                                    self.loan_account.no_of_repayments_completed += self.loan_account.loan_repayment_every

                                    self.group_loan_account.total_loan_amount_repaid += Decimal(self.data.get("loanprinciple_amount"))
                                    self.group_loan_account.total_interest_repaid += Decimal(self.data.get("loaninterest_amount"))
                                    self.group_loan_account.total_loan_paid = Decimal(self.group_loan_account.total_loan_amount_repaid) +\
                                        Decimal(self.group_loan_account.total_interest_repaid)
                                    self.group_loan_account.total_loan_balance -= Decimal(self.data.get("loanprinciple_amount"))

                                    if Decimal(self.loan_account.total_loan_amount_repaid) == Decimal(self.loan_account.loan_amount) and\
                                       Decimal(self.loan_account.total_loan_balance) == 0:
                                        if Decimal(self.data.get("loanprinciple_amount")) > \
                                           Decimal(self.loan_account.principle_repayment):
                                            errors.append(
                                                """
                                                Amount is greater than issued loan amount. Transaction can't be done.
                                                """
                                            )
                                            raise forms.ValidationError(errors)
                elif self.loan_account.status == "Applied":
                    errors.append(
                        """
                        Member Loan / Group Loan is under pending for approval.
                        """
                    )
                    raise forms.ValidationError(errors)
                elif self.loan_account.status == "Rejected":
                    errors.append(
                        """
                        Member Loan has been Rejected.
                        """
                    )
                    raise forms.ValidationError(errors)
                elif self.loan_account.status == "Closed":
                    errors.append(
                        """
                        Member Loan has been Closed.
                        """
                    )
                    raise forms.ValidationError(errors)
                elif self.group_loan_account.status == "Applied":
                    errors.append(
                        """
                        Group Loan is under pending for approval.
                        """
                    )
                    raise forms.ValidationError(errors)
                elif self.group_loan_account.status == "Rejected":
                    raise forms.ValidationError(
                        """
                        Group Loan has been Rejected.
                        """
                    )
                elif self.group_loan_account.status == "Closed":
                    errors.append(
                        """
                        Group Loan has been Closed.
                        """
                    )
                    raise forms.ValidationError(errors)
        return self.data

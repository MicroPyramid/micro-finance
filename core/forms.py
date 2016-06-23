from decimal import Decimal
from django import forms
from micro_admin.models import(
    Client,
    Receipts,
    LoanAccount,
    Group,
    SavingsAccount,
)


class ReceiptForm(forms.ModelForm):

    date = forms.DateField(input_formats=["%m/%d/%Y"])
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

        self.client = Client.objects.filter(
            first_name__iexact=self.data.get("name"),
            account_number=self.data.get("account_number")
        ).last()
        if not self.client:
            raise forms.ValidationError(
                "No Client exists with this First Name and Account number."
            )
        # client loan a/c
        loan_account_no = self.data.get("loan_account_no")
        if loan_account_no:
            self.loan_account = LoanAccount.objects.filter(
                client=self.client,
                account_no=loan_account_no
            ).last()
            if not self.loan_account:
                raise forms.ValidationError(
                    """
                    Loan does not exists with this
                    Loan Account Number for this Member.
                    """
                )
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
                    raise forms.ValidationError(
                        """
                        No Group exists with given name and account number.
                        """
                    )
        if group_name or group_account_number:
            raise forms.ValidationError(
                """
                Please enter both Group Name and Account Number.
                """
            )
        # client group a/c
        group_loan_account_no = self.data.get("group_loan_account_no")
        if group_loan_account_no:
            self.group_loan_account = LoanAccount.objects.filter(
                group=self.group,
                account_no=group_loan_account_no
            ).last()
            if not self.group_loan_account:
                raise forms.ValidationError(
                    """
                    Loan does not exists with this Loan Account Number for this Group.
                    """
                )
        # cannot pay both loans at once
        if self.group_loan_account and self.loan_account:
            raise forms.ValidationError(
                """
                Unable pay personal loan and group loan at once.
                """
            )
        # check personal savings a/c
        if self.data.get("savingsdeposit_thrift_amount") or self.data.get("recurringdeposit_amount"):
            self.savings_account = SavingsAccount.objects.filter(
                client=self.client
            ).last()
            if not self.savings_account:
                raise forms.ValidationError(
                    """
                    Member does not have savings account
                    """
                )
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
                        raise forms.ValidationError(
                            """
                            Loan Payment has not yet done.
                            """
                        )
                    else:
                        if not (Decimal(self.loan_account.total_loan_balance) or
                                Decimal(self.loan_account.interest_charged) or
                                Decimal(self.loan_account.loan_repayment_amount) or
                                Decimal(self.loan_account.principle_repayment)):
                            raise forms.ValidationError(
                                """
                                Loan has been cleared sucessfully.
                                """
                            )
                        else:
                            if not (Decimal(self.data.get("loanprinciple_amount")) <=
                                    Decimal(self.loan_account.total_loan_balance)):
                                raise forms.ValidationError(
                                    """
                                    Amount is greater than loan balance.
                                    """
                                )
                            else:
                                if Decimal(self.data.get("loaninterest_amount")) >\
                                   Decimal(self.loan_account.interest_charged):
                                    raise forms.ValidationError(
                                        """
                                        Entered interest amount is greater than interest charged.
                                        """
                                    )

                elif self.loan_account.status == "Applied":
                    pass
        return self.data

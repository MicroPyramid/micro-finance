from django.http import JsonResponse
from django.views.generic import(CreateView, FormView,)
from .mixins import LoginRequiredMixin
from .forms import ReceiptForm, PaymentForm, ClientLoanAccountsForm, GetLoanDemandsForm
from micro_admin.models import Branch, Receipts, PAYMENT_TYPES, Payments, LoanAccount


class ClientLoanAccountsView(LoginRequiredMixin, FormView):

    form_class = ClientLoanAccountsForm

    def form_valid(self, form):
        if form.client:
            loan_accounts = LoanAccount.objects.filter(
                client=form.client,
                total_loan_balance__gt=0
            ).values_list("account_no", "loan_amount")
            groups = form.client.group_set.all()
            default_group = groups.first()
            group_accounts = LoanAccount.objects.filter(
                group__in=groups
            ).values_list("account_no", "loan_amount")
        else:
            loan_accounts = []
            group_accounts = []
            default_group = None
        group = {"group_name": default_group.name if default_group else "",
                 "group_account_number": default_group.account_number if default_group else ""}
        data = {"error": False,
                "loan_accounts": list(loan_accounts),
                "group_accounts": list(group_accounts),
                "group": group if default_group else False}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)


class GetLoanDemandsView(LoginRequiredMixin, FormView):

    form_class = GetLoanDemandsForm

    def form_valid(self, form):
        data = {
            "error": False,
            "demand_loanprinciple": form.loan_account.principle_repayment or 0,
            "demand_loaninterest": form.loan_account.interest_charged or 0
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)


class Receipts_Deposit(LoginRequiredMixin, CreateView):
    template_name = "core/receiptsform.html"
    model = Receipts
    form_class = ReceiptForm

    def get_context_data(self, *args, **kwargs):
        context = super(Receipts_Deposit, self).get_context_data(*args, **kwargs)

        if self.request.method == "GET":
            context["branches"] = Branch.objects.all()
        return context

    def form_invalid(self, form):
        data = {"error": True,
                "message": form.errors}
        return JsonResponse(data)

    def form_valid(self, form):
        self.client = form.client
        self.client_group = form.client_group
        self.var_demand_loanprinciple_amount_atinstant = 0
        self.var_demand_loaninterest_amount_atinstant = 0
        if form.cleaned_data.get("sharecapital_amount"):
            self.client.sharecapital_amount += \
                (form.cleaned_data.get("sharecapital_amount", 0))
        if form.cleaned_data.get("entrancefee_amount"):
            self.client.entrancefee_amount += \
                (form.cleaned_data.get("entrancefee_amount", 0))
        if form.cleaned_data.get("membershipfee_amount"):
            self.client.membershipfee_amount += \
                (form.cleaned_data.get("membershipfee_amount", 0))
        if form.cleaned_data.get("bookfee_amount"):
            self.client.bookfee_amount += (form.cleaned_data.get("bookfee_amount", 0))
        # loan processing fee amount
        if form.loan_account:
            # personal
            self.loan_account = form.loan_account
            if form.cleaned_data.get("loan_account_no"):
                if form.cleaned_data.get("loanprocessingfee_amount"):
                    self.loan_account.loanprocessingfee_amount += \
                        (form.cleaned_data.get("loanprocessingfee_amount", 0))
            if self.loan_account.status == "Approved":
                if (self.loan_account.total_loan_balance)\
                   or (self.loan_account.interest_charged)\
                   or (self.loan_account.loan_repayment_amount)\
                   or (self.loan_account.principle_repayment):
                    self.var_demand_loanprinciple_amount_atinstant = \
                        (self.loan_account.principle_repayment)
                    self.var_demand_loaninterest_amount_atinstant = \
                        (self.loan_account.interest_charged)
        if form.group_loan_account:
            # group
            self.group_loan_account = form.group_loan_account
            if form.cleaned_data.get("group_loan_account_no"):
                if form.cleaned_data.get("loanprocessingfee_amount"):
                    self.group_loan_account.loanprocessingfee_amount += \
                        (form.cleaned_data.get("loanprocessingfee_amount"))
        # savings deposit thrift amount
        if form.savings_account:
            self.savings_account = form.savings_account
            if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                # personal
                self.savings_account.savings_balance += \
                    (form.cleaned_data.get("savingsdeposit_thrift_amount"))
                self.savings_account.total_deposits += \
                    (form.cleaned_data.get("savingsdeposit_thrift_amount"))

            if form.cleaned_data.get("recurringdeposit_amount"):
                self.savings_account.recurringdeposit_amount += \
                    (form.cleaned_data.get("recurringdeposit_amount"))
        if form.group_savings_account:
            # group
            self.group_savings_account = form.group_savings_account
            if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                self.group_savings_account.savings_balance += \
                    (form.cleaned_data.get("savingsdeposit_thrift_amount"))
                self.group_savings_account.total_deposits += \
                    (form.cleaned_data.get("savingsdeposit_thrift_amount"))

        if form.cleaned_data.get("insurance_amount"):
            self.client.insurance_amount += (form.cleaned_data.get("insurance_amount", 0))

        if form.cleaned_data.get("loanprinciple_amount") \
           or (form.cleaned_data.get("loaninterest_amount")) != 0:
            if form.loan_account:
                # now
                if not ((self.loan_account.total_loan_amount_repaid) ==
                        (self.loan_account.loan_amount) and
                        (self.loan_account.total_loan_balance) == 0):
                    if (form.cleaned_data.get("loaninterest_amount")) == \
                       (self.loan_account.interest_charged):
                        if (form.cleaned_data.get("loanprinciple_amount")) ==\
                           (self.loan_account.principle_repayment):
                            self.loan_account.loan_repayment_amount = 0
                            self.loan_account.principle_repayment = 0
                            self.loan_account.interest_charged = 0
                        elif (form.cleaned_data.get("loanprinciple_amount")) <\
                                (self.loan_account.principle_repayment):
                            balance_principle = (self.loan_account.principle_repayment) -\
                                (form.cleaned_data.get("loanprinciple_amount"))
                            self.loan_account.principle_repayment = balance_principle
                            self.loan_account.loan_repayment_amount = balance_principle
                            self.loan_account.interest_charged = 0
                    else:
                        if form.cleaned_data.get("loaninterest_amount"):
                            if form.cleaned_data.get("loaninterest_amount") < self.loan_account.interest_charged:
                                if form.cleaned_data.get("loanprinciple_amount") == self.loan_account.principle_repayment:
                                    balance_interest = self.loan_account.interest_charged -\
                                        form.cleaned_data.get("loaninterest_amount")
                                    self.loan_account.interest_charged = balance_interest
                                    self.loan_account.loan_repayment_amount = balance_interest
                                    self.loan_account.principle_repayment = 0
                                if form.cleaned_data.get("loanprinciple_amount"):
                                    if form.cleaned_data.get("loanprinciple_amount") < \
                                            self.loan_account.principle_repayment:
                                        balance_principle = self.loan_account.principle_repayment -\
                                            form.cleaned_data.get("loanprinciple_amount")
                                        self.loan_account.principle_repayment = balance_principle
                                        balance_interest = self.loan_account.interest_charged -\
                                            form.cleaned_data.get("loaninterest_amount")
                                        self.loan_account.interest_charged = balance_interest
                                        self.loan_account.loan_repayment_amount = balance_principle +\
                                            balance_interest

                elif self.loan_account.total_loan_amount_repaid <\
                        self.loan_account.loan_amount and self.loan_account.total_loan_balance:
                    if int(self.loan_account.no_of_repayments_completed) >=\
                            int(self.loan_account.loan_repayment_period):
                        if form.cleaned_data.get("loaninterest_amount") ==\
                                self.loan_account.interest_charged:
                            if self.loan_account.interest_type == "Flat":
                                self.loan_account.interest_charged = (
                                    (self.loan_account.loan_amount * (
                                        self.loan_account.annual_interest_rate / 12)) / 100)
                            elif self.loan_account.interest_type == "Declining":
                                self.loan_account.interest_charged = (
                                    ((self.loan_account.total_loan_balance * (
                                        self.loan_account.annual_interest_rate / 12)) / 100))
                        elif form.cleaned_data.get("loaninterest_amount") < self.loan_account.interest_charged:
                            balance_interest = self.loan_account.interest_charged -\
                                form.cleaned_data.get("loaninterest_amount")
                            if self.loan_account.interest_type == "Flat":
                                interest_charged = (
                                    ((self.loan_account.loan_amount * (
                                        self.loan_account.annual_interest_rate / 12)) / 100))
                            elif self.loan_account.interest_type == "Declining":
                                interest_charged = ((((self.loan_account.total_loan_balance) * (
                                    (self.loan_account.annual_interest_rate) / 12)) / 100))
                            self.loan_account.interest_charged = (balance_interest + interest_charged)

                        if form.cleaned_data.get("loanprinciple_amount") == \
                                self.loan_account.principle_repayment:
                            self.loan_account.principle_repayment = \
                                self.loan_account.total_loan_balance
                            self.loan_account.loan_repayment_amount = \
                                ((self.loan_account.total_loan_balance) +
                                    (self.loan_account.interest_charged))
                        elif form.cleaned_data.get("loanprinciple_amount") <\
                                (self.loan_account.principle_repayment):
                            balance_principle = (((self.loan_account.loan_repayment_amount) -
                                                  (self.loan_account.interest_charged)) -
                                                 (form.cleaned_data.get("loanprinciple_amount")))
                            self.loan_account.principle_repayment =\
                                ((self.loan_account.total_loan_balance) + (balance_principle))
                            self.loan_account.loan_repayment_amount = (
                                (self.loan_account.total_loan_balance) +
                                (self.loan_account.interest_charged) +
                                (balance_principle))

                    elif int(self.loan_account.no_of_repayments_completed) <\
                            int(self.loan_account.loan_repayment_period):
                        principle_repayable = (
                            (self.loan_account.loan_amount) / (self.loan_account.loan_repayment_period))
                        if self.loan_account.interest_type == "Flat":
                            if (self.data.get("loaninterest_amount")) ==\
                                    (self.loan_account.interest_charged):
                                self.loan_account.interest_charged = (
                                    int(self.loan_account.loan_repayment_every) * (
                                        ((self.loan_account.loan_amount) *
                                            ((self.loan_account.annual_interest_rate) / 12)) / 100))
                            elif (form.cleaned_data.get("loaninterest_amount")) <\
                                    (self.loan_account.interest_charged):
                                balance_interest = \
                                    (self.loan_account.interest_charged) -\
                                    (form.cleaned_data.get("loaninterest_amount"))
                                interest_charged = (
                                    int(self.loan_account.loan_repayment_every) * (
                                        ((self.loan_account.loan_amount) * (
                                            (self.loan_account.annual_interest_rate) / 12)) / 100))
                                self.loan_account.interest_charged = (balance_interest + interest_charged)
                        elif self.loan_account.interest_type == "Declining":
                            if (form.cleaned_data.get("loaninterest_amount")) ==\
                                    (self.loan_account.interest_charged):
                                self.loan_account.interest_charged = (
                                    int(self.loan_account.loan_repayment_every) * (
                                        ((self.loan_account.total_loan_balance) * (
                                            (self.loan_account.annual_interest_rate) / 12)) / 100))
                            elif (form.cleaned_data.get("loaninterest_amount")) <\
                                    (self.loan_account.interest_charged):
                                balance_interest = (self.loan_account.interest_charged) -\
                                    (form.cleaned_data.get("loaninterest_amount"))
                                interest_charged = (int(self.loan_account.loan_repayment_every) *
                                                    (((self.loan_account.total_loan_balance) * (
                                                        (self.loan_account.annual_interest_rate) / 12)) / 100))
                                self.loan_account.interest_charged = (balance_interest + interest_charged)

                        if (form.cleaned_data.get("loanprinciple_amount")) == (
                                (int(self.loan_account.loan_repayment_every) * (
                                    principle_repayable))):
                            if (self.loan_account.total_loan_balance) <\
                                ((int(self.loan_account.loan_repayment_every) * (
                                    principle_repayable))):
                                self.loan_account.principle_repayment = (
                                    self.loan_account.total_loan_balance)
                                self.loan_account.loan_repayment_amount = (
                                    (self.loan_account.total_loan_balance) +
                                    (self.loan_account.interest_charged))
                            else:
                                self.loan_account.principle_repayment = (
                                    int(self.loan_account.loan_repayment_every) *
                                    ((self.loan_account.loan_amount) /
                                        (self.loan_account.loan_repayment_period)))
                                self.loan_account.loan_repayment_amount = (
                                    (self.loan_account.principle_repayment) +
                                    (self.loan_account.interest_charged))
                        elif (form.cleaned_data.get("loanprinciple_amount")) <\
                                ((int(self.loan_account.loan_repayment_every) * (principle_repayable))):
                            balance_principle = (
                                ((int(self.loan_account.loan_repayment_every) *
                                    (principle_repayable))) - (form.cleaned_data.get("loanprinciple_amount")))
                            if (self.loan_account.total_loan_balance) <\
                                    ((int(self.loan_account.loan_repayment_every) *
                                        (principle_repayable))):
                                self.loan_account.principle_repayment = (self.loan_account.total_loan_balance)
                                self.loan_account.loan_repayment_amount = (
                                    (self.loan_account.total_loan_balance) + (self.loan_account.interest_charged))
                            else:
                                self.loan_account.principle_repayment = (
                                    (int(self.loan_account.loan_repayment_every) *
                                        (principle_repayable)) + (balance_principle))
                                self.loan_account.loan_repayment_amount = (
                                    (int(self.loan_account.loan_repayment_every) *
                                        (principle_repayable)) +
                                    (self.loan_account.interest_charged) + (balance_principle))

        if form.cleaned_data.get("sharecapital_amount") or\
                form.cleaned_data.get("entrancefee_amount") or\
                form.cleaned_data.get("membershipfee_amount") or\
                form.cleaned_data.get("bookfee_amount") or\
                form.cleaned_data.get("loanprocessingfee_amount") or\
                form.cleaned_data.get("savingsdeposit_thrift_amount") or\
                form.cleaned_data.get("fixeddeposit_amount") or\
                form.cleaned_data.get("recurringdeposit_amount") or\
                form.cleaned_data.get("loanprinciple_amount") or\
                form.cleaned_data.get("insurance_amount") or\
                form.cleaned_data.get("loaninterest_amount") != 0:
            receipt_number = form.cleaned_data.get("receipt_number")
            branch = Branch.objects.get(id=form.data.get("branch"))
            date = form.cleaned_data.get("date")
            receipt = Receipts.objects.create(
                date=date,
                branch=branch,
                receipt_number=receipt_number,
                client=self.client,
                group=self.client_group,
                staff=self.request.user
            )
            if form.cleaned_data.get("sharecapital_amount"):
                receipt.sharecapital_amount = form.cleaned_data.get("sharecapital_amount")
            if form.cleaned_data.get("entrancefee_amount"):
                receipt.entrancefee_amount = form.cleaned_data.get("entrancefee_amount")
            if form.cleaned_data.get("membershipfee_amount"):
                receipt.membershipfee_amount = form.cleaned_data.get("membershipfee_amount")
            if form.cleaned_data.get("bookfee_amount"):
                receipt.bookfee_amount = form.cleaned_data.get("bookfee_amount")
            if form.cleaned_data.get("loanprocessingfee_amount"):
                receipt.loanprocessingfee_amount = form.cleaned_data.get("loanprocessingfee_amount")
                if form.loan_account:
                    receipt.member_loan_account = self.loan_account
                if form.group_loan_account:
                    receipt.group_loan_account = self.group_loan_account
            if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                receipt.savingsdeposit_thrift_amount = form.cleaned_data.get("savingsdeposit_thrift_amount")
                receipt.savings_balance_atinstant = self.savings_account.savings_balance
            if form.cleaned_data.get("fixeddeposit_amount"):
                receipt.fixeddeposit_amount = form.cleaned_data.get("fixeddeposit_amount")
            if form.cleaned_data.get("recurringdeposit_amount"):
                receipt.recurringdeposit_amount = form.cleaned_data.get("recurringdeposit_amount")
            if form.cleaned_data.get("insurance_amount"):
                receipt.insurance_amount = form.cleaned_data.get("insurance_amount")
            if form.cleaned_data.get("loanprinciple_amount"):
                receipt.loanprinciple_amount = form.cleaned_data.get("loanprinciple_amount")
                if form.loan_account:
                    receipt.member_loan_account = self.loan_account
                if form.group_loan_account:
                    receipt.group_loan_account = self.group_loan_account
            if form.cleaned_data.get("loaninterest_amount") != 0:
                receipt.loaninterest_amount = form.cleaned_data.get("loaninterest_amount")
                if form.loan_account:
                    receipt.member_loan_account = self.loan_account
                if form.group_loan_account:
                    receipt.group_loan_account = self.group_loan_account
            if form.loan_account:
                receipt.demand_loanprinciple_amount_atinstant = self.var_demand_loanprinciple_amount_atinstant
                receipt.demand_loaninterest_amount_atinstant = self.var_demand_loaninterest_amount_atinstant
                receipt.principle_loan_balance_atinstant = self.loan_account.total_loan_balance
            # save data
            receipt.save()
            self.client.save()
            if form.loan_account:
                self.loan_account.save()
            if form.group_loan_account:
                self.group_loan_account.save()
            if form.savings_account:
                self.savings_account.save()
            if form.group_savings_account:
                self.group_savings_account.save()

        return JsonResponse({"error": False})


class PaySlip(LoginRequiredMixin, CreateView):
    template_name = "core/paymentform.html"
    model = Payments
    form_class = PaymentForm

    def get_context_data(self, *args, **kwargs):
        context = super(PaySlip, self).get_context_data(*args, **kwargs)

        if self.request.method == "GET":
            context["branches"] = Branch.objects.all()
            context["voucher_types"] = [voucher_type[0] for voucher_type in PAYMENT_TYPES]
        return context

    def form_invalid(self, form):
        data = {"error": True,
                "message": form.errors}
        return JsonResponse(data)

    def form_valid(self, form):

        return JsonResponse({"error": False})


# class GetmemberLoanAccounts(LoginRequiredMixin, view):

#     def post(self, request, )
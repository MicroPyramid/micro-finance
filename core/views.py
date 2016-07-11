from django.http import JsonResponse
from django.views.generic import(CreateView, FormView,)
from .mixins import LoginRequiredMixin
from .forms import ReceiptForm, PaymentForm, ClientLoanAccountsForm, GetLoanDemandsForm, GetFixedDepositsForm, GetRecurringDepositsForm, \
    GetFixedDepositsPaidForm, GetRecurringDepositsPaidForm, ClientDepositsAccountsForm
from micro_admin.models import Branch, Receipts, PAYMENT_TYPES, Payments, LoanAccount, Group, Client, FixedDeposits, RecurringDeposits
import decimal
from django.db.models import Q

d = decimal.Decimal


class ClientLoanAccountsView(LoginRequiredMixin, FormView):

    form_class = ClientLoanAccountsForm

    def form_valid(self, form):
        if form.client:
            loan_accounts_filter = LoanAccount.objects.filter(
                client=form.client,
                total_loan_balance__gt=0,
                status='Approved'
            ).exclude(loan_issued_by__isnull=True,
                      loan_issued_date__isnull=True)
            member_loan_has_payments = []
            for loan in loan_accounts_filter:
                payments = Payments.objects.filter(client=form.client, loan_account=loan)
                if payments:
                    member_loan_has_payments.append(loan.id)
            loan_accounts = loan_accounts_filter.filter(
                id__in=[int(x) for x in member_loan_has_payments]).values_list("account_no", "loan_amount")
            groups = form.client.group_set.all()
            default_group = groups.first()
            group_accounts_filter = LoanAccount.objects.filter(
                group=default_group,
                status='Approved'
            ).exclude(loan_issued_by__isnull=True,
                      loan_issued_date__isnull=True)
            group_loan_has_payments = []
            for loan in group_accounts_filter:
                payments = Payments.objects.filter(group=default_group, loan_account=loan)
                if payments:
                    group_loan_has_payments.append(loan.id)
            group_accounts = group_accounts_filter.filter(
                id__in=[int(x) for x in group_loan_has_payments]).values_list("account_no", "loan_amount")
            fixed_deposit_accounts = FixedDeposits.objects.filter(
                client=form.client,
                status='Opened'
            ).values_list("fixed_deposit_number", "fixed_deposit_amount")
            recurring_deposit_accounts = RecurringDeposits.objects.filter(
                client=form.client,
                status="Opened"
            ).values_list("reccuring_deposit_number", "recurring_deposit_amount")
        else:
            loan_accounts = []
            group_accounts = []
            fixed_deposit_accounts = []
            recurring_deposit_accounts = []
            default_group = None
        group = {"group_name": default_group.name if default_group else "",
                 "group_account_number": default_group.account_number if default_group else ""}
        data = {"error": False,
                "loan_accounts": list(loan_accounts),
                "group_accounts": list(group_accounts),
                "fixed_deposit_accounts": list(fixed_deposit_accounts),
                "recurring_deposit_accounts": list(recurring_deposit_accounts),
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


class GetFixedDepositAccountsView(LoginRequiredMixin, FormView):

    form_class = GetFixedDepositsForm

    def form_valid(self, form):
        data = {
            "error": False,
            "fixeddeposit_amount": form.fixed_deposit_account.fixed_deposit_amount or 0
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)


class GetRecurringDepositAccountsView(LoginRequiredMixin, FormView):

    form_class = GetRecurringDepositsForm

    def form_valid(self, form):
        data = {
            "error": False,
            "recurringdeposit_amount": form.recurring_deposit_account.recurring_deposit_amount or 0
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)


class Receipts_Deposit(LoginRequiredMixin, CreateView):
    template_name = 'core/receiptsform.html'
    model = Receipts
    form_class = ReceiptForm

    def loan_valid(self, form, loan_account):
            # now
        if loan_account.status == "Approved":
            if loan_account.loan_issued_date:
                if d(loan_account.total_loan_balance) or d(loan_account.interest_charged) or d(loan_account.loan_repayment_amount) or d(loan_account.principle_repayment) :
                    if form.cleaned_data.get("loanprinciple_amount") or form.cleaned_data.get("loaninterest_amount"):
                        if d(form.cleaned_data.get("loanprinciple_amount")) <= d(loan_account.total_loan_balance):
                            loan_account.total_loan_amount_repaid += d(form.cleaned_data.get("loanprinciple_amount"))
                            loan_account.total_interest_repaid += d(form.cleaned_data.get("loaninterest_amount", 0))
                            loan_account.total_loan_paid = d(d(loan_account.total_loan_amount_repaid) + d(loan_account.total_interest_repaid))
                            loan_account.total_loan_balance -= d(form.cleaned_data.get("loanprinciple_amount"))
                            loan_account.no_of_repayments_completed += loan_account.loan_repayment_every
                            if not ((loan_account.total_loan_amount_repaid) ==
                                    (loan_account.loan_amount) and
                                    (loan_account.total_loan_balance) == 0):
                                loan_account.save()
                                if (form.cleaned_data.get("loaninterest_amount")) == \
                                   (loan_account.interest_charged):
                                    if (form.cleaned_data.get("loanprinciple_amount")) ==\
                                       (loan_account.principle_repayment):
                                        loan_account.loan_repayment_amount = 0
                                        loan_account.principle_repayment = 0
                                        loan_account.interest_charged = 0
                                    elif (form.cleaned_data.get("loanprinciple_amount")) <\
                                            (loan_account.principle_repayment):
                                        balance_principle = (loan_account.principle_repayment) -\
                                            (form.cleaned_data.get("loanprinciple_amount"))
                                        loan_account.principle_repayment = balance_principle
                                        loan_account.loan_repayment_amount = balance_principle
                                        loan_account.interest_charged = 0
                                else:
                                    if form.cleaned_data.get("loaninterest_amount"):
                                        if form.cleaned_data.get("loaninterest_amount") < loan_account.interest_charged:
                                            if form.cleaned_data.get("loanprinciple_amount") == loan_account.principle_repayment:
                                                balance_interest = loan_account.interest_charged -\
                                                    form.cleaned_data.get("loaninterest_amount")
                                                loan_account.interest_charged = balance_interest
                                                loan_account.loan_repayment_amount = balance_interest
                                                loan_account.principle_repayment = 0
                                            if form.cleaned_data.get("loanprinciple_amount"):
                                                if form.cleaned_data.get("loanprinciple_amount") < \
                                                        loan_account.principle_repayment:
                                                    balance_principle = loan_account.principle_repayment -\
                                                        form.cleaned_data.get("loanprinciple_amount")
                                                    loan_account.principle_repayment = d(balance_principle)
                                                    balance_interest = loan_account.interest_charged -\
                                                        form.cleaned_data.get("loaninterest_amount")
                                                    loan_account.interest_charged = d(balance_interest)
                                                    loan_account.loan_repayment_amount = d(balance_principle) +\
                                                        d(balance_interest)
                                return loan_account
                            elif loan_account.total_loan_amount_repaid < loan_account.loan_amount and loan_account.total_loan_balance:
                                if int(loan_account.no_of_repayments_completed) >= int(loan_account.loan_repayment_period):
                                    if form.cleaned_data.get("loaninterest_amount") ==\
                                            loan_account.interest_charged:
                                        if loan_account.interest_type == "Flat":
                                            loan_account.interest_charged = (
                                                (loan_account.loan_amount * (
                                                    loan_account.annual_interest_rate / 12)) / 100)
                                        elif loan_account.interest_type == "Declining":
                                            loan_account.interest_charged = (
                                                ((loan_account.total_loan_balance * (
                                                    loan_account.annual_interest_rate / 12)) / 100))
                                    elif form.cleaned_data.get("loaninterest_amount") < loan_account.interest_charged:
                                        balance_interest = loan_account.interest_charged -\
                                            form.cleaned_data.get("loaninterest_amount")
                                        if loan_account.interest_type == "Flat":
                                            interest_charged = (
                                                ((loan_account.loan_amount * (
                                                    loan_account.annual_interest_rate / 12)) / 100))
                                        elif loan_account.interest_type == "Declining":
                                            interest_charged = ((((loan_account.total_loan_balance) * (
                                                (loan_account.annual_interest_rate) / 12)) / 100))
                                        loan_account.interest_charged = (balance_interest + interest_charged)

                                    if form.cleaned_data.get("loanprinciple_amount") == \
                                            loan_account.principle_repayment:
                                        loan_account.principle_repayment = \
                                            loan_account.total_loan_balance
                                        loan_account.loan_repayment_amount = \
                                            ((loan_account.total_loan_balance) +
                                                (loan_account.interest_charged))
                                    elif form.cleaned_data.get("loanprinciple_amount") <\
                                            (loan_account.principle_repayment):
                                        balance_principle = (((loan_account.loan_repayment_amount) -
                                                              (loan_account.interest_charged)) -
                                                             (form.cleaned_data.get("loanprinciple_amount")))
                                        loan_account.principle_repayment =\
                                            ((loan_account.total_loan_balance) + (balance_principle))
                                        loan_account.loan_repayment_amount = (
                                            (loan_account.total_loan_balance) +
                                            (loan_account.interest_charged) +
                                            (balance_principle))

                                elif int(loan_account.no_of_repayments_completed) < int(loan_account.loan_repayment_period):
                                    principle_repayable = (
                                        (loan_account.loan_amount) / (loan_account.loan_repayment_period))
                                    if loan_account.interest_type == "Flat":
                                        if (self.data.get("loaninterest_amount")) ==\
                                                (loan_account.interest_charged):
                                            loan_account.interest_charged = (
                                                int(loan_account.loan_repayment_every) * (
                                                    ((loan_account.loan_amount) *
                                                        ((loan_account.annual_interest_rate) / 12)) / 100))
                                        elif (form.cleaned_data.get("loaninterest_amount")) <\
                                                (loan_account.interest_charged):
                                            balance_interest = \
                                                d(loan_account.interest_charged) -\
                                                d(form.cleaned_data.get("loaninterest_amount"))
                                            interest_charged = (
                                                int(loan_account.loan_repayment_every) * (
                                                    ((loan_account.loan_amount) * (
                                                        (loan_account.annual_interest_rate) / 12)) / 100))
                                            loan_account.interest_charged = d(balance_interest + interest_charged)

                                    elif loan_account.interest_type == "Declining":
                                        if (form.cleaned_data.get("loaninterest_amount")) ==\
                                                (loan_account.interest_charged):
                                            loan_account.interest_charged = (
                                                int(loan_account.loan_repayment_every) * (
                                                    ((loan_account.total_loan_balance) * (
                                                        (loan_account.annual_interest_rate) / 12)) / 100))
                                        elif (form.cleaned_data.get("loaninterest_amount")) <\
                                                (loan_account.interest_charged):
                                            balance_interest = (loan_account.interest_charged) -\
                                                (form.cleaned_data.get("loaninterest_amount"))
                                            interest_charged = (int(loan_account.loan_repayment_every) *
                                                                (((loan_account.total_loan_balance) * (
                                                                    (loan_account.annual_interest_rate) / 12)) / 100))
                                            loan_account.interest_charged = (balance_interest + interest_charged)

                                    if (form.cleaned_data.get("loanprinciple_amount")) == (
                                            (int(loan_account.loan_repayment_every) * (
                                                principle_repayable))):
                                        if (loan_account.total_loan_balance) <\
                                            ((int(loan_account.loan_repayment_every) * (
                                                principle_repayable))):
                                            loan_account.principle_repayment = (
                                                loan_account.total_loan_balance)
                                            loan_account.loan_repayment_amount = (
                                                (loan_account.total_loan_balance) +
                                                (loan_account.interest_charged))
                                        else:
                                            loan_account.principle_repayment = (
                                                int(loan_account.loan_repayment_every) *
                                                ((loan_account.loan_amount) /
                                                    (loan_account.loan_repayment_period)))
                                            loan_account.loan_repayment_amount = (
                                                (loan_account.principle_repayment) +
                                                (loan_account.interest_charged))
                                    elif (form.cleaned_data.get("loanprinciple_amount")) <\
                                            ((int(loan_account.loan_repayment_every) * (principle_repayable))):
                                        balance_principle = (
                                            ((int(loan_account.loan_repayment_every) *
                                                (principle_repayable))) - (form.cleaned_data.get("loanprinciple_amount")))
                                        if (loan_account.total_loan_balance) <\
                                                ((int(loan_account.loan_repayment_every) *
                                                    (principle_repayable))):
                                            loan_account.principle_repayment = (loan_account.total_loan_balance)
                                            loan_account.loan_repayment_amount = (
                                                (loan_account.total_loan_balance) + (loan_account.interest_charged))
                                        else:
                                            loan_account.principle_repayment = (
                                                (int(loan_account.loan_repayment_every) *
                                                    (principle_repayable)) + (balance_principle))
                                            loan_account.loan_repayment_amount = (
                                                (int(loan_account.loan_repayment_every) *
                                                    (principle_repayable)) +
                                                (loan_account.interest_charged) + (balance_principle))
                                return loan_account
        return loan_account

    def get_context_data(self, *args,  **kwargs):
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
                (form.cleaned_data.get("bookfee_amount", 0))

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
                        (form.cleaned_data.get("loanprocessingfee_amount"), 0)
            if self.group_loan_account.status == "Approved":
                if (self.group_loan_account.total_loan_balance)\
                   or (self.group_loan_account.interest_charged)\
                   or (self.group_loan_account.loan_repayment_amount)\
                   or (self.group_loan_account.principle_repayment):
                    self.var_demand_loanprinciple_amount_atinstant = \
                        (self.group_loan_account.principle_repayment)
                    self.var_demand_loaninterest_amount_atinstant = \
                        (self.group_loan_account.interest_charged)

        if form.savings_account:
            self.savings_account = form.savings_account
            if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                # personal
                self.savings_account.savings_balance += \
                    (form.cleaned_data.get("savingsdeposit_thrift_amount"))
                self.savings_account.total_deposits += \
                    (form.cleaned_data.get("savingsdeposit_thrift_amount"))

            if form.cleaned_data.get('recurring_deposit_account_no'):
                recurring_deposit_account = RecurringDeposits.objects.filter(
                    reccuring_deposit_number=form.cleaned_data.get('recurring_deposit_account_no')
                ).first()
                if recurring_deposit_account:
                    if form.cleaned_data.get('recurringdeposit_amount'):
                        if int(recurring_deposit_account.number_of_payments) <= int(recurring_deposit_account.recurring_deposit_period):
                            if d(recurring_deposit_account.recurring_deposit_amount) == d(form.cleaned_data.get('recurringdeposit_amount')):
                                self.savings_account.recurringdeposit_amount += \
                                    (form.cleaned_data.get('recurringdeposit_amount'))
                                recurring_deposit_account.number_of_payments += 1
                                if int(recurring_deposit_account.number_of_payments) == int(recurring_deposit_account.recurring_deposit_period):
                                    recurring_deposit_account.status = 'Paid'
                                recurring_deposit_account.save()
                                self.recurring_deposit_account = recurring_deposit_account

            if form.cleaned_data.get('fixed_deposit_account_no'):
                fixed_deposit_account = FixedDeposits.objects.filter(
                    fixed_deposit_number=form.cleaned_data.get('fixed_deposit_account_no')
                ).first()
                if fixed_deposit_account:
                    if form.cleaned_data.get('fixeddeposit_amount'):
                        if d(fixed_deposit_account.fixed_deposit_amount) == d(form.cleaned_data.get('fixeddeposit_amount')):
                            self.savings_account.fixeddeposit_amount += \
                                (form.cleaned_data.get('fixeddeposit_amount'))
                            fixed_deposit_account.status = 'Paid'
                            fixed_deposit_account.save()
                            self.fixed_deposit_account = fixed_deposit_account

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
                self.loan_account = self.loan_valid(form, self.loan_account)
            elif form.group_loan_account:
                self.group_loan_account = self.loan_valid(form, self.group_loan_account)

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
            if form.cleaned_data.get('fixed_deposit_account_no') and form.cleaned_data.get("fixeddeposit_amount"):
                receipt.fixed_deposit_account = FixedDeposits.objects.filter(
                    fixed_deposit_number=form.cleaned_data.get('fixed_deposit_account_no')).first()

            if form.cleaned_data.get("recurringdeposit_amount"):
                receipt.recurringdeposit_amount = form.cleaned_data.get("recurringdeposit_amount")
            if form.cleaned_data.get("recurringdeposit_amount") and form.cleaned_data.get('recurring_deposit_account_no'):
                receipt.recurring_deposit_account = RecurringDeposits.objects.filter(
                    reccuring_deposit_number=form.cleaned_data.get('recurring_deposit_account_no')).first()
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


class Receipts_Deposit_Old(LoginRequiredMixin, CreateView):
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

            if form.cleaned_data.get('recurring_deposit_account_no'):
                recurring_deposit_account_filter = RecurringDeposits.objects.filter(
                    reccuring_deposit_number=form.cleaned_data.get('recurring_deposit_account_no')
                )
                if recurring_deposit_account_filter:
                    recurring_deposit_account = recurring_deposit_account_filter.first()
                    if form.cleaned_data.get('recurringdeposit_amount'):
                        if int(recurring_deposit_account.number_of_payments) <= int(recurring_deposit_account.recurring_deposit_period):
                            if d(recurring_deposit_account.recurring_deposit_amount) == d(form.cleaned_data.get('recurringdeposit_amount')):
                                self.savings_account.recurringdeposit_amount += \
                                    (form.cleaned_data.get('recurringdeposit_amount'))
                                recurring_deposit_account.number_of_payments += 1
                                if int(recurring_deposit_account.number_of_payments) == int(recurring_deposit_account.recurring_deposit_period):
                                    recurring_deposit_account.status = 'Paid'
                                recurring_deposit_account.save()

            if form.cleaned_data.get('fixed_deposit_account_no'):
                fixed_deposit_account_filter = FixedDeposits.objects.filter(
                    fixed_deposit_number=form.cleaned_data.get('fixed_deposit_account_no')
                )
                if fixed_deposit_account_filter:
                    fixed_deposit_account = fixed_deposit_account_filter.first()
                    if form.cleaned_data.get('fixeddeposit_amount'):
                        if d(fixed_deposit_account.fixed_deposit_amount) == d(form.cleaned_data.get('fixeddeposit_amount')):
                            self.savings_account.fixeddeposit_amount += \
                                (form.cleaned_data.get('fixeddeposit_amount'))
                            fixed_deposit_account.status = 'Paid'
                            fixed_deposit_account.save()

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


class PaySlipCreateView(LoginRequiredMixin, CreateView):
    login_url = '/'
    redirect_field_name = 'next'
    model = Payments
    form_class = PaymentForm
    template_name = "core/paymentform.html"

    def get_context_data(self, **kwargs):
        context = super(PaySlipCreateView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['voucher_types'] = dict(PAYMENT_TYPES).keys()
        return context

    def get_form_kwargs(self):
        kwargs = super(PaySlipCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        pay_slip = form.save()
        data = {"error": False, 'pay_slip': pay_slip.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "errors": form.errors}
        return JsonResponse(data)


def get_group_loan_accounts(request):
    group_name = request.GET.get("group_name", None)
    group_account_number = request.GET.get('group_account_no', None)
    loan_accounts_data = {}
    if group_name and group_account_number:
        group_filter = Group.objects.filter(
            name__iexact=group_name,
            account_number=group_account_number)
        if group_filter:
            group = group_filter.first()
            loan_accounts = LoanAccount.objects.filter(group=group, status='Approved')
            if loan_accounts:
                for account in loan_accounts:
                    loan_accounts_data[account.id] = account.account_no
        else:
            return JsonResponse({"error": True,
                                 "data": dict(loan_accounts_data)})

    return JsonResponse({"error": False, "data": dict(loan_accounts_data)})


def get_member_loan_accounts(request):
    client_name = request.GET.get("client_name", None)
    client_account_number = request.GET.get('client_account_number', None)
    loan_accounts_data = {}
    if client_name and client_account_number:
        member_filter = Client.objects.filter(
            first_name__iexact=client_name,
            account_number=client_account_number)
        if member_filter:
            client = member_filter.first()
            loan_accounts = LoanAccount.objects.filter(client=client, status='Approved')
            if loan_accounts:
                for account in loan_accounts:
                    loan_accounts_data[account.id] = account.account_no
        else:
            return JsonResponse({"error": True,
                                 "data": dict(loan_accounts_data)})

    return JsonResponse({"error": False, "data": dict(loan_accounts_data)})


class ClientDepositAccountsView(LoginRequiredMixin, FormView):

    form_class = ClientDepositsAccountsForm

    def form_valid(self, form):
        if form.client:
            fixed_deposit_accounts = []
            recurring_deposit_accounts = []
            if form.pay_type == 'FixedWithdrawal':
                fixed_deposit_accounts = FixedDeposits.objects.filter(
                    client=form.client,
                    status='Paid'
                ).values_list("fixed_deposit_number", "fixed_deposit_amount")
            elif form.pay_type == 'RecurringWithdrawal':
                recurring_deposit_accounts_filter = RecurringDeposits.objects.filter(
                    client=form.client
                ).exclude(number_of_payments=0).exclude(status='Closed')
                recurring_deposit_accounts = \
                    recurring_deposit_accounts_filter.values_list(
                        "reccuring_deposit_number", "recurring_deposit_amount")
        else:
            fixed_deposit_accounts = []
            recurring_deposit_accounts = []
        data = {"error": False,
                "fixed_deposit_accounts": list(fixed_deposit_accounts),
                "recurring_deposit_accounts": list(recurring_deposit_accounts)}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)


class GetFixedDepositPaidAccountsView(LoginRequiredMixin, FormView):

    form_class = GetFixedDepositsPaidForm

    def form_valid(self, form):
        fixed_deposit = form.fixed_deposit_account
        interest_charged = (fixed_deposit.fixed_deposit_amount * (
            fixed_deposit.fixed_deposit_interest_rate / 12)) / 100
        fixed_deposit_interest_charged = interest_charged * d(
            fixed_deposit.fixed_deposit_period)
        total_amount = \
            fixed_deposit.fixed_deposit_amount + fixed_deposit_interest_charged
        data = {
            "error": False,
            "fixeddeposit_amount": fixed_deposit.fixed_deposit_amount or 0,
            "interest_charged": round(fixed_deposit_interest_charged, 6),
            'total_amount': round(total_amount, 6)
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)


class GetRecurringDepositPaidAccountsView(LoginRequiredMixin, FormView):

    form_class = GetRecurringDepositsPaidForm

    def form_valid(self, form):
        recurring_deposit = form.recurring_deposit_account
        recurring_deposit_amount = d(recurring_deposit.recurring_deposit_amount) * recurring_deposit.number_of_payments
        interest_charged = (recurring_deposit_amount * (
            recurring_deposit.recurring_deposit_interest_rate / 12)) / 100
        recurring_deposit_interest_charged = interest_charged * d(
            recurring_deposit.recurring_deposit_period)
        total_amount = \
            recurring_deposit_amount + recurring_deposit_interest_charged
        data = {
            "error": False,
            "recurringdeposit_amount": recurring_deposit_amount,
            "interest_charged": round(recurring_deposit_interest_charged, 6),
            'total_amount': round(total_amount, 6)
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True,
                "errors": form.errors}
        return JsonResponse(data)

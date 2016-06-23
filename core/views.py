import json
from decimal import Decimal
from django.shortcuts import HttpResponse
from django.views.generic.edit import CreateView
from .mixins import LoginRequiredMixin
from .forms import ReceiptForm
from micro_admin.models import(
    Branch,
    Receipts,
    SavingsAccount,
)
# Create your views here.


class Receipts_Deposit(LoginRequiredMixin, CreateView):
    template_name = "core/receiptsform.html"
    model = Receipts
    form_class = ReceiptForm

    def get_context_data(self, *args, **kwargs):
        context = super(Receipts_Deposit, self).get_context_data(*args, **kwargs)
        if self.request.method is "GET":
            context["branches"] = Branch.objects.all()
        return context

    def form_invalid(self, form):
        data = {"error": True,
                "message": form.errors}
        return HttpResponse(json.dumps(data))

    def form_valid(self, form):
        client = form.client
        if form.data.get("sharecapital_amount"):
            client.sharecapital_amount += \
                Decimal(form.data.get("sharecapital_amount", 0))
        if form.data.get("entrancefee_amount"):
            client.entrancefee_amount += \
                Decimal(form.data.get("entrancefee_amount", 0))
        if form.data.get("membershipfee_amount"):
            client.membershipfee_amount += \
                Decimal(form.data.get("membershipfee_amount", 0))
        if form.data.get("bookfee_amount"):
            client.bookfee_amount += Decimal(form.data.get("bookfee_amount", 0))
        # loan processing fee amount
        if form.loan_account:
            # personal
            loan_account = form.loan_account
            if form.data.get("loan_account_no"):
                loan_account.loanprocessingfee_amount += \
                    Decimal(form.data.get("loanprocessingfee_amount", 0))
            if loan_account.status == "Approved":
                if Decimal(loan_account.total_loan_balance)\
                   or Decimal(loan_account.interest_charged)\
                   or Decimal(loan_account.loan_repayment_amount)\
                   or Decimal(loan_account.principle_repayment):
                    var_demand_loanprinciple_amount_atinstant = \
                        Decimal(loan_account.principle_repayment)
                    var_demand_loaninterest_amount_atinstant = \
                        Decimal(loan_account.interest_charged)
                else:
                    var_demand_loanprinciple_amount_atinstant = 0
                    var_demand_loaninterest_amount_atinstant = 0
        if form.group_loan_account:
            # group
            if form.data.get("group_loan_account_no"):
                group_loan_account = form.group_loan_account
                group_loan_account.loanprocessingfee_amount += \
                    Decimal(form.data.get("loanprocessingfee_amount"))
        # savings deposit thrift amount
        if form.savings_account:
            self.savings_account = form.savings_account
            if form.data.get("savingsdeposit_thrift_amount"):
                # personal
                self.savings_account.savings_balance += \
                    Decimal(form.data.get("savingsdeposit_thrift_amount"))
                self.savings_account.total_deposits += \
                    Decimal(form.data.get("savingsdeposit_thrift_amount"))

            if form.data.get("recurringdeposit_amount"):
                self.savings_account.recurringdeposit_amount += \
                    Decimal(form.data.get("recurringdeposit_amount"))
        if form.group_savings_account:
            # group
            group_savings_account = form.group_savings_account
            group_savings_account.savings_balance += \
                Decimal(form.data.get("savingsdeposit_thrift_amount"))
            group_savings_account.total_deposits += \
                Decimal(form.data.get("savingsdeposit_thrift_amount"))

        if form.data.get("insurance_amount"):
            client.insurance_amount += Decimal(form.data.get("insurance_amount", 0))

        
        return HttpResponse(json.dumps({"error": False}))

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(Receipts_Deposit, self).post(request, *args, **kwargs)


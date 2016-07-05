from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from micro_admin.models import User, Group, Client, LoanAccount, Receipts
from django.views.generic import CreateView, DetailView, ListView, View
from micro_admin.forms import LoanAccountForm
import decimal
import datetime

d = decimal.Decimal


class ClientLoanApplicationView(LoginRequiredMixin, CreateView):
    model = LoanAccount
    form_class = LoanAccountForm
    template_name = "client/loan/application.html"

    def dispatch(self, request, *args, **kwargs):
        self.client = get_object_or_404(Client, id=self.kwargs.get('client_id'))
        return super(ClientLoanApplicationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientLoanApplicationView, self).get_context_data(**kwargs)
        count = LoanAccount.objects.all().count()
        account_no = "%s%s%d" % ("L", self.client.branch.id, count + 1)
        context["account_no"] = account_no
        context["client"] = self.client
        return context

    def form_valid(self, form):
        loan_account = form.save(commit=False)
        loan_account.status = "Applied"
        loan_account.created_by = User.objects.get(username=self.request.user)
        loan_account.client = self.client
        interest_charged = d(
            (
                d(loan_account.loan_amount) * (
                    d(loan_account.annual_interest_rate) / 12)
            ) / 100
        )
        loan_account.principle_repayment = d(
            int(loan_account.loan_repayment_every) * (
                d(loan_account.loan_amount) / d(
                    loan_account.loan_repayment_period)
            )
        )
        loan_account.interest_charged = d(
            int(loan_account.loan_repayment_every) * d(interest_charged))
        loan_account.loan_repayment_amount = d(
            d(loan_account.principle_repayment) + d(
                loan_account.interest_charged)
        )
        loan_account.total_loan_balance = d(d(loan_account.loan_amount))
        loan_account.save()
        return JsonResponse({"error": False, "loanaccount_id": loan_account.id})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class ClientLoansListView(LoginRequiredMixin, ListView):

    template_name = "client/loan/list_of_loan_accounts.html"
    context_object_name = "loan_accounts_list"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        queryset = LoanAccount.objects.filter(client=self.client)
        return queryset

    def get_context_data(self):
        context = super(ClientLoansListView, self).get_context_data()
        context["client"] = self.client
        return context


class ClientLoanAccount(LoginRequiredMixin, DetailView):
    model = LoanAccount
    pk = 'pk'
    template_name = "client/loan/account.html"


class ClientLoanDepositsListView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_lists"
    template_name = "client/loan/view_loan_deposits.html"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        self.loanaccount = get_object_or_404(LoanAccount, id=self.kwargs.get('loanaccount_id'))
        queryset = self.model.objects.filter(
            client=self.client,
            member_loan_account=self.loanaccount
        ).exclude(
            demand_loanprinciple_amount_atinstant=0,
            demand_loaninterest_amount_atinstant=0
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClientLoanDepositsListView, self).get_context_data(**kwargs)
        context["loanaccount"] = self.loanaccount
        return context


class GroupLoanApplicationView(LoginRequiredMixin, CreateView):
    model = LoanAccount
    form_class = LoanAccountForm
    template_name = "group/loan/application.html"

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        return super(GroupLoanApplicationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GroupLoanApplicationView, self).get_context_data(**kwargs)
        count = LoanAccount.objects.all().count()
        account_no = "%s%s%d" % ("L", self.group.branch.id, count + 1)
        context["account_no"] = account_no
        context["group"] = self.group
        return context

    def form_valid(self, form):
        loan_account = form.save(commit=False)
        loan_account.status = "Applied"
        loan_account.created_by = User.objects.get(username=self.request.user)
        loan_account.group = self.group

        interest_charged = d(
            (
                d(loan_account.loan_amount) * (
                    d(loan_account.annual_interest_rate) / 12)
            ) / 100
        )

        loan_account.principle_repayment = d(
            int(loan_account.loan_repayment_every) *
            (
                d(loan_account.loan_amount) / d(
                    loan_account.loan_repayment_period)
            )
        )
        loan_account.interest_charged = d(
            int(loan_account.loan_repayment_every) * d(interest_charged))
        loan_account.loan_repayment_amount = d(
            d(loan_account.principle_repayment) + d(
                loan_account.interest_charged)
        )
        loan_account.total_loan_balance = d(d(loan_account.loan_amount))
        loan_account.save()
        return JsonResponse({"error": False, "loanaccount_id": loan_account.id})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class GroupLoansListView(LoginRequiredMixin, ListView):

    template_name = "group/loan/list_of_loan_accounts.html"
    context_object_name = "loan_accounts_list"

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        queryset = LoanAccount.objects.filter(group=self.group)
        return queryset

    def get_context_data(self):
        context = super(GroupLoansListView, self).get_context_data()
        context["group"] = self.group
        return context


class GroupLoanAccount(LoginRequiredMixin, DetailView):
    model = LoanAccount
    pk = 'pk'
    context_object_name = "loan_account"
    template_name = "group/loan/account.html"

    def get_context_data(self, **kwargs):
        context = super(GroupLoanAccount, self).get_context_data(**kwargs)
        context['group'] = self.object.group
        return context


class GroupLoanDepositsListView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_list"
    template_name = "group/loan/list_of_loan_deposits.html"

    def get_queryset(self):
        self.loan_account = get_object_or_404(LoanAccount, id=self.kwargs.get('loanaccount_id'))
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        queryset = self.model.objects.filter(
            group=self.group,
            group_loan_account=self.loan_account
        ).exclude(
            demand_loanprinciple_amount_atinstant=0,
            demand_loaninterest_amount_atinstant=0
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupLoanDepositsListView, self).get_context_data(**kwargs)
        context["loan_account"] = self.loan_account
        context["group"] = self.group
        return context


class ChangeLoanAccountStatus(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(LoanAccount, id=kwargs.get("pk"))
        if self.object.group:
            branch_id = self.object.group.branch.id
        elif self.object.client:
            branch_id = self.object.client.branch.id
        else:
            branch_id = None
        if branch_id:
            if (request.user.is_admin or
                (request.user.has_perm("branch_manager") and
                 request.user.branch.id == branch_id)):
                status = request.GET.get("status")
                if status in ['Closed', 'Withdrawn', 'Rejected', 'Approved']:
                    self.object.status = request.GET.get("status")
                    self.object.approved_date = datetime.datetime.now()
                    self.object.save()
                    data = {"error": False}
                else:
                    data = {"error": True, "error_message": "Status is not in available choices"}
            else:
                data = {
                    "error": True, "error_message": "You don't have permission to change the status.",
                }
        else:
            data = {"error": True, "error_message": "Branch Id not Found"}

        data["success_url"] = reverse('loans:clientloanaccount', kwargs={"pk": self.object.id})
        return JsonResponse(data)


class IssueLoan(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        loan_account = get_object_or_404(LoanAccount, id=kwargs.get("loanaccount_id"))
        if loan_account.group or loan_account.client:
            loan_account.loan_issued_date = datetime.datetime.now()
            loan_account.loan_issued_by = self.request.user
            loan_account.save()

        if loan_account.group:
            url = reverse("loans:grouploanaccount", kwargs={"pk": loan_account.id})
        elif loan_account.client:
            url = reverse("loans:clientloanaccount", kwargs={'pk': loan_account.id})
        else:
            url = "/"
        return HttpResponseRedirect(url)

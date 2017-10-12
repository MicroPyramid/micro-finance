from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, render
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from micro_admin.models import Group, Client, SavingsAccount, Receipts, Payments
from micro_admin.forms import SavingsAccountForm
from django.db.models import Sum
from core.utils import unique_random_number
import decimal
import datetime

d = decimal.Decimal


# Client Savings
def client_savings_application_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    form = SavingsAccountForm()
    if SavingsAccount.objects.filter(client=client).exists():
        return HttpResponseRedirect(reverse(request, "savings:clientsavingsaccount", {'client_id': client.id}))
    if request.method == 'POST':
        form = SavingsAccountForm(request.POST)
        if form.is_valid():
            obj_sav_acc = form.save(commit=False)
            obj_sav_acc.status = "Applied"
            obj_sav_acc.created_by = request.user
            obj_sav_acc.client = client
            obj_sav_acc.save()
            return JsonResponse({"error": False, "client_id": client.id})
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    else:
        account_no = unique_random_number(SavingsAccount)
        return render(request, "client/savings/application.html", {'client': client, 'account_no': account_no})


def client_savings_accountview(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    account_object = get_object_or_404(SavingsAccount, client=client)
    return render(request, "client/savings/account.html", {'client': client, 'account_object': account_object})


class ClientSavingsDepositsListView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_lists"
    template_name = "client/savings/list_of_savings_deposits.html"

    def get_queryset(self):
        queryset = self.model.objects.filter(
            client=self.kwargs.get('client_id')
        ).exclude(savingsdeposit_thrift_amount=0)
        return queryset

    def get_context_data(self):
        context = super(ClientSavingsDepositsListView, self).get_context_data()
        context["savingsaccount"] = get_object_or_404(SavingsAccount, client=self.kwargs.get("client_id"))
        return context


class ClientSavingsWithdrawalsListView(LoginRequiredMixin, ListView):
    model = Payments
    context_object_name = "savings_withdrawals_list"
    template_name = "client/savings/list_of_savings_withdrawals.html"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        queryset = self.model.objects.filter(
            client=self.client,
            payment_type="SavingsWithdrawal"
        )
        return queryset

    def get_context_data(self):
        context = super(ClientSavingsWithdrawalsListView, self).get_context_data()
        context['client'] = self.client
        return context


# Group Savings
class GroupSavingsApplicationView(LoginRequiredMixin, CreateView):
    model = SavingsAccount
    form_class = SavingsAccountForm
    template_name = "group/savings/application.html"

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        if SavingsAccount.objects.filter(group=self.group).exists():
            return HttpResponseRedirect(
                reverse("savings:groupsavingsaccount",
                        kwargs={'group_id': self.group.id})
            )
        return super(GroupSavingsApplicationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GroupSavingsApplicationView, self).get_context_data(**kwargs)
        context["group"] = self.group
        context["account_no"] = unique_random_number(SavingsAccount)
        return context

    def form_valid(self, form):
        obj_sav_acc = form.save(commit=False)
        obj_sav_acc.status = "Applied"
        obj_sav_acc.created_by = self.request.user
        obj_sav_acc.group = self.group
        obj_sav_acc.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse("savings:groupsavingsaccount",
                                   kwargs={'group_id': self.group.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class GroupSavingsAccountView(LoginRequiredMixin, DetailView):
    model = SavingsAccount
    context_object_name = "savings_account"
    pk_url_kwarg = "group_id"
    template_name = "group/savings/account.html"

    def get_object(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        self.object = get_object_or_404(SavingsAccount, group=self.group)
        return self.object

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context["group"] = self.group
        context["totals"] = self.group.clients.all().aggregate(
            sharecapital_amount=Sum('sharecapital_amount'),
            entrancefee_amount=Sum('entrancefee_amount'),
            membershipfee_amount=Sum('membershipfee_amount'),
            bookfee_amount=Sum('bookfee_amount'),
            insurance_amount=Sum('insurance_amount'),
        )
        return self.render_to_response(context)


class GroupSavingsDepositsListView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_list"
    template_name = "group/savings/list_of_savings_deposits.html"

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        self.savings_account = get_object_or_404(SavingsAccount, group=self.group)
        queryset = self.model.objects.filter(
            group=self.group
        ).exclude(
            savingsdeposit_thrift_amount=0
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupSavingsDepositsListView, self).get_context_data(**kwargs)
        context["savings_account"] = self.savings_account
        context["group"] = self.group
        return context


class GroupSavingsWithdrawalsListView(LoginRequiredMixin, ListView):
    model = Payments
    context_object_name = "savings_withdrawals_list"
    template_name = "group/savings/list_of_savings_withdrawals.html"

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        queryset = self.model.objects.filter(
            group=self.group,
            payment_type="SavingsWithdrawal"
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupSavingsWithdrawalsListView, self).get_context_data(**kwargs)
        context["group"] = self.group
        return context


# Change Group/Client Savings account status
class ChangeSavingsAccountStatus(LoginRequiredMixin, UpdateView):
    model = SavingsAccount
    pk_url_kwarg = "savingsaccount_id"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        group = self.object.group
        client = self.object.client
        if group:
            branch_id = group.branch.id
        elif client:
            branch_id = client.branch.id
        else:
            branch_id = None
        if branch_id:
            if (
                request.user.is_admin or
                (request.user.has_perm("branch_manager") and request.user.branch.id == branch_id)
            ):
                if request.POST.get("status") in ['Closed', 'Withdrawn', 'Rejected', 'Approved']:
                    self.object.status = request.POST.get("status")
                    self.object.approved_date = datetime.datetime.now()
                    self.object.save()
                    data = {"error": False}
                else:
                    data = {"error": True,
                            "error_message": "Invalid status. Selected status is not in available choices."}
            else:
                data = {
                    "error": True,
                    "error_message": "You don't have permission to change the status.",
                }
        else:
            data = {"error": True, "error_message": "Branch ID not Found"}
        return JsonResponse(data)

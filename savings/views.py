from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DetailView
from micro_admin.models import Group, Client, SavingsAccount
from micro_admin.forms import SavingsAccountForm
from django.db.models import Sum
import decimal
import datetime

d = decimal.Decimal


class ClientSavingsApplicationView(LoginRequiredMixin, CreateView):
    model = SavingsAccount
    form_class = SavingsAccountForm
    template_name = "client/savings/application.html"

    def dispatch(self, request, *args, **kwargs):
        self.client = get_object_or_404(
            Client, id=self.kwargs.get('client_id'))
        if SavingsAccount.objects.filter(client=self.client).exists():
            return HttpResponseRedirect(
                reverse("savings:clientsavingsaccount", kwargs={
                    'client_id': self.client.id}))

        return super(ClientSavingsApplicationView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            ClientSavingsApplicationView, self).get_context_data(**kwargs)
        count = SavingsAccount.objects.all().count()
        context["client"] = self.client
        context["account_no"] = "%s%s%d" % (
            "S", self.client.branch.id, count + 1)
        return context

    def form_valid(self, form):
        obj_sav_acc = form.save(commit=False)
        obj_sav_acc.status = "Applied"
        obj_sav_acc.created_by = self.request.user
        obj_sav_acc.client = self.client
        obj_sav_acc.save()
        return JsonResponse(
            {"error": False, "client_id": self.client.id})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class ClientSavingsAccountView(LoginRequiredMixin, DetailView):
    model = SavingsAccount
    context_object_name = "savingsaccount"
    template_name = "client/savings/account.html"

    def get_object(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        self.object = get_object_or_404(SavingsAccount, client=self.client)
        return self.object

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context["client"] = self.client
        return self.render_to_response(context)


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
        count = SavingsAccount.objects.all().count()
        context["group"] = self.group
        context["account_no"] = "%s%s%d" % ("S", self.group.branch.id, count + 1)
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

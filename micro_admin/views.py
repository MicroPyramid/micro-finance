import json
import datetime
import decimal
# import csv

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
# from django.views.generic.detail import BaseDetailView
from django.contrib.auth.decorators import login_required
# from django.utils.encoding import smart_str
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, View
from django.views.generic import ListView, DetailView, RedirectView, FormView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Sum
# import xlwt
# from xhtml2pdf import pisa
# from django.template.loader import get_template
# import cStringIO as StringIO
# from weasyprint import HTML

from micro_admin.models import (
    User, Branch, Group, Client, CLIENT_ROLES, GroupMeetings, SavingsAccount,
    LoanAccount, Receipts, FixedDeposits, PAYMENT_TYPES, Payments,
    RecurringDeposits, USER_ROLES)
from micro_admin.forms import (
    BranchForm, UserForm, GroupForm, ClientForm, AddMemberForm,
    ReceiptForm, FixedDepositForm, PaymentForm,
    ReccuringDepositForm, ChangePasswordForm, GroupMeetingsForm)
from micro_admin.mixins import BranchAccessRequiredMixin, BranchManagerRequiredMixin

d = decimal.Decimal


class IndexView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return render(request, "index.html", {"user": request.user})
        return render(request, "login.html")


class LoginView(View):

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                data = {"error": False, "errors": "Loggedin Successfully"}
            else:
                data = {"error": True, "errors": "User is not active."}
        else:
            data = {"error": True, "errors": "Username and Password were incorrect."}
        return JsonResponse(data)

    def get(self, request):
        if request.user.is_authenticated():
            return render(request, 'index.html', {'user': request.user})
        return render(request, "login.html")


class LogoutView(RedirectView):
    pattern_name = "micro_admin:login"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


# --------------------------------------------------- #
# Branch Model class Based View #
class CreateBranchView(LoginRequiredMixin, CreateView):
    form_class = BranchForm
    template_name = "branch/create.html"

    def form_valid(self, form):
        branch = form.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:branchprofile', kwargs={"pk": branch.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class UpdateBranchView(LoginRequiredMixin, UpdateView):
    pk = 'pk'
    model = Branch
    form_class = BranchForm
    template_name = "branch/edit.html"

    def form_valid(self, form):
        branch = form.save()
        return JsonResponse({
            "error": False, "success_url": reverse('micro_admin:branchprofile', kwargs={"pk": branch.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class BranchProfileView(LoginRequiredMixin, DetailView):
    model = Branch
    pk = 'pk'
    template_name = "branch/view.html"


class BranchListView(LoginRequiredMixin, ListView):
    model = Branch
    template_name = "branch/list.html"


class BranchInactiveView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.is_admin:
            branch = get_object_or_404(Branch, id=kwargs.get('pk'))
            if branch.is_active:
                branch.is_active = False
                branch.save()
        return HttpResponseRedirect(reverse('micro_admin:viewbranch'))
# --------------------------------------------------- #


# --------------------------------------------------- #
# Clinet model views
class CreateClientView(LoginRequiredMixin, CreateView):
    form_class = ClientForm
    template_name = "client/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateClientView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['client_roles'] = dict(CLIENT_ROLES).keys()
        return context

    def form_valid(self, form):
        client = form.save(commit=False)
        client.created_by = self.request.user
        client.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:clientprofile', kwargs={"pk": client.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class ClienProfileView(LoginRequiredMixin, DetailView):
    pk = 'pk'
    model = Client
    template_name = "client/profile.html"


class UpdateClientView(LoginRequiredMixin, UpdateView):
    pk = 'pk'
    model = Client
    form_class = ClientForm
    template_name = "client/edit.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateClientView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['client_roles'] = dict(CLIENT_ROLES).keys()
        return context

    def form_valid(self, form):
        # if not (request.user.is_admin or request.user.branch == client.branch):
        #     return HttpResponseRedirect(reverse('micro_admin:viewclient'))
        client = form.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:clientprofile', kwargs={"pk": client.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


@login_required
def update_clientprofile(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if not (request.user.is_admin or request.user.branch == client.branch):
        return HttpResponseRedirect(
            reverse('micro_admin:clientprofile', kwargs={
                    'client_id': client_id}))

    if request.method == "GET":
        return render(request, "client/update-profile.html", {"client": client})
    else:
        if (
            request.FILES and request.FILES.get("photo") and
            request.FILES.get("signature")
        ):
            client.photo = request.FILES.get("photo")
            client.signature = request.FILES.get("signature")
            client.save()
        return HttpResponseRedirect(reverse('micro_admin:clientprofile', kwargs={'client_id': client_id}))


class ClientsListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "client/list.html"


class ClientInactiveView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        client = get_object_or_404(Client, id=kwargs.get('client_id'))
        if (
            request.user.is_admin or (
                request.user.has_perm("branch_manager") and
                request.user.branch == client.branch
            )
        ):
            if client.is_active:
                client.is_active = False
                client.save()
        return HttpResponseRedirect(reverse("micro_admin:viewclient"))


# ------------------------------------------- #
# User Model views
class CreateUserView(LoginRequiredMixin, CreateView):
    form_class = UserForm
    template_name = "user/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateUserView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['userroles'] = dict(USER_ROLES).keys()
        return context

    def form_valid(self, form):
        user = form.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:userprofile', kwargs={"pk": user.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class UpdateUserView(LoginRequiredMixin, UpdateView):
    pk_url_kwarg = 'pk'
    model = User
    form_class = UserForm
    context_object_name = 'selecteduser'
    template_name = "user/edit.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data(**kwargs)
        context['branch'] = Branch.objects.all()
        context['userroles'] = dict(USER_ROLES).keys()
        return context

    def form_valid(self, form):
        user = form.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:userprofile', kwargs={"pk": user.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class UserProfileView(LoginRequiredMixin, DetailView):
    pk = 'pk'
    model = User
    context_object_name = 'selecteduser'
    template_name = "user/profile.html"


class UsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "user/list.html"
    context_object_name = 'list_of_users'

    def get_queryset(self):
        return User.objects.filter(is_admin=0)


class UserInactiveView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('pk'))
        if (
            request.user.is_admin or
            (request.user.has_perm("branch_manager") and
             request.user.branch == user.branch)
        ):
            if request.user == user or not user.is_active:
                pass
            else:
                user.is_active = False
                user.save()
        return HttpResponseRedirect(reverse('micro_admin:userslist'))
# ------------------------------------------------- #


class CreateGroupView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "group/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateGroupView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context

    def form_valid(self, form):
        group = form.save(commit=False)
        group.created_by = self.request.user
        group.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:groupprofile', kwargs={"group_id": group.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class GroupProfileView(LoginRequiredMixin, DetailView):
    pk_url_kwarg = 'group_id'
    model = Group
    context_object_name = 'group'
    template_name = "group/profile.html"

    def get_context_data(self, **kwargs):
        context = super(GroupProfileView, self).get_context_data(**kwargs)
        clients_list = self.object.clients.all()
        group_mettings = GroupMeetings.objects.filter(group_id=self.object.id).order_by('-id')

        context["clients_list"] = clients_list
        context["clients_count"] = len(clients_list)
        context["latest_group_meeting"] = group_mettings.first() if group_mettings else None
        return context


class GroupAssignStaffView(LoginRequiredMixin, BranchAccessRequiredMixin, DetailView):
    model = Group
    pk_url_kwarg = 'group_id'
    context_object_name = 'group'
    template_name = "group/assign_staff.html"

    def get_context_data(self, **kwargs):
        context = super(GroupAssignStaffView, self).get_context_data(**kwargs)
        context["users_list"] = User.objects.filter(is_admin=0)
        return context

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        if request.POST.get("staff"):
            group.staff = get_object_or_404(User, id=request.POST.get("staff"))
            group.save()
            data = {
                "error": False,
                "success_url": reverse('micro_admin:groupprofile', kwargs={"group_id": group.id})
            }
        else:
            data = {"error": True, "message": {"staff": "This field is required"}}
        return JsonResponse(data)


class GroupAddMembersView(LoginRequiredMixin, BranchAccessRequiredMixin, UpdateView):
    model = Group
    pk_url_kwarg = 'group_id'
    context_object_name = 'group'
    form_class = AddMemberForm
    template_name = "group/add_member.html"

    def get_context_data(self, **kwargs):
        context = super(GroupAddMembersView, self).get_context_data(**kwargs)
        context["clients_list"] = Client.objects.filter(status="UnAssigned", is_active=1)
        return context

    def form_valid(self, form):
        group = self.object
        client_ids = self.request.POST.getlist("clients")
        for client_id in client_ids:
            try:
                client = Client.objects.get(id=client_id, status="UnAssigned", is_active=1)
            except Client.DoesNotExist:
                continue
            else:
                group.clients.add(client)
                group.save()
                client.status = "Assigned"
                client.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:groupprofile', kwargs={"group_id": group.id})
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class GroupMembersListView(LoginRequiredMixin, ListView):
    template_name = "group/view-members.html"
    context_object_name = 'clients_list'

    def get_context_data(self, **kwargs):
        context = super(GroupMembersListView, self).get_context_data(**kwargs)
        context["group"] = self.group
        return context

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        return self.group.clients.all()


class GroupsListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = "group/list.html"
    context_object_name = 'groups_list'

    def get_queryset(self):
        query_set = super(GroupsListView, self).get_queryset()
        return query_set.select_related("staff", "branch").prefetch_related("clients")


class GroupInactiveView(LoginRequiredMixin, BranchManagerRequiredMixin, UpdateView):
    model = Group
    pk_url_kwarg = 'group_id'

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            group = self.get_object()
        else:
            group = self.object

        if (
            LoanAccount.objects.filter(
                group=group, status="Approved"
            ).exclude(
                total_loan_balance=0
            ).count() or not group.is_active
        ):
            # TODO: Add message saying that, this group
            # has pending loans or already in-active.
            pass
        else:
            group.is_active = False
            group.save()
        return HttpResponseRedirect(reverse('micro_admin:groupslist'))


class GroupRemoveMembersView(LoginRequiredMixin, BranchManagerRequiredMixin, UpdateView):
    model = Group
    pk_url_kwarg = 'group_id'
    context_object_name = 'group'

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            group = self.get_object()
        else:
            group = self.object

        client = get_object_or_404(Client, id=self.kwargs.get('client_id'))
        group.clients.remove(client)
        client.status = "UnAssigned"
        client.save()
        return HttpResponseRedirect(reverse('micro_admin:groupprofile', kwargs={'group_id': group.id}))


class GroupMeetingsListView(LoginRequiredMixin, ListView):
    model = GroupMeetings
    template_name = "group/meetings/list.html"
    context_object_name = 'group_meetings'

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        query_set = super(GroupMeetingsListView, self).get_queryset()
        return query_set.filter(group=self.group).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(GroupMeetingsListView, self).get_context_data(**kwargs)
        context["group"] = self.group
        return context


class GroupMeetingsAddView(LoginRequiredMixin, CreateView):
    model = GroupMeetings
    form_class = GroupMeetingsForm
    template_name = "group/meetings/add.html"

    def get_context_data(self, **kwargs):
        context = super(GroupMeetingsAddView, self).get_context_data(**kwargs)
        context["group"] = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        return context

    def form_valid(self, form):
        group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        meeting = form.save(commit=False)
        meeting.group = group
        meeting.save()
        return JsonResponse({"error": False, "group_id": group.id})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


@login_required
def receipts_deposit(request):
    if request.method == "GET":
        branches = Branch.objects.all()
        return render(request, "receiptsform.html", {"branches": branches})
    elif request.method == "POST":
        receipt_form = ReceiptForm(request.POST)
        if receipt_form.is_valid():
            datestring_format = datetime.datetime.strptime(request.POST.get("date"), "%m/%d/%Y").strftime("%Y-%m-%d")
            dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            date = dateconvert
            branch = Branch.objects.get(id=request.POST.get("branch"))
            receipt_number = request.POST.get("receipt_number")
            name = request.POST.get("name")
            account_number = request.POST.get("account_number")
            staff = request.user
            try:
                client = Client.objects.get(first_name__iexact=name, account_number=account_number)
                if request.POST.get("sharecapital_amount"):
                    client.sharecapital_amount += d(request.POST.get("sharecapital_amount"))
                if request.POST.get("entrancefee_amount"):
                    client.entrancefee_amount += d(request.POST.get("entrancefee_amount"))
                if request.POST.get("membershipfee_amount"):
                    client.membershipfee_amount += d(request.POST.get("membershipfee_amount"))
                if request.POST.get("bookfee_amount"):
                    client.bookfee_amount += d(request.POST.get("bookfee_amount"))
                if request.POST.get("loanprocessingfee_amount"):
                    if request.POST.get("loan_account_no"):
                        try:
                            loan_account = LoanAccount.objects.get(client=client, account_no=request.POST.get("loan_account_no"))
                            loan_account.loanprocessingfee_amount += d(request.POST.get("loanprocessingfee_amount"))
                            try:
                                client_group = client.group_set.get()
                                if request.POST.get("group_name") and request.POST.get("group_account_number"):
                                    try:
                                        group = Group.objects.get(name__iexact=request.POST.get("group_name"), account_number=request.POST.get("group_account_number"))
                                        if request.POST.get("group_name").lower() == client_group.name.lower() and int(request.POST.get("group_account_number")) == int(client_group.account_number):
                                            if request.POST.get("group_loan_account_no"):
                                                try:
                                                    group_loan_account = LoanAccount.objects.get(group=group, account_no=request.POST.get("group_loan_account_no"))
                                                    group_loan_account.loanprocessingfee_amount += d(request.POST.get("loanprocessingfee_amount"))
                                                except LoanAccount.DoesNotExist:
                                                    data = {"error": True, "message1": "Loan does not exists with this Loan Account Number for this Group."}
                                                    return HttpResponse(json.dumps(data))
                                            else:
                                                data = {"error": True, "message1": "Please enter the group loan account number."}
                                                return HttpResponse(json.dumps(data))
                                        else:
                                            data = {"error": True, "message1": "Member does not belong to this group."}
                                            return HttpResponse(json.dumps(data))
                                    except Group.DoesNotExist:
                                        data = {"error": True, "message1": "No Group exists with this name."}
                                        return HttpResponse(json.dumps(data))
                                else:
                                    data = {"error": True, "message1": "Please enter the Group Name and Account Number."}
                                    return HttpResponse(json.dumps(data))
                            except ObjectDoesNotExist:
                                data = {"error": True, "message1": "Member has not been assigned to any group."}
                                return HttpResponse(json.dumps(data))
                        except LoanAccount.DoesNotExist:
                            data = {"error": True, "message1": "Loan does not exists with this Loan Account Number for this Member."}
                            return HttpResponse(json.dumps(data))
                    else:
                        data = {"error": True, "message1": "Please enter the Member Loan Account Number to pay the Loan processing fee."}
                        return HttpResponse(json.dumps(data))

                if request.POST.get("savingsdeposit_thrift_amount"):
                    try:
                        savings_account = SavingsAccount.objects.get(client=client)
                        savings_account.savings_balance += d(request.POST.get("savingsdeposit_thrift_amount"))
                        savings_account.total_deposits += d(request.POST.get("savingsdeposit_thrift_amount"))

                        try:
                            client_group = client.group_set.get()
                            if request.POST.get("group_name") and request.POST.get("group_account_number"):
                                try:
                                    group = Group.objects.get(name__iexact=request.POST.get("group_name"), account_number=request.POST.get("group_account_number"))
                                    if request.POST.get("group_name").lower() == client_group.name.lower() and int(request.POST.get("group_account_number")) == int(client_group.account_number):
                                        try:
                                            group_savings_account = SavingsAccount.objects.get(group=client_group)
                                            group_savings_account.savings_balance += d(request.POST.get("savingsdeposit_thrift_amount"))
                                            group_savings_account.total_deposits += d(request.POST.get("savingsdeposit_thrift_amount"))
                                        except SavingsAccount.DoesNotExist:
                                            data = {"error": True, "message1": "Group does not have savings account to make thrift deposit."}
                                            return HttpResponse(json.dumps(data))
                                    else:
                                        data = {"error": True, "message1": "Member does not belong to this Group.Please check Group Name and Account Number."}
                                        return HttpResponse(json.dumps(data))
                                except Group.DoesNotExist:
                                    data = {"error": True, "message1": "No Group exists with this Name and Account Number."}
                                    return HttpResponse(json.dumps(data))
                            else:
                                data = {"error": True, "message1": "Please enter Group Name and Account Number."}
                                return HttpResponse(json.dumps(data))
                        except ObjectDoesNotExist:
                            pass

                    except SavingsAccount.DoesNotExist:
                        data = {"error": True, "message1": "Member does not have savings account to make thrift deposit."}
                        return HttpResponse(json.dumps(data))

                if request.POST.get("recurringdeposit_amount"):
                    try:
                        savings_account = SavingsAccount.objects.get(client=client)
                        savings_account.recurringdeposit_amount += d(request.POST.get("recurringdeposit_amount"))
                    except SavingsAccount.DoesNotExist:
                        data = {"error": True, "message1": "Member does not have savings account."}
                        return HttpResponse(json.dumps(data))
                if request.POST.get("insurance_amount"):
                    client.insurance_amount += d(request.POST.get("insurance_amount"))

                try:
                    loan_account = LoanAccount.objects.get(client=client, account_no=request.POST.get("loan_account_no"))
                    if loan_account.status == "Approved":
                        if d(loan_account.total_loan_balance) or d(loan_account.interest_charged) or d(loan_account.loan_repayment_amount) or d(loan_account.principle_repayment) :
                            var_demand_loanprinciple_amount_atinstant = d(loan_account.principle_repayment)
                            var_demand_loaninterest_amount_atinstant = d(loan_account.interest_charged)
                        else:
                            var_demand_loanprinciple_amount_atinstant = 0
                            var_demand_loaninterest_amount_atinstant = 0
                except LoanAccount.DoesNotExist:
                    pass

                if d(request.POST.get("loaninterest_amount")) != int(0):
                    if request.POST.get("loan_account_no"):
                        try:
                            loan_account = LoanAccount.objects.get(client=client, account_no=request.POST.get("loan_account_no"))
                            if request.POST.get("group_loan_account_no"):
                                try:
                                    client_group = client.group_set.get()
                                    if request.POST.get("group_name") and request.POST.get("group_account_number"):
                                        try:
                                            group = Group.objects.get(name__iexact=request.POST.get("group_name"), account_number=request.POST.get("group_account_number"))
                                            if request.POST.get("group_name").lower() == client_group.name.lower() and int(request.POST.get("group_account_number")) == int(client_group.account_number):
                                                try:
                                                    group_loan_account = LoanAccount.objects.get(group=group, account_no=request.POST.get("group_loan_account_no"))
                                                except LoanAccount.DoesNotExist:
                                                    data = {"error": True, "message1": "Group does not have any Loan to pay the Loan interest amount."}
                                                    return HttpResponse(json.dumps(data))
                                            else:
                                                data = {"error": True, "message1": "Member does not belong to this Group.Please check Group Name and Account Number."}
                                                return HttpResponse(json.dumps(data))
                                        except Group.DoesNotExist:
                                            data = {"error": True, "message1": "No Group exists with this Name and Account Number."}
                                            return HttpResponse(json.dumps(data))
                                    else:
                                        data = {"error": True, "message1": "Please enter Group Name and Account Number."}
                                        return HttpResponse(json.dumps(data))
                                except ObjectDoesNotExist:
                                    data = {"error": True, "message1": "Member has not been assigned to any group."}
                                    return HttpResponse(json.dumps(data))
                            else:
                                data = {"error": True, "message1": "Please enter the the Group Loan A/C Number."}
                                return HttpResponse(json.dumps(data))
                        except LoanAccount.DoesNotExist:
                            data = {"error": True, "message1": "Member does not have any Loan to pay the Loan interest amount."}
                            return HttpResponse(json.dumps(data))
                    else:
                        data = {"error": True, "message1": "Please enter the the Member Loan A/C Number."}
                        return HttpResponse(json.dumps(data))
                else:
                    pass

                if request.POST.get("loanprinciple_amount") or d(request.POST.get("loaninterest_amount")) != int(0) :
                    if request.POST.get("loan_account_no") :
                        try:
                            loan_account = LoanAccount.objects.get(client=client, account_no=request.POST.get("loan_account_no"))
                            try:
                                client_group = client.group_set.get()
                                if request.POST.get("group_name") and request.POST.get("group_account_number"):
                                    try:
                                        group = Group.objects.get(name__iexact=request.POST.get("group_name"), account_number=request.POST.get("group_account_number"))
                                        if request.POST.get("group_name").lower() == client_group.name.lower() and int(request.POST.get("group_account_number")) == int(client_group.account_number):
                                            if request.POST.get("group_loan_account_no") :
                                                try:
                                                    group_loan_account = LoanAccount.objects.get(group=group, account_no=request.POST.get("group_loan_account_no"))
                                                    if loan_account.status == "Approved" and group_loan_account.status == "Approved" :
                                                        if group_loan_account.loan_issued_date:
                                                            if d(loan_account.total_loan_balance) or d(loan_account.interest_charged) or d(loan_account.loan_repayment_amount) or d(loan_account.principle_repayment) :
                                                                if d(request.POST.get("loanprinciple_amount")) <= d(loan_account.total_loan_balance) :
                                                                    if d(request.POST.get("loaninterest_amount")) > d(loan_account.interest_charged) :
                                                                        data = {"error": True, "message1": "Entered interest amount is greater than interest charged."}
                                                                        return HttpResponse(json.dumps(data))
                                                                    elif d(request.POST.get("loaninterest_amount")) > d(loan_account.loan_amount) or d(request.POST.get("loanprinciple_amount")) > d(loan_account.loan_amount) :
                                                                        data = {"error": True, "message1": "Amount is greater than issued loan amount. Transaction can't be done."}
                                                                        return HttpResponse(json.dumps(data))
                                                                    else:
                                                                        loan_account.total_loan_amount_repaid += d(request.POST.get("loanprinciple_amount"))
                                                                        loan_account.total_interest_repaid += d(request.POST.get("loaninterest_amount"))
                                                                        loan_account.total_loan_paid = d(d(loan_account.total_loan_amount_repaid) + d(loan_account.total_interest_repaid))
                                                                        loan_account.total_loan_balance -= d(request.POST.get("loanprinciple_amount"))
                                                                        loan_account.no_of_repayments_completed += loan_account.loan_repayment_every


                                                                        group_loan_account.total_loan_amount_repaid += d(request.POST.get("loanprinciple_amount"))
                                                                        group_loan_account.total_interest_repaid += d(request.POST.get("loaninterest_amount"))
                                                                        group_loan_account.total_loan_paid = d(d(group_loan_account.total_loan_amount_repaid) + d(group_loan_account.total_interest_repaid))
                                                                        group_loan_account.total_loan_balance -= d(request.POST.get("loanprinciple_amount"))

                                                                        if d(loan_account.total_loan_amount_repaid) == d(loan_account.loan_amount) and d(loan_account.total_loan_balance) == d(0):
                                                                            if d(request.POST.get("loanprinciple_amount")) > d(loan_account.principle_repayment) :
                                                                                data = {"error": True, "message1": "Amount is greater than issued loan amount. Transaction can't be done."}
                                                                                return HttpResponse(json.dumps(data))
                                                                            else:
                                                                                loan_account.save()
                                                                                group_loan_account.save()
                                                                                if d(request.POST.get("loaninterest_amount")) == d(loan_account.interest_charged) :
                                                                                    if d(request.POST.get("loanprinciple_amount")) == d(loan_account.principle_repayment) :
                                                                                        loan_account.loan_repayment_amount = 0
                                                                                        loan_account.principle_repayment = 0
                                                                                        loan_account.interest_charged = 0
                                                                                    elif d(request.POST.get("loanprinciple_amount")) < d(loan_account.principle_repayment) :
                                                                                        balance_principle = d(loan_account.principle_repayment) - d(request.POST.get("loanprinciple_amount"))
                                                                                        loan_account.principle_repayment = d(balance_principle)
                                                                                        loan_account.loan_repayment_amount = d(balance_principle)
                                                                                        loan_account.interest_charged = 0
                                                                                else:
                                                                                    if d(request.POST.get("loaninterest_amount")) < d(loan_account.interest_charged) :
                                                                                        if d(request.POST.get("loanprinciple_amount")) == d(loan_account.principle_repayment) :
                                                                                            balance_interest = d(loan_account.interest_charged) - d(request.POST.get("loaninterest_amount"))
                                                                                            loan_account.interest_charged = d(balance_interest)
                                                                                            loan_account.loan_repayment_amount = d(balance_interest)
                                                                                            loan_account.principle_repayment = 0
                                                                                        elif d(request.POST.get("loanprinciple_amount")) < d(loan_account.principle_repayment) :
                                                                                            balance_principle = d(loan_account.principle_repayment) - d(request.POST.get("loanprinciple_amount"))
                                                                                            loan_account.principle_repayment = d(balance_principle)
                                                                                            balance_interest = d(loan_account.interest_charged) - d(request.POST.get("loaninterest_amount"))
                                                                                            loan_account.interest_charged = d(balance_interest)
                                                                                            loan_account.loan_repayment_amount = d(d(balance_principle) + d(balance_interest))

                                                                        elif d(loan_account.total_loan_amount_repaid) < d(loan_account.loan_amount) and d(loan_account.total_loan_balance) :
                                                                            loan_account.save()
                                                                            group_loan_account.save()
                                                                            if int(loan_account.no_of_repayments_completed) >= int(loan_account.loan_repayment_period) :
                                                                                if d(request.POST.get("loaninterest_amount")) == d(loan_account.interest_charged) :
                                                                                    if loan_account.interest_type == "Flat" :
                                                                                        loan_account.interest_charged = d(d((d(loan_account.loan_amount) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                    elif loan_account.interest_type == "Declining":
                                                                                        loan_account.interest_charged = d(d((d(loan_account.total_loan_balance) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                elif d(request.POST.get("loaninterest_amount")) < d(loan_account.interest_charged) :
                                                                                    balance_interest = d(loan_account.interest_charged) - d(request.POST.get("loaninterest_amount"))
                                                                                    if loan_account.interest_type == "Flat" :
                                                                                        interest_charged = d(d((d(loan_account.loan_amount) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                    elif loan_account.interest_type == "Declining":
                                                                                        interest_charged = d(d((d(loan_account.total_loan_balance) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                    loan_account.interest_charged = d(balance_interest + interest_charged)

                                                                                if d(request.POST.get("loanprinciple_amount")) == d(loan_account.principle_repayment) :
                                                                                    loan_account.principle_repayment = d(loan_account.total_loan_balance)
                                                                                    loan_account.loan_repayment_amount = d(d(loan_account.total_loan_balance) + d(loan_account.interest_charged))
                                                                                elif d(request.POST.get("loanprinciple_amount")) < d(loan_account.principle_repayment) :
                                                                                    balance_principle = d(d(d(loan_account.loan_repayment_amount) - d(loan_account.interest_charged)) - d(request.POST.get("loanprinciple_amount")))
                                                                                    loan_account.principle_repayment = d(d(loan_account.total_loan_balance) +  d(balance_principle))
                                                                                    loan_account.loan_repayment_amount = d(d(loan_account.total_loan_balance) + d(loan_account.interest_charged) + d(balance_principle))

                                                                            elif int(loan_account.no_of_repayments_completed) < int(loan_account.loan_repayment_period) :
                                                                                principle_repayable = d(d(loan_account.loan_amount) / d(loan_account.loan_repayment_period))
                                                                                if loan_account.interest_type == "Flat" :
                                                                                    if d(request.POST.get("loaninterest_amount")) == d(loan_account.interest_charged) :
                                                                                        loan_account.interest_charged = d(int(loan_account.loan_repayment_every) * d((d(loan_account.loan_amount) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                    elif d(request.POST.get("loaninterest_amount")) < d(loan_account.interest_charged) :
                                                                                        balance_interest = d(loan_account.interest_charged) - d(request.POST.get("loaninterest_amount"))
                                                                                        interest_charged = d(int(loan_account.loan_repayment_every) * d((d(loan_account.loan_amount) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                        loan_account.interest_charged = d(balance_interest + interest_charged)
                                                                                elif loan_account.interest_type == "Declining":
                                                                                    if d(request.POST.get("loaninterest_amount")) == d(loan_account.interest_charged) :
                                                                                        loan_account.interest_charged = d(int(loan_account.loan_repayment_every) * d((d(loan_account.total_loan_balance) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                    elif d(request.POST.get("loaninterest_amount")) < d(loan_account.interest_charged) :
                                                                                        balance_interest = d(loan_account.interest_charged) - d(request.POST.get("loaninterest_amount"))
                                                                                        interest_charged = d(int(loan_account.loan_repayment_every) * d((d(loan_account.total_loan_balance) * (d(loan_account.annual_interest_rate) / 12)) / 100))
                                                                                        loan_account.interest_charged = d(balance_interest + interest_charged)

                                                                                if d(request.POST.get("loanprinciple_amount")) == d((int(loan_account.loan_repayment_every) * d(principle_repayable))) :
                                                                                    if d(loan_account.total_loan_balance) < d((int(loan_account.loan_repayment_every) * d(principle_repayable))) :
                                                                                        loan_account.principle_repayment = d(loan_account.total_loan_balance)
                                                                                        loan_account.loan_repayment_amount = d(d(loan_account.total_loan_balance) + d(loan_account.interest_charged))
                                                                                    else:
                                                                                        loan_account.principle_repayment = d(int(loan_account.loan_repayment_every) * (d(loan_account.loan_amount) / d(loan_account.loan_repayment_period)))
                                                                                        loan_account.loan_repayment_amount = d(d(loan_account.principle_repayment) + d(loan_account.interest_charged))
                                                                                elif d(request.POST.get("loanprinciple_amount")) < d((int(loan_account.loan_repayment_every) * d(principle_repayable))) :
                                                                                    balance_principle = d(d((int(loan_account.loan_repayment_every) * d(principle_repayable))) - d(request.POST.get("loanprinciple_amount")))
                                                                                    if d(loan_account.total_loan_balance) < d((int(loan_account.loan_repayment_every) * d(principle_repayable))) :
                                                                                        loan_account.principle_repayment = d(loan_account.total_loan_balance)
                                                                                        loan_account.loan_repayment_amount = d(d(loan_account.total_loan_balance) + d(loan_account.interest_charged))
                                                                                    else:
                                                                                        loan_account.principle_repayment  = d((int(loan_account.loan_repayment_every) * d(principle_repayable)) + d(balance_principle))
                                                                                        loan_account.loan_repayment_amount = d((int(loan_account.loan_repayment_every) * d(principle_repayable)) + d(loan_account.interest_charged) + d(balance_principle))
                                                                else:
                                                                    data = {"error": True, "message1": "Amount is greater than loan balance."}
                                                                    return HttpResponse(json.dumps(data))
                                                            else:
                                                                data = {"error": True, "message1": "Loan has been cleared sucessfully."}
                                                                return HttpResponse(json.dumps(data))
                                                        else:
                                                            data = {"error": True, "message1": "Loan Payment has not yet done."}
                                                            return HttpResponse(json.dumps(data))
                                                    elif loan_account.status == "Applied":
                                                        data = {"error": True, "message1": "Member Loan / Group Loan is under pending for approval."}
                                                        return HttpResponse(json.dumps(data))
                                                    elif loan_account.status == "Rejected":
                                                        data = {"error": True, "message1": "Member Loan has been Rejected."}
                                                        return HttpResponse(json.dumps(data))
                                                    elif loan_account.status == "Closed":
                                                        data = {"error": True, "message1": "Member Loan has been Closed."}
                                                        return HttpResponse(json.dumps(data))
                                                    elif group_loan_account.status == "Applied":
                                                        data = {"error": True, "message1": "Group Loan is under pending for approval."}
                                                        return HttpResponse(json.dumps(data))
                                                    elif group_loan_account.status == "Rejected":
                                                        data = {"error": True, "message1": "Group Loan has been Rejected."}
                                                        return HttpResponse(json.dumps(data))
                                                    elif group_loan_account.status == "Closed":
                                                        data = {"error": True, "message1": "Group Loan has been Closed."}
                                                        return HttpResponse(json.dumps(data))
                                                except LoanAccount.DoesNotExist:
                                                    data = {"error": True, "message1": "Group does not have any Loan with this Loan A/C Number."}
                                                    return HttpResponse(json.dumps(data))
                                            else:
                                                data = {"error": True, "message1": "Please enter the group loan account number."}
                                                return HttpResponse(json.dumps(data))
                                        else:
                                            data = {"error": True, "message1": "Member does not belong to this group.Please check Group name and Account Number."}
                                            return HttpResponse(json.dumps(data))
                                    except Group.DoesNotExist:
                                        data = {"error": True, "message1": "Group does not exists with this Name and Account Number."}
                                        return HttpResponse(json.dumps(data))
                                else:
                                    data = {"error": True, "message1": "Please enter the Group Name and Account Number."}
                                    return HttpResponse(json.dumps(data))
                            except ObjectDoesNotExist:
                                data = {"error": True, "message1": "Member has not been assigned to any group."}
                                return HttpResponse(json.dumps(data))
                        except LoanAccount.DoesNotExist:
                            data = {"error": True, "message1": "Member does not have any Loan with this Loan A/C Number."}
                            return HttpResponse(json.dumps(data))
                    else:
                        data = {"error": True, "message1": "Please enter the Member Loan A/C Number."}
                        return HttpResponse(json.dumps(data))


                if request.POST.get("sharecapital_amount") or request.POST.get("entrancefee_amount") or request.POST.get("membershipfee_amount") or request.POST.get("bookfee_amount") or request.POST.get("loanprocessingfee_amount") or request.POST.get("savingsdeposit_thrift_amount") or request.POST.get("fixeddeposit_amount") or request.POST.get("recurringdeposit_amount") or request.POST.get("loanprinciple_amount") or request.POST.get("insurance_amount") or d(request.POST.get("loaninterest_amount")) != 0 :
                    try:
                        client_group = client.group_set.get()
                        receipt = Receipts.objects.create(
                            date=date,
                            branch=branch,
                            receipt_number=receipt_number,
                            client=client,
                            group=client_group,
                            staff=staff
                        )
                    except ObjectDoesNotExist:
                        receipt = Receipts.objects.create(date=date, branch=branch, receipt_number=receipt_number, client=client, staff=staff)
                    if request.POST.get("sharecapital_amount"):
                        receipt.sharecapital_amount = d(request.POST.get("sharecapital_amount"))
                    if request.POST.get("entrancefee_amount"):
                        receipt.entrancefee_amount = d(request.POST.get("entrancefee_amount"))
                    if request.POST.get("membershipfee_amount"):
                        receipt.membershipfee_amount = d(request.POST.get("membershipfee_amount"))
                    if request.POST.get("bookfee_amount"):
                        receipt.bookfee_amount = d(request.POST.get("bookfee_amount"))
                    if request.POST.get("loanprocessingfee_amount"):
                        receipt.loanprocessingfee_amount = d(request.POST.get("loanprocessingfee_amount"))
                        receipt.member_loan_account = loan_account
                        receipt.group_loan_account = group_loan_account
                    if request.POST.get("savingsdeposit_thrift_amount"):
                        receipt.savingsdeposit_thrift_amount = d(request.POST.get("savingsdeposit_thrift_amount"))
                        receipt.savings_balance_atinstant = d(savings_account.savings_balance)
                    if request.POST.get("fixeddeposit_amount"):
                        receipt.fixeddeposit_amount = d(request.POST.get("fixeddeposit_amount"))
                    if request.POST.get("recurringdeposit_amount"):
                        receipt.recurringdeposit_amount = d(request.POST.get("recurringdeposit_amount"))
                    if request.POST.get("insurance_amount"):
                        receipt.insurance_amount = d(request.POST.get("insurance_amount"))
                    if request.POST.get("loanprinciple_amount"):
                        receipt.loanprinciple_amount = d(request.POST.get("loanprinciple_amount"))
                        receipt.member_loan_account = loan_account
                        receipt.group_loan_account = group_loan_account
                    if d(request.POST.get("loaninterest_amount")) != int(0):
                        receipt.loaninterest_amount = d(request.POST.get("loaninterest_amount"))
                        receipt.member_loan_account = loan_account
                        receipt.group_loan_account = group_loan_account

                    try:
                        if var_demand_loanprinciple_amount_atinstant:
                            receipt.demand_loanprinciple_amount_atinstant = d(var_demand_loanprinciple_amount_atinstant)
                    except NameError:
                        pass

                    try:
                        if var_demand_loaninterest_amount_atinstant:
                            receipt.demand_loaninterest_amount_atinstant = d(var_demand_loaninterest_amount_atinstant)
                    except NameError:
                        pass

                    try:
                        receipt.principle_loan_balance_atinstant = d(loan_account.total_loan_balance)
                    except Exception:
                        pass

                    receipt.save()
                    client.save()
                    try:
                        savings_account.save()
                    except NameError:
                        pass
                    try:
                        loan_account.save()
                    except NameError:
                        pass
                    try:
                        group_savings_account.save()
                    except NameError:
                        pass
                    data = {"error": False}
                    return HttpResponse(json.dumps(data))
                else:
                    data = {"error": True, "message1": "Empty Receipt can't be generated."}
                    return HttpResponse(json.dumps(data))
            except Client.DoesNotExist:
                data = {"error": True, "message1": "No Client exists with this First Name and Account number."}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": receipt_form.errors}
            return HttpResponse(json.dumps(data))


class ReceiptsList(LoginRequiredMixin, ListView):
    context_object_name = "receipt_list"
    queryset = Receipts.objects.all().order_by("-id")
    template_name = "listof_receipts.html"


def general_ledger_function():
    return Receipts.objects.all().values("date").distinct().order_by("-date").annotate(
        sum_sharecapital_amount=Sum('sharecapital_amount'),
        sum_entrancefee_amount=Sum('entrancefee_amount'),
        sum_membershipfee_amount=Sum('membershipfee_amount'),
        sum_bookfee_amount=Sum('bookfee_amount'),
        sum_loanprocessingfee_amount=Sum('loanprocessingfee_amount'),
        sum_savingsdeposit_thrift_amount=Sum('savingsdeposit_thrift_amount'),
        sum_fixeddeposit_amount=Sum('fixeddeposit_amount'),
        sum_recurringdeposit_amount=Sum('recurringdeposit_amount'),
        sum_loanprinciple_amount=Sum('loanprinciple_amount'),
        sum_loaninterest_amount=Sum('loaninterest_amount'),
        sum_insurance_amount=Sum('insurance_amount'),
        total_sum=(Sum('sharecapital_amount') + Sum('entrancefee_amount') +
                   Sum('membershipfee_amount') + Sum('bookfee_amount') +
                   Sum('loanprocessingfee_amount') + Sum('savingsdeposit_thrift_amount') +
                   Sum('fixeddeposit_amount') + Sum('recurringdeposit_amount') +
                   Sum('loanprinciple_amount') + Sum('loaninterest_amount') +
                   Sum('insurance_amount'))
    )


class GeneralLedger(LoginRequiredMixin, ListView):
    context_object_name = "list"
    template_name = "generalledger.html"

    def get_queryset(self):
        return general_ledger_function()


class FixedDepositsView(LoginRequiredMixin, CreateView):
    form_class = FixedDepositForm
    template_name = "client/fixed-deposits/fixed_deposit_application.html"

    def form_valid(self, form):
        fixed_deposit = form.save(commit=False)
        fixed_deposit.status = "Opened"
        fixed_deposit.client = form.client
        interest_charged = (fixed_deposit.fixed_deposit_amount * (
                            fixed_deposit.fixed_deposit_interest_rate / 12)) / 100
        fixed_deposit_interest_charged = interest_charged * d(
            fixed_deposit.fixed_deposit_period)
        fixed_deposit.maturity_amount = (fixed_deposit.fixed_deposit_amount +
                                         fixed_deposit_interest_charged)
        fixed_deposit.fixed_deposit_interest = (
            fixed_deposit.maturity_amount - fixed_deposit.fixed_deposit_amount
        )
        fixed_deposit.save()
        url = reverse('micro_admin:clientfixeddepositsprofile',
                      kwargs={"fixed_deposit_id": fixed_deposit.id})
        return JsonResponse({"error": False, "success_url": url})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class ClientFixedDepositsProfile(LoginRequiredMixin, DetailView):
    model = FixedDeposits
    pk_url_kwarg = "fixed_deposit_id"
    context_object_name = "fixed_deposit"
    template_name = "client/fixed-deposits/fixed_deposits_profile.html"


class ViewClientFixedDeposits(LoginRequiredMixin, ListView):
    model = FixedDeposits
    template_name = "client/fixed-deposits/view_fixed_deposits.html"
    context_object_name = "fixed_deposit_list"


class ViewParticularClientFixedDeposits(LoginRequiredMixin, ListView):
    context_object_name = "fixed_deposit_list"
    template_name = "client/fixed-deposits/view_fixed_deposits.html"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        queryset = FixedDeposits.objects.filter(client=self.client).order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ViewParticularClientFixedDeposits, self).get_context_data(**kwargs)
        context["client"] = self.client
        return context


class ClientRecurringDepositsProfile(LoginRequiredMixin, DetailView):
    model = RecurringDeposits
    pk_url_kwarg = "recurring_deposit_id"
    context_object_name = "recurring_deposit"
    template_name = "client/recurring-deposits/recurring_deposit_profile.html"


class ViewClientRecurringDeposits(LoginRequiredMixin, ListView):
    queryset = RecurringDeposits.objects.all().order_by("-id")
    template_name = "client/recurring-deposits/view_recurring_deposits.html"
    context_object_name = "recurring_deposit_list"


class ViewParticularClientRecurringDeposits(LoginRequiredMixin, ListView):
    template_name = "client/recurring-deposits/view_recurring_deposits.html"
    context_object_name = "recurring_deposit_list"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        queryset = RecurringDeposits.objects.filter(client=self.client).order_by("-id")
        return queryset

    def get_context_data(self):
        context = super(ViewParticularClientRecurringDeposits, self).get_context_data()
        context["client"] = self.client
        return context


def get_results_list(receipts_list, group_id, thrift_deposit_sum_list, loanprinciple_amount_sum_list, loaninterest_amount_sum_list,
                     entrancefee_amount_sum_list, membershipfee_amount_sum_list, bookfee_amount_sum_list,
                     loanprocessingfee_amount_sum_list, insurance_amount_sum_list, fixed_deposit_sum_list,
                     recurring_deposit_sum_list, share_capital_amount_sum_list):
    group = None
    if group_id:
        group = Group.objects.get(id=group_id)

    thrift_deposit_sum, loanprinciple_amount_sum, loaninterest_amount_sum, entrancefee_amount_sum, \
        membershipfee_amount_sum, bookfee_amount_sum, loanprocessingfee_amount_sum, \
        insurance_amount_sum, fixed_deposit_sum, recurring_deposit_sum, \
        share_capital_amount_sum = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    if group:
        thrift_deposit_receipts_list, loanprinciple_receipts_list, loaninterest_receipts_list, \
            entrancefee_receipts_list, membershipfee_receipts_list, bookfee_receipts_list, \
            loanprocessingfee_receipts_list, insurance_receipts_list, fixed_deposit_receipts_list, \
            recurring_deposit_receipts_list, share_capital_receipts_list = [], [], [], [], [], [], [], [], [], [], []

    for receipt in receipts_list:
        if receipt.savingsdeposit_thrift_amount and receipt.savingsdeposit_thrift_amount > 0:
            if group:
                thrift_deposit_receipts_list.append(receipt)
            thrift_deposit_sum += d(receipt.savingsdeposit_thrift_amount)
        if receipt.loanprinciple_amount and receipt.loanprinciple_amount > 0:
            if group:
                loanprinciple_receipts_list.append(receipt)
            loanprinciple_amount_sum += d(receipt.loanprinciple_amount)
        if receipt.loaninterest_amount and receipt.loaninterest_amount > 0:
            if group:
                loaninterest_receipts_list.append(receipt)
            loaninterest_amount_sum += d(receipt.loaninterest_amount)
        if receipt.entrancefee_amount and receipt.entrancefee_amount > 0:
            if group:
                entrancefee_receipts_list.append(receipt)
            entrancefee_amount_sum += d(receipt.entrancefee_amount)
        if receipt.membershipfee_amount and receipt.membershipfee_amount > 0:
            if group:
                membershipfee_receipts_list.append(receipt)
            membershipfee_amount_sum += d(receipt.membershipfee_amount)
        if receipt.bookfee_amount and receipt.bookfee_amount > 0:
            if group:
                bookfee_receipts_list.append(receipt)
            bookfee_amount_sum += d(receipt.bookfee_amount)
        if receipt.loanprocessingfee_amount and receipt.loanprocessingfee_amount > 0:
            if group:
                loanprocessingfee_receipts_list.append(receipt)
            loanprocessingfee_amount_sum += d(receipt.loanprocessingfee_amount)
        if receipt.insurance_amount and receipt.insurance_amount > 0:
            if group:
                insurance_receipts_list.append(receipt)
            insurance_amount_sum += d(receipt.insurance_amount)
        if receipt.fixeddeposit_amount and receipt.fixeddeposit_amount > 0:
            if group:
                fixed_deposit_receipts_list.append(receipt)
            fixed_deposit_sum += d(receipt.fixeddeposit_amount)
        if receipt.recurringdeposit_amount and receipt.recurringdeposit_amount > 0:
            if group:
                recurring_deposit_receipts_list.append(receipt)
            recurring_deposit_sum += d(receipt.recurringdeposit_amount)
        if receipt.sharecapital_amount and receipt.sharecapital_amount > 0:
            if group:
                share_capital_receipts_list.append(receipt)
            share_capital_amount_sum += d(receipt.sharecapital_amount)

    # Share Capital
    share_capital_amount_sum_list.append({
        "share_capital_amount_sum": share_capital_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": share_capital_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Recurring deposits
    recurring_deposit_sum_list.append({
        "recurring_deposit_sum": recurring_deposit_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": recurring_deposit_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Fixed Deposits
    fixed_deposit_sum_list.append({
        "fixed_deposit_sum": fixed_deposit_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": fixed_deposit_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Savings(Thrift) Deposits
    thrift_deposit_sum_list.append({
        "thrift_deposit_sum": thrift_deposit_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": thrift_deposit_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Loan priniciple repayments
    loanprinciple_amount_sum_list.append({
        "loanprinciple_amount_sum": loanprinciple_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": loanprinciple_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Loan interest Repayments
    loaninterest_amount_sum_list.append({
        "loaninterest_amount_sum": loaninterest_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": loaninterest_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Entrance fees
    entrancefee_amount_sum_list.append({
        "entrancefee_amount_sum": entrancefee_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": entrancefee_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Membership Fees
    membershipfee_amount_sum_list.append({
        "membershipfee_amount_sum": membershipfee_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": membershipfee_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Book Fees
    bookfee_amount_sum_list.append({
        "bookfee_amount_sum": bookfee_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": bookfee_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Loan Processing fees
    loanprocessingfee_amount_sum_list.append({
        "loanprocessingfee_amount_sum": loanprocessingfee_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": loanprocessingfee_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    # Insurance Amounts
    insurance_amount_sum_list.append({
        "insurance_amount_sum": insurance_amount_sum,
        "group_name": group.name if group else receipt.client.first_name,
        "account_number": group.account_number if group else receipt.client.account_number,
        "receipt_number": insurance_receipts_list if group else receipt.receipt_number,
        "has_list": True if group else False
    })

    return thrift_deposit_sum_list, loanprinciple_amount_sum_list, loaninterest_amount_sum_list, entrancefee_amount_sum_list, \
        membershipfee_amount_sum_list, bookfee_amount_sum_list, loanprocessingfee_amount_sum_list, insurance_amount_sum_list, \
        fixed_deposit_sum_list, recurring_deposit_sum_list, share_capital_amount_sum_list


def day_book_function(request, date):
    selected_date = date
    query_set = Receipts.objects.filter(date=selected_date)
    grouped_receipts_list = list(set([i.group_id for i in query_set]))
    receipts_list = []

    thrift_deposit_sum_list, loanprinciple_amount_sum_list, loaninterest_amount_sum_list, entrancefee_amount_sum_list, \
        membershipfee_amount_sum_list, bookfee_amount_sum_list, loanprocessingfee_amount_sum_list, insurance_amount_sum_list, \
        fixed_deposit_sum_list, recurring_deposit_sum_list, share_capital_amount_sum_list = [], [], [], [], [], [], [], [], [], [], []

    for group_id in grouped_receipts_list:
        if group_id:
            receipts_list = Receipts.objects.filter(group=group_id, date=selected_date)
            # Calculate all the deposits collected from this group.
            (thrift_deposit_sum_list, loanprinciple_amount_sum_list, loaninterest_amount_sum_list, entrancefee_amount_sum_list,
             membershipfee_amount_sum_list, bookfee_amount_sum_list, loanprocessingfee_amount_sum_list, insurance_amount_sum_list,
             fixed_deposit_sum_list, recurring_deposit_sum_list, share_capital_amount_sum_list) = \
                get_results_list(receipts_list, group_id, thrift_deposit_sum_list, loanprinciple_amount_sum_list,
                                 loaninterest_amount_sum_list, entrancefee_amount_sum_list, membershipfee_amount_sum_list,
                                 bookfee_amount_sum_list, loanprocessingfee_amount_sum_list, insurance_amount_sum_list,
                                 fixed_deposit_sum_list, recurring_deposit_sum_list, share_capital_amount_sum_list)
        else:
            receipts_list = Receipts.objects.filter(group=None, date=selected_date)
            for receipt in receipts_list:
                # Calculate individual deposit.
                (thrift_deposit_sum_list, loanprinciple_amount_sum_list, loaninterest_amount_sum_list, entrancefee_amount_sum_list,
                 membershipfee_amount_sum_list, bookfee_amount_sum_list, loanprocessingfee_amount_sum_list, insurance_amount_sum_list,
                 fixed_deposit_sum_list, recurring_deposit_sum_list, share_capital_amount_sum_list) = \
                    get_results_list([receipt], None, thrift_deposit_sum_list, loanprinciple_amount_sum_list,
                                     loaninterest_amount_sum_list, entrancefee_amount_sum_list, membershipfee_amount_sum_list,
                                     bookfee_amount_sum_list, loanprocessingfee_amount_sum_list, insurance_amount_sum_list,
                                     fixed_deposit_sum_list, recurring_deposit_sum_list, share_capital_amount_sum_list)

    total_dict = {
        "total_recurring_deposit_sum": sum([i["recurring_deposit_sum"] for i in recurring_deposit_sum_list]),
        "total_share_capital_amount_sum": sum([i["share_capital_amount_sum"] for i in share_capital_amount_sum_list]),
        "total_fixed_deposit_sum": sum([i["fixed_deposit_sum"] for i in fixed_deposit_sum_list]),
        "total_thrift_deposit_sum": sum([i["thrift_deposit_sum"] for i in thrift_deposit_sum_list]),
        "total_loanprinciple_amount_sum": sum([i["loanprinciple_amount_sum"] for i in loanprinciple_amount_sum_list]),
        "total_loaninterest_amount_sum": sum([i["loaninterest_amount_sum"] for i in loaninterest_amount_sum_list]),
        "total_entrancefee_amount_sum": sum([i["entrancefee_amount_sum"] for i in entrancefee_amount_sum_list]),
        "total_membershipfee_amount_sum": sum([i["membershipfee_amount_sum"] for i in membershipfee_amount_sum_list]),
        "total_bookfee_amount_sum": sum([i["bookfee_amount_sum"] for i in bookfee_amount_sum_list]),
        "total_loanprocessingfee_amount_sum": sum([i["loanprocessingfee_amount_sum"] for i in loanprocessingfee_amount_sum_list]),
        "total_insurance_amount_sum": sum([i["insurance_amount_sum"] for i in insurance_amount_sum_list]),
    }
    # Total deposits anount
    total = sum([value for value in total_dict.values()])

    # Payments totals
    payments_list = Payments.objects.filter(date=selected_date)
    travellingallowance_list, loans_list, paymentofsalary_list, printingcharges_list, \
        stationarycharges_list, othercharges_list, savingswithdrawal_list, \
        fixedwithdrawal_list, recurringwithdrawal_list = [], [], [], [], [], [], [], [], []

    for payment in payments_list:
        if payment.payment_type == "TravellingAllowance":
            travellingallowance_list.append(payment)
        elif payment.payment_type == "Loans":
            loans_list.append(payment)
        elif payment.payment_type == "Paymentofsalary":
            paymentofsalary_list.append(payment)
        elif payment.payment_type == "PrintingCharges":
            printingcharges_list.append(payment)
        elif payment.payment_type == "StationaryCharges":
            stationarycharges_list.append(payment)
        elif payment.payment_type == "OtherCharges":
            othercharges_list.append(payment)
        elif payment.payment_type == "SavingsWithdrawal":
            savingswithdrawal_list.append(payment)
        elif payment.payment_type == "FixedWithdrawal":
            fixedwithdrawal_list.append(payment)
        elif payment.payment_type == "RecurringWithdrawal":
            recurringwithdrawal_list.append(payment)

    dict_payments = {
        "loans_sum": sum([i.total_amount for i in loans_list]),
        "othercharges_sum": sum([i.total_amount for i in othercharges_list]),
        "fixedwithdrawal_sum": sum([i.total_amount for i in fixedwithdrawal_list]),
        "paymentofsalary_sum": sum([i.total_amount for i in paymentofsalary_list]),
        "printingcharges_sum": sum([i.total_amount for i in printingcharges_list]),
        "stationarycharges_sum": sum([i.total_amount for i in stationarycharges_list]),
        "savingswithdrawal_sum": sum([i.total_amount for i in savingswithdrawal_list]),
        "recurringwithdrawal_sum": sum([i.total_amount for i in recurringwithdrawal_list]),
        "travellingallowance_sum": sum([i.total_amount for i in travellingallowance_list]),
    }

    # Total payments amount
    total_payments = sum([value for value in dict_payments.values()])

    return receipts_list, total_payments, travellingallowance_list, \
        loans_list, paymentofsalary_list, printingcharges_list, \
        stationarycharges_list, othercharges_list, savingswithdrawal_list, \
        recurringwithdrawal_list, fixedwithdrawal_list, total, dict_payments, \
        total_dict, selected_date, grouped_receipts_list, \
        thrift_deposit_sum_list, loanprinciple_amount_sum_list, \
        loaninterest_amount_sum_list, entrancefee_amount_sum_list, \
        membershipfee_amount_sum_list, bookfee_amount_sum_list, \
        loanprocessingfee_amount_sum_list, insurance_amount_sum_list, \
        fixed_deposit_sum_list, recurring_deposit_sum_list, \
        share_capital_amount_sum_list


class DayBookView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if self.request.GET.get("date"):
            try:
                self.date = datetime.datetime.strptime(self.request.GET.get("date"), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return render(request, "day_book.html", {"error_message": "Invalid date."})
        else:
            self.date = datetime.datetime.now().date()

        context = self.get_context_data(**kwargs)
        return render(request, "day_book.html", context)

    def post(self, request, *args, **kwargs):
        try:
            self.date = datetime.datetime.strptime(self.request.POST.get("date"), "%m/%d/%Y").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return render(request, "day_book.html", {"error_message": "Invalid date."})

        context = self.get_context_data(**kwargs)
        return render(request, "day_book.html", context)

    def get_context_data(self):
        date = self.date

        receipts_list, total_payments, travellingallowance_list, \
            loans_list, paymentofsalary_list, printingcharges_list, \
            stationarycharges_list, othercharges_list, savingswithdrawal_list,\
            recurringwithdrawal_list, fixedwithdrawal_list, total, \
            dict_payments, total_dict, selected_date, grouped_receipts_list, \
            thrift_deposit_sum_list, loanprinciple_amount_sum_list, \
            loaninterest_amount_sum_list, entrancefee_amount_sum_list, \
            membershipfee_amount_sum_list, bookfee_amount_sum_list, \
            loanprocessingfee_amount_sum_list, insurance_amount_sum_list, \
            fixed_deposit_sum_list, recurring_deposit_sum_list, \
            share_capital_amount_sum_list = day_book_function(self.request, date)

        date_formated = datetime.datetime.strptime(str(selected_date), "%Y-%m-%d").strftime("%m/%d/%Y")
        return {
            "receipts_list": receipts_list, "total_payments": total_payments,
            "fixedwithdrawal_list": fixedwithdrawal_list, "total": total,
            "dict_payments": dict_payments, "dict": total_dict,
            "selected_date": selected_date, "date_formated": date_formated,
            "othercharges_list": othercharges_list, "loans_list": loans_list,
            "loanprinciple_amount_sum_list": loanprinciple_amount_sum_list,
            "loaninterest_amount_sum_list": loaninterest_amount_sum_list,
            "entrancefee_amount_sum_list": entrancefee_amount_sum_list,
            "membershipfee_amount_sum_list": membershipfee_amount_sum_list,
            "share_capital_amount_sum_list": share_capital_amount_sum_list,
            "bookfee_amount_sum_list": bookfee_amount_sum_list,
            "insurance_amount_sum_list": insurance_amount_sum_list,
            "recurring_deposit_sum_list": recurring_deposit_sum_list,
            "fixed_deposit_sum_list": fixed_deposit_sum_list,
            "travellingallowance_list": travellingallowance_list,
            "paymentofsalary_list": paymentofsalary_list,
            "printingcharges_list": printingcharges_list,
            "stationarycharges_list": stationarycharges_list,
            "savingswithdrawal_list": savingswithdrawal_list,
            "recurringwithdrawal_list": recurringwithdrawal_list,
            "grouped_receipts_list": grouped_receipts_list,
            "thrift_deposit_sum_list": thrift_deposit_sum_list,
            "loanprocessingfee_amount_sum_list": loanprocessingfee_amount_sum_list,
        }


class RecurringDepositsView(LoginRequiredMixin, CreateView):
    form_class = ReccuringDepositForm
    template_name = "client/recurring-deposits/application.html"

    def form_valid(self, form):
        recurring_deposit = form.save(commit=False)
        recurring_deposit.status = "Opened"
        recurring_deposit.client = form.client
        recurring_deposit.save()
        url = reverse('micro_admin:clientrecurringdepositsprofile',
                      kwargs={"recurring_deposit_id": recurring_deposit.id})
        return JsonResponse({"error": False, "success_url": url})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class PaymentsList(LoginRequiredMixin, ListView):
    queryset = Payments.objects.all().order_by("-id")
    context_object_name = "payments_list"
    template_name = "list_of_payments.html"


@login_required
def pay_slip(request):
    if request.method == "GET":
        branches = Branch.objects.all()
        voucher_types = []
        for voucher_type in PAYMENT_TYPES:
            voucher_types.append(voucher_type[0])
        return render(request, "paymentform.html", {"branches": branches, "voucher_types": voucher_types})
    elif request.method == "POST":
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            datestring_format = datetime.datetime.strptime(request.POST.get("date"), "%m/%d/%Y").strftime("%Y-%m-%d")
            dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            date = dateconvert
            branch = Branch.objects.get(id=request.POST.get("branch"))
            voucher_number = request.POST.get("voucher_number")
            payment_type = request.POST.get("payment_type")
            amount = request.POST.get("amount")
            total_amount = request.POST.get("total_amount")
            totalamount_in_words = request.POST.get("totalamount_in_words")

            if d(request.POST.get("amount")) != 0 and d(request.POST.get("total_amount")) != 0:

                if request.POST.get("payment_type") == "TravellingAllowance" or request.POST.get("payment_type") == "Paymentofsalary":
                    if not request.POST.get("staff_username"):
                        data = {"error": True, "message1": "Please enter Employee Username"}
                        return HttpResponse(json.dumps(data))
                    elif request.POST.get("staff_username"):
                        try:
                            staff = User.objects.get(username__iexact=request.POST.get("staff_username"))
                            if not request.POST.get("interest"):
                                if d(request.POST.get("total_amount")) == d(request.POST.get("amount")):
                                    Payments.objects.create(
                                        date=date,
                                        branch=branch,
                                        voucher_number=voucher_number,
                                        payment_type=payment_type,
                                        staff=staff,
                                        amount=amount,
                                        total_amount=total_amount,
                                        totalamount_in_words=totalamount_in_words
                                    )
                                    data = {"error": False}
                                    return HttpResponse(json.dumps(data))
                                else:
                                    data = {"error": True, "message1": "Entered total amount is not equal to amount."}
                                    return HttpResponse(json.dumps(data))
                            else:
                                data = {"error": True, "message1": "Interest must be empty for TA and Payment of salary Voucher."}
                                return HttpResponse(json.dumps(data))
                        except User.DoesNotExist:
                            data = {"error": True, "message1": "Entered Employee Username is incorrect"}
                            return HttpResponse(json.dumps(data))

                elif request.POST.get("payment_type") == "PrintingCharges" or request.POST.get("payment_type") == "StationaryCharges" or request.POST.get("payment_type") == "OtherCharges" :
                    if not request.POST.get("interest"):
                        if d(request.POST.get("total_amount")) == d(request.POST.get("amount")):
                            Payments.objects.create(
                                date=date,
                                branch=branch,
                                voucher_number=voucher_number,
                                payment_type=payment_type,
                                amount=amount,
                                total_amount=total_amount,
                                totalamount_in_words=totalamount_in_words
                            )
                            data = {"error": False}
                            return HttpResponse(json.dumps(data))
                        else:
                            data = {"error": True, "message1": "Entered total amount is not equal to amount."}
                            return HttpResponse(json.dumps(data))
                    else:
                        data = {"error": True, "message1": "Interest must be empty for Charges Voucher."}
                        return HttpResponse(json.dumps(data))

                elif request.POST.get("payment_type") == "SavingsWithdrawal":
                    if not request.POST.get("client_name"):
                        data = {"error": True, "message1": "Please enter the Member First Name"}
                        return HttpResponse(json.dumps(data))
                    elif request.POST.get("client_name"):
                        if not request.POST.get("client_account_number"):
                            data = {"error": True, "message1": "Please enter the Member Account number"}
                            return HttpResponse(json.dumps(data))
                        try:
                            client = Client.objects.get(first_name__iexact=request.POST.get("client_name"), \
                                                            account_number=request.POST.get("client_account_number"))
                            try:
                                savings_account = SavingsAccount.objects.get(client=client)
                                if d(savings_account.savings_balance) >= d(request.POST.get("amount")):
                                    try:
                                        client_group = client.group_set.get()
                                        try:
                                            group_savings_account = SavingsAccount.objects.get(group=client_group)
                                            if d(group_savings_account.savings_balance) >= d(request.POST.get("amount")):
                                                if request.POST.get("group_name"):
                                                    if request.POST.get("group_name").lower() == client_group.name.lower():
                                                        if request.POST.get("group_account_number"):
                                                            if request.POST.get("group_account_number") == client_group.account_number:
                                                                if not request.POST.get("interest"):
                                                                    if d(request.POST.get("total_amount")) == d(request.POST.get("amount")):
                                                                        payment = Payments.objects.create(
                                                                            date=date,
                                                                            branch=branch,
                                                                            voucher_number=voucher_number,
                                                                            client=client,
                                                                            group=client_group,
                                                                            payment_type=payment_type,
                                                                            amount=amount,
                                                                            total_amount=total_amount,
                                                                            totalamount_in_words=totalamount_in_words
                                                                        )
                                                                        savings_account.savings_balance -= d(request.POST.get("amount"))
                                                                        savings_account.total_withdrawals += d(request.POST.get("amount"))
                                                                        savings_account.save()

                                                                        group_savings_account.savings_balance -= d(request.POST.get("amount"))
                                                                        group_savings_account.total_withdrawals += d(request.POST.get("amount"))
                                                                        group_savings_account.save()
                                                                        data = {"error": False}
                                                                        return HttpResponse(json.dumps(data))
                                                                    else:
                                                                        data = {"error": True, "message1": "Entered total amount is not equal to amount."}
                                                                        return HttpResponse(json.dumps(data))

                                                                elif request.POST.get("interest"):
                                                                    if d(request.POST.get("total_amount")) == d(d(request.POST.get("amount")) + d(request.POST.get("interest"))) :
                                                                        payment = Payments.objects.create(
                                                                            date=date,
                                                                            branch=branch,
                                                                            voucher_number=voucher_number,
                                                                            client=client,
                                                                            group=client_group,
                                                                            payment_type=payment_type,
                                                                            amount=amount,
                                                                            interest=request.POST.get("interest"),
                                                                            total_amount=total_amount,
                                                                            totalamount_in_words=totalamount_in_words
                                                                        )
                                                                        savings_account.savings_balance -= d(request.POST.get("amount"))
                                                                        savings_account.total_withdrawals += d(request.POST.get("amount"))
                                                                        savings_account.save()

                                                                        group_savings_account.savings_balance -= d(request.POST.get("amount"))
                                                                        group_savings_account.total_withdrawals += d(request.POST.get("amount"))
                                                                        group_savings_account.save()
                                                                        data = {"error": False}
                                                                        return HttpResponse(json.dumps(data))
                                                                    else:
                                                                        data = {"error": True, "message1": "Entered total amount is incorrect."}
                                                                        return HttpResponse(json.dumps(data))
                                                            else:
                                                                data = {"error": True, "message1": "Entered Group A/C Number is incorrect."}
                                                                return HttpResponse(json.dumps(data))
                                                        else:
                                                            data = {"error": True, "message1": "Please enter the Group A/C Number."}
                                                            return HttpResponse(json.dumps(data))
                                                    else:
                                                        data = {"error": True, "message1": "Member does not belong to the entered Group Name."}
                                                        return HttpResponse(json.dumps(data))
                                                else:
                                                    data = {"error": True, "message1": "Please enter the Group name of the Member."}
                                                    return HttpResponse(json.dumps(data))
                                            elif d(group_savings_account.savings_balance) < d(request.POST.get("amount")):
                                                data = {"error": True, "message1": "Group Savings A/C does not have sufficient balance."}
                                                return HttpResponse(json.dumps(data))
                                        except SavingsAccount.DoesNotExist:
                                            data = {"error": True, "message1": "The Group which the Member belongs to does not have Savings Account."}
                                            return HttpResponse(json.dumps(data))
                                    except ObjectDoesNotExist:
                                        if request.POST.get("group_name") or request.POST.get("group_account_number"):
                                            data = {"error": True, "message1": "Member does not assigned to any Group. Please clear Group details"}
                                            return HttpResponse(json.dumps(data))
                                        else:
                                            if not request.POST.get("interest"):
                                                if d(request.POST.get("total_amount")) == d(request.POST.get("amount")):
                                                    Payments.objects.create(
                                                        date=date,
                                                        branch=branch,
                                                        voucher_number=voucher_number,
                                                        client=client,
                                                        payment_type=payment_type,
                                                        amount=amount,
                                                        total_amount=total_amount,
                                                        totalamount_in_words=totalamount_in_words
                                                    )
                                                    savings_account.savings_balance -= d(request.POST.get("amount"))
                                                    savings_account.total_withdrawals += d(request.POST.get("amount"))
                                                    savings_account.save()

                                                    data = {"error": False}
                                                    return HttpResponse(json.dumps(data))
                                                else:
                                                    data = {"error": True, "message1": "Entered total amount is not equal to amount."}
                                                    return HttpResponse(json.dumps(data))

                                            elif request.POST.get("interest"):
                                                if d(request.POST.get("total_amount")) == d(d(request.POST.get("amount")) + d(request.POST.get("interest"))):
                                                    Payments.objects.create(
                                                        date=date,
                                                        branch=branch,
                                                        voucher_number=voucher_number,
                                                        client=client,
                                                        payment_type=payment_type,
                                                        amount=amount,
                                                        interest=request.POST.get("interest"),
                                                        total_amount=total_amount,
                                                        totalamount_in_words=totalamount_in_words
                                                    )
                                                    savings_account.savings_balance -= d(request.POST.get("amount"))
                                                    savings_account.total_withdrawals += d(request.POST.get("amount"))
                                                    savings_account.save()

                                                    data = {"error": False}
                                                    return HttpResponse(json.dumps(data))
                                                else:
                                                    data = {"error": True, "message1": "Entered total amount is incorrect."}
                                                    return HttpResponse(json.dumps(data))

                                elif d(savings_account.savings_balance) < d(request.POST.get("amount")):
                                    data = {"error": True, "message1": "Member Savings Account does not have sufficient balance."}
                                    return HttpResponse(json.dumps(data))
                            except SavingsAccount.DoesNotExist:
                                data = {"error": True, "message1": "Member does not have Savings Account to withdraw amount."}
                                return HttpResponse(json.dumps(data))
                        except Client.DoesNotExist:
                            data = {"error": True, "message1": "Member does not exists with this First Name and A/C Number. Please enter correct details."}
                            return HttpResponse(json.dumps(data))
                elif request.POST.get("payment_type") == "Loans":
                    if request.POST.get("interest"):
                        data = {"error": True, "message1": "Interest amount must be empty while issuing Loans."}
                        return HttpResponse(json.dumps(data))
                    if request.POST.get("client_name") or request.POST.get("client_account_number"):
                        data = {"error": True, "message1": "Client details must be empty while issuing Loans."}
                        return HttpResponse(json.dumps(data))
                    if not request.POST.get("group_name"):
                        data = {"error": True, "message1": "Please enter Group Name."}
                        return HttpResponse(json.dumps(data))
                    elif request.POST.get("group_name"):
                        if not request.POST.get("group_account_number"):
                            data = {"error": True, "message1": "Please enter Group Account Number."}
                            return HttpResponse(json.dumps(data))
                        elif request.POST.get("group_account_number"):
                            try:
                                group = Group.objects.get(name__iexact=request.POST.get("group_name"), account_number=request.POST.get("group_account_number"))
                                if not request.POST.get("group_loan_account_no"):
                                    data = {"error": True, "message1": "Please enter the Group Loan Account Number."}
                                    return HttpResponse(json.dumps(data))
                                else:
                                    try:
                                        loan_account = LoanAccount.objects.get(group=group, account_no=request.POST.get("group_loan_account_no"))
                                        if d(request.POST.get("total_amount")) == d(request.POST.get("amount")):
                                            if d(loan_account.loan_amount) == d(request.POST.get("total_amount")):
                                                try:
                                                    clients_list = group.clients.all()
                                                    if len(clients_list) != 0:
                                                        Payments.objects.create(
                                                            date=date,
                                                            branch=branch,
                                                            voucher_number=voucher_number,
                                                            group=group,
                                                            payment_type=payment_type,
                                                            amount=amount,
                                                            total_amount=total_amount,
                                                            totalamount_in_words=totalamount_in_words
                                                        )
                                                        loan_account.loan_issued_date = datetime.datetime.now().date()
                                                        loan_account.loan_issued_by = request.user
                                                        loan_account.save()
                                                        data = {"error": False}
                                                        return HttpResponse(json.dumps(data))
                                                    else:
                                                        data = {"error": True, "message1": "Group does not contain members inorder to issue Loan."}
                                                        return HttpResponse(json.dumps(data))

                                                except ObjectDoesNotExist:
                                                    data = {"error": True, "message1": "Group does not contain members inorder to issue Loan."}
                                                    return HttpResponse(json.dumps(data))
                                            else:
                                                data = {"error": True, "message1": "Amount is less than applied loan amount."}
                                                return HttpResponse(json.dumps(data))
                                        else:
                                            data = {"error": True, "message1": "Entered total amount is not equal to amount."}
                                            return HttpResponse(json.dumps(data))
                                    except LoanAccount.DoesNotExist:
                                        data = {"error": True, "message1": "Group does not have any Loan with this Loan A/C Number."}
                                        return HttpResponse(json.dumps(data))
                            except Group.DoesNotExist:
                                data = {"error": True, "message1": "Group does not exists with this Name and A/C Number. Please enter correct details."}
                                return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "message1": "Voucher can't be generated with amount/total amount zero"}
                return HttpResponse(json.dumps(data))

        else:
            data = {"error": True, "message": payment_form.errors}
            return HttpResponse(json.dumps(data))


class GeneralLedgerPdfDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        general_ledger_list = general_ledger_function()
        try:
            # template = get_template("pdfgeneral_ledger.html")
            context = Context(
                {'pagesize': 'A4', "list": general_ledger_list,
                 "mediaroot": settings.MEDIA_ROOT})
            return render(request, 'pdfgeneral_ledger.html', context)
            # html = template.render(context)
            # result = StringIO.StringIO()
            # # pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
            # if not pdf.err:
            #     return HttpResponse(result.getvalue(),
            #                         content_type='application/pdf')
            # else:
            #     return HttpResponse('We had some errors')
        except Exception as err:
            errmsg = "%s" % (err)
            return HttpResponse(errmsg)


class DayBookPdfDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        date = kwargs.get("date")
        receipts_list, total_payments, travellingallowance_list, \
            loans_list, paymentofsalary_list, printingcharges_list, \
            stationarycharges_list, othercharges_list, savingswithdrawal_list,\
            recurringwithdrawal_list, fixedwithdrawal_list, total, \
            dict_payments, total_dict, selected_date, grouped_receipts_list, \
            thrift_deposit_sum_list, loanprinciple_amount_sum_list, \
            loaninterest_amount_sum_list, entrancefee_amount_sum_list, \
            membershipfee_amount_sum_list, bookfee_amount_sum_list, \
            loanprocessingfee_amount_sum_list, insurance_amount_sum_list, \
            fixed_deposit_sum_list, recurring_deposit_sum_list, \
            share_capital_amount_sum_list = day_book_function(request, date)

        try:
            # template = get_template("pdf_daybook.html")
            context = Context(
                {"receipts_list": receipts_list, "total_payments": total_payments,
                 "loans_list": loans_list, "selected_date": selected_date,
                 "fixedwithdrawal_list": fixedwithdrawal_list, "total": total,
                 "dict_payments": dict_payments, "dict": total_dict,
                 "travellingallowance_list": travellingallowance_list,
                 "paymentofsalary_list": paymentofsalary_list,
                 "printingcharges_list": printingcharges_list,
                 "stationarycharges_list": stationarycharges_list,
                 "othercharges_list": othercharges_list,
                 "savingswithdrawal_list": savingswithdrawal_list,
                 "recurringwithdrawal_list": recurringwithdrawal_list,
                 "grouped_receipts_list": grouped_receipts_list,
                 "thrift_deposit_sum_list": thrift_deposit_sum_list,
                 "loanprinciple_amount_sum_list": loanprinciple_amount_sum_list,
                 "loaninterest_amount_sum_list": loaninterest_amount_sum_list,
                 "entrancefee_amount_sum_list": entrancefee_amount_sum_list,
                 "membershipfee_amount_sum_list": membershipfee_amount_sum_list,
                 "bookfee_amount_sum_list": bookfee_amount_sum_list,
                 "insurance_amount_sum_list": insurance_amount_sum_list,
                 "share_capital_amount_sum_list": share_capital_amount_sum_list,
                 "recurring_deposit_sum_list": recurring_deposit_sum_list,
                 "fixed_deposit_sum_list": fixed_deposit_sum_list,
                 "loanprocessingfee_amount_sum_list":
                    loanprocessingfee_amount_sum_list
                 }
            )
            return render(request, 'pdf_daybook.html', context)
            # html = template.render(context)
            # result = StringIO.StringIO()
            # # pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
            # if not pdf.err:
            #     return HttpResponse(result.getvalue(),
            #                         content_type='application/pdf')
            # else:
            #     return HttpResponse('We had some errors')
        except Exception as err:
            errmsg = "%s" % (err)
            return HttpResponse(errmsg)


class UserChangePassword(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    template_name = "user_change_password.html"

    def get_form_kwargs(self):
        kwargs = super(UserChangePassword, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data.get("new_password"))
        user.save()
        return JsonResponse({"error": False, "message": "You have changed your password!"})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


@login_required
def getmember_loanaccounts(request):
    if request.method == "POST":
        account_number = request.POST.get("account_number")
        try:
            client = Client.objects.get(account_number=account_number)
            try:
                loan_accounts_list = LoanAccount.objects.filter(client=client)
                data_list = []
                for loan_account in loan_accounts_list:
                    if d(loan_account.total_loan_balance):
                        data_dict = {}
                        data_dict['loan_account_number'] = \
                            loan_account.account_no
                        data_dict['loan_amount'] = \
                            int(loan_account.loan_amount)
                        data_list.append(data_dict)
                    else:
                        continue

                try:
                    group = client.group_set.get()
                    groupname = client.group_set.get().name
                    groupaccountnumber = client.group_set.get().account_number

                    try:
                        loan_accounts_list = LoanAccount.objects.filter(
                            group=group)
                        grouploanlist = []
                        for loan_account in loan_accounts_list:
                            if d(loan_account.total_loan_balance):
                                data_dict = {}
                                data_dict['loan_account_number'] = \
                                    loan_account.account_no
                                data_dict['loan_amount'] = \
                                    int(loan_account.loan_amount)
                                grouploanlist.append(data_dict)
                            else:
                                continue
                        data = {
                            "error": False, "list": data_list,
                            "grouploanlist": grouploanlist,
                            "groupname": groupname,
                            "groupaccountnumber": groupaccountnumber
                        }
                    except Exception:
                        data = {
                            "error": False, "list": data_list,
                            "groupname": groupname,
                            "groupaccountnumber": groupaccountnumber
                        }
                except ObjectDoesNotExist:
                    data = {"error": False, "list": data_list}
            except Exception:
                data = {"error": False}
        except Client.DoesNotExist:
            data = {
                "error": True,
                "message1": "No Member exists with this Account Number."
            }
    else:
        data = {"error": False}
    return HttpResponse(json.dumps(data))


@login_required
def getloan_demands(request):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(
            account_no=request.POST.get("loan_account_no"))
        if loan_account.status == "Approved":
            if (
                d(loan_account.total_loan_balance) or
                d(loan_account.interest_charged) or
                d(loan_account.loan_repayment_amount) or
                d(loan_account.principle_repayment)
            ):
                demand_loanprinciple = str(loan_account.principle_repayment)
                demand_loaninterest = str(loan_account.interest_charged)
                data = {
                    "error": False,
                    "demand_loanprinciple": demand_loanprinciple,
                    "demand_loaninterest": demand_loaninterest
                }
            else:
                data = {
                    "error": True,
                    "message1": "Loan has been cleared sucessfully."
                }
        else:
            data = {
                "error": True,
                "message1": "Member Loan is under pending for approval."
            }
        return HttpResponse(json.dumps(data))

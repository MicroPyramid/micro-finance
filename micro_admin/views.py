from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.contrib.auth import login, authenticate, logout
import json
from django.contrib.auth.models import Permission
from micro_admin.models import (
    User, Branch, Group, Client, CLIENT_ROLES, GroupMeetings, SavingsAccount,
    LoanAccount, Receipts, FixedDeposits, PAYMENT_TYPES, Payments,
    RecurringDeposits, USER_ROLES)
from micro_admin.forms import (
    BranchForm, UserForm, GroupForm, ClientForm, AddMemberForm,
    SavingsAccountForm, LoanAccountForm, ReceiptForm, FixedDepositForm,
    PaymentForm, ReccuringDepositForm)
from django.contrib.auth.decorators import login_required
import datetime
import decimal
from django.conf import settings
import csv
from django.utils.encoding import smart_str
import xlwt
# from xhtml2pdf import pisa
# from django.template.loader import get_template
# import cStringIO as StringIO
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from weasyprint import HTML

from django.views.generic.edit import CreateView, UpdateView, \
    View
from django.views.generic import ListView, DetailView, \
    FormView, RedirectView
from django.http import JsonResponse
from micro_admin.mixins import UserPermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

d = decimal.Decimal


def index(request):
    if request.user.is_authenticated():
        return render(request, "index.html", {"user": request.user})
    data = {}
    data.update(csrf(request))
    return render_to_response("login.html", data)


class LoginView(View):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                data = {"error": False, "message": "Loggedin Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "message": "User is not active."}
                return JsonResponse(data)
        else:
            data = {
                "error": True,
                "message": "Username and Password were incorrect."
            }
            return JsonResponse(data)

        return render(request, "index.html")

    def get(self, request):
        if request.user.is_authenticated():
            return render(request, 'index.html', {'user': request.user})
        data = {}
        data.update(csrf(request))
        return render_to_response("login.html", data)


class LogoutView(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


# --------------------------------------------------- #
# Branch Model class Based View #
class CreateBranchView(LoginRequiredMixin, CreateView):
    login_url = '/'
    redirect_field_name = 'next'
    form_class = BranchForm
    template_name = "branch/create.html"

    def form_valid(self, form):
        branch = form.save()
        data = {"error": False, "branch_id": branch.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "message": form.errors}
        return JsonResponse(data)


class UpdateBranchView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = 'next'
    pk = 'pk'
    model = Branch
    form_class = BranchForm
    template_name = "branch/edit.html"

    def form_valid(self, form):
        branch = form.save()
        data = {"error": False, "branch_id": branch.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "message": form.errors}
        return JsonResponse(data)


class BranchProfileView(LoginRequiredMixin, DetailView):
    login_url = '/'
    redirect_field_name = 'next'
    model = Branch
    pk = 'pk'
    template_name = "branch/view.html"


class BranchListView(LoginRequiredMixin, ListView):
    login_url = '/'
    redirect_field_name = 'next'
    model = Branch
    template_name = "branch/list.html"


class BranchInactiveView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = 'next'

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
    login_url = '/'
    redirect_field_name = 'next'
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
        data = {"error": False, "client_id": client.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "message": form.errors}
        return JsonResponse(data)


class ClienProfileView(LoginRequiredMixin, DetailView):
    login_url = '/'
    redirect_field_name = 'next'
    pk = 'pk'
    model = Client
    template_name = "client/profile.html"


class UpdateClientView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = 'next'
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
        data = {"error": False, "client_id": client.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "message": form.errors}
        return JsonResponse(data)


@login_required
def update_clientprofile(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if not (request.user.is_admin or request.user.branch == client.branch):
        return HttpResponseRedirect(
            reverse('micro_admin:clientprofile', kwargs={
                    'client_id': client_id}))

    if request.method == "GET":
        return render(
            request, "client/update-profile.html", {"client": client})
    else:
        if (
            request.FILES and request.FILES.get("photo") and
            request.FILES.get("signature")
        ):
            client.photo = request.FILES.get("photo")
            client.signature = request.FILES.get("signature")
            client.save()
        return HttpResponseRedirect(
            reverse('micro_admin:clientprofile', kwargs={
                    'client_id': client_id}))


class ClientsListView(LoginRequiredMixin, ListView):
    login_url = '/'
    redirect_field_name = 'next'
    model = Client
    template_name = "client/list.html"


class ClientInactiveView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = 'next'

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
    login_url = '/'
    redirect_field_name = 'next'
    form_class = UserForm
    template_name = "user/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateUserView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['userroles'] = dict(USER_ROLES).keys()
        return context

    def form_valid(self, form):
        user = form.save()
        data = {"error": False, "user_id": user.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "message": form.errors}
        return JsonResponse(data)


class UpdateUserView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = 'next'
    pk = 'pk'
    model = User
    form_class = UserForm
    context_object_name = 'selecteduser'
    template_name = "user/edit.html"

    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.kwargs.get('pk'))
        data = request.POST.copy()
        data['password'] = user.password
        request.POST = data
        return super(UpdateUserView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data(**kwargs)
        context['branch'] = Branch.objects.all()
        context['userroles'] = dict(USER_ROLES).keys()
        return context

    def form_valid(self, form):
        user = form.save()
        data = {"error": False, "user_id": user.id}
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {"error": True, "message": form.errors}
        return JsonResponse(data)


class UserProfileView(LoginRequiredMixin, DetailView):
    login_url = '/'
    redirect_field_name = 'next'
    pk = 'pk'
    model = User
    context_object_name = 'selecteduser'
    template_name = "user/profile.html"


class UsersListView(LoginRequiredMixin, ListView):
    login_url = '/'
    redirect_field_name = 'next'
    model = User
    template_name = "user/list.html"
    context_object_name = 'list_of_users'

    def get_queryset(self):
        return User.objects.filter(is_admin=0)


class UserInactiveView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = 'next'

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
        return JsonResponse({"error": False, "group_id": group.id})

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
        group_mettings = GroupMeetings.objects.filter(
            group_id=self.object.id).order_by('-id')

        context["clients_list"] = clients_list
        context["clients_count"] = len(clients_list)
        context["latest_group_meeting"] = \
            group_mettings.first() if group_mettings else None
        return context


@login_required
def assign_staff_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not(request.user.is_admin or request.user.branch == group.branch):
        return HttpResponseRedirect(
            reverse('micro_admin:groupprofile', kwargs={'group_id': group_id}))

    if request.method == "GET":
        return render(
            request, "group/assign_staff.html", {
                "group": group,
                "users_list": User.objects.filter(is_admin=0)
            })
    else:
        if request.POST.get("staff"):
            group.staff = get_object_or_404(
                User, id=request.POST.get("staff"))
            group.save()
            data = {"error": False, "group_id": group.id}
        else:
            data = {"error": True,
                    "message": {"staff": "This field is required"}}
        return HttpResponse(json.dumps(data))


@login_required
def addmembers_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not(request.user.is_admin or request.user.branch == group.branch):
        return HttpResponseRedirect(
            reverse('micro_admin:groupprofile', kwargs={'group_id': group_id}))

    if request.method == "GET":
        clients_list = Client.objects.filter(status="UnAssigned", is_active=1)
        return render(
            request, "group/add_member.html",
            {"group": group, "clients_list": clients_list})
    else:
        addmember_form = AddMemberForm(request.POST)
        if addmember_form.is_valid():
            client_ids = request.POST.getlist("clients")
            for client_id in client_ids:
                try:
                    client = Client.objects.get(
                        id=client_id, status="UnAssigned", is_active=1)
                except Client.DoesNotExist:
                    continue
                else:
                    group.clients.add(client)
                    group.save()
                    client.status = "Assigned"
                    client.save()
            data = {"error": False, "group_id": group.id}
        else:
            data = {"error": True, "message": addmember_form.errors}
        return HttpResponse(json.dumps(data))


@login_required
def viewmembers_under_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    clients_list = group.clients.all()
    return render(
        request, "group/view-members.html",
        {
            "group": group, "clients_list": clients_list,
            "clients_count": len(clients_list)
        }
    )


@login_required
def groups_list(request):
    groups_list = Group.objects.all() \
        .select_related("staff", "branch").prefetch_related("clients")
    return render(request, "group/list.html", {"groups_list": groups_list})


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if (
        request.user.is_admin or
        (request.user.has_perm("branch_manager") and
         request.user.branch == group.branch)
    ):
        if (
            LoanAccount.objects.filter(
                group=group, status="Approved"
            ).exclude(
                total_loan_balance=0
            ).count() or not group.is_active
        ):
            pass
        else:
            group.is_active = 0
            group.save()
    return HttpResponseRedirect(reverse('micro_admin:groupslist'))


@login_required
def removemembers_from_group(request, group_id, client_id):
    group = get_object_or_404(Group, id=group_id)
    if (
        request.user.is_admin or
        (request.user.has_perm("branch_manager") and
         request.user.branch == group.branch)
    ):
        client = get_object_or_404(Client, id=client_id)
        group.clients.remove(client)
        group.save()
        client.status = "UnAssigned"
        client.save()
    return HttpResponseRedirect(
        reverse('micro_admin:groupprofile', kwargs={'group_id': group_id}))


@login_required
def group_meetings(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return HttpResponse("List of Group #%s Meetings" % group.id)


@login_required
def add_group_meeting(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "GET":
        group_meetings = GroupMeetings.objects.filter(
            group_id=group.id).order_by('-id')
        return render(
            request, "group/add_group_meeting.html",
            {
                "group": group,
                "latest_group_meeting":
                    group_meetings.first() if group_meetings else None
            }
        )
    else:
        datestring_format = datetime.datetime.strptime(
            request.POST.get("meeting_date"), '%m/%d/%Y').strftime('%Y-%m-%d')
        meeting_date = datetime.datetime.strptime(
            datestring_format, "%Y-%m-%d")
        meeting_time = request.POST.get("meeting_time")
        GroupMeetings.objects.create(meeting_date=meeting_date,
                                     meeting_time=meeting_time,
                                     group=group)
        return HttpResponseRedirect(
            reverse('micro_admin:groupprofile', kwargs={'group_id': group_id}))


@login_required
def client_savings_application(request, client_id):
    if request.method == "GET":
        client = Client.objects.get(id=client_id)
        count = SavingsAccount.objects.filter(client=client).count()
        if count == 1:
            return HttpResponseRedirect(
                reverse("micro_admin:clientsavingsaccount", kwargs={
                    'client_id': client_id}))
        else:
            count = SavingsAccount.objects.all().count()
            account_no = "%s%s%d" % ("S", client.branch.id, count + 1)
            return render(
                request, "client/savings/application.html",
                {"client": client, "account_no": account_no})
    else:
        form = SavingsAccountForm(request.POST)
        if form.is_valid():
            obj_sav_acc = form.save(commit=False)
            obj_sav_acc.status = "Applied"
            obj_sav_acc.created_by = User.objects.get(username=request.user)
            obj_sav_acc.client = Client.objects.get(id=client_id)
            obj_sav_acc.save()
            data = {"error": False, "client_id": obj_sav_acc.client.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_savings_account(request, client_id):
    client = Client.objects.get(id=client_id)
    savingsaccount = SavingsAccount.objects.get(client=client)
    return render(
        request, "client/savings/account.html",
        {"client": client, "savingsaccount": savingsaccount})


@login_required
def group_savings_application(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        count = SavingsAccount.objects.filter(group=group).count()
        if count == 1:
            return HttpResponseRedirect(reverse(
                "micro_admin:groupsavingsaccount",
                kwargs={'group_id': group_id}))
        else:
            count = SavingsAccount.objects.all().count()
            account_no = "%s%s%d" % ("S", group.branch.id, count + 1)
            return render(
                request, "group/savings/application.html",
                {"group": group, "account_no": account_no})
    else:
        group_savingsaccount_form = SavingsAccountForm(request.POST)
        if group_savingsaccount_form.is_valid():
            obj_sav_acc = group_savingsaccount_form.save(commit=False)
            obj_sav_acc.status = "Applied"
            obj_sav_acc.created_by = User.objects.get(username=request.user)
            obj_sav_acc.group = Group.objects.get(id=group_id)
            obj_sav_acc.save()
            data = {"error": False, "group_id": obj_sav_acc.group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": group_savingsaccount_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def group_savings_account(request, group_id):
    group = Group.objects.get(id=group_id)
    savings_account = SavingsAccount.objects.get(group=group)
    clients_list = group.clients.all()
    sharecapital_amount = 0
    entrancefee_amount = 0
    membershipfee_amount = 0
    bookfee_amount = 0
    insurance_amount = 0
    for client in clients_list:
        sharecapital_amount += client.sharecapital_amount
        entrancefee_amount += client.entrancefee_amount
        membershipfee_amount += client.membershipfee_amount
        bookfee_amount += client.bookfee_amount
        insurance_amount += client.insurance_amount
    group_totals_dict = {}
    group_totals_dict["sharecapital_amount"] = sharecapital_amount
    group_totals_dict["entrancefee_amount"] = entrancefee_amount
    group_totals_dict["membershipfee_amount"] = membershipfee_amount
    group_totals_dict["bookfee_amount"] = bookfee_amount
    group_totals_dict["insurance_amount"] = insurance_amount
    return render(request, "group/savings/account.html",
                  {"group": group, "savings_account": savings_account,
                   "dict": group_totals_dict})


@login_required
def change_savings_account_status(request, savingsaccount_id):
    if request.method == "POST":
        savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
        if savings_account.group:
            if (
                request.user.is_admin or
                (request.user.has_perm("branch_manager") and
                 request.user.branch == savings_account.group.branch)
            ):
                savings_account.status = request.GET.get("status")
                savings_account.save()
                data = {"error": False, "group_id": savings_account.group.id}
            else:
                data = {
                    "error": True,
                    "errmsg": "You don't have permission to " +
                              request.GET.get("status") + " savings account.",
                    "group_id": savings_account.group.id
                }
            return HttpResponse(json.dumps(data))
        elif savings_account.client:
            if (
                request.user.is_admin or
                (request.user.has_perm("branch_manager") and
                 request.user.branch == savings_account.client.branch)
            ):
                savings_account.status = request.GET.get("status")
                savings_account.save()
                data = {"error": False, "client_id": savings_account.client.id}
            else:
                data = {
                    "error": True,
                    "errmsg": "You don't have permission to " +
                              request.GET.get("status") + " savings account.",
                    "client_id": savings_account.client.id
                }
            return HttpResponse(json.dumps(data))


@login_required
def group_loan_application(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        count = LoanAccount.objects.all().count()
        account_no = "%s%s%d" % ("L", group.branch.id, count + 1)
        return render(
            request, "group/loan/application.html",
            {"group": group, "account_no": account_no})
    else:
        group_loanaccount_form = LoanAccountForm(request.POST)
        if group_loanaccount_form.is_valid():
            group = Group.objects.get(id=group_id)
            loan_account = group_loanaccount_form.save(commit=False)
            loan_account.status = "Applied"
            loan_account.created_by = User.objects.get(username=request.user)
            loan_account.group = group

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
            data = {"error": False, "loanaccount_id": loan_account.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": group_loanaccount_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_loan_application(request, client_id):
    if request.method == "GET":
        client = Client.objects.get(id=client_id)
        count = LoanAccount.objects.all().count()
        account_no = "%s%s%d" % ("L", client.branch.id, count + 1)
        return render(
            request, "client/loan/application.html",
            {"client": client, "account_no": account_no})
    else:
        form = LoanAccountForm(request.POST)
        if form.is_valid():
            loan_account = form.save(commit=False)
            loan_account.status = "Applied"
            loan_account.created_by = User.objects.get(username=request.user)
            loan_account.client = Client.objects.get(id=client_id)
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
            data = {"error": False, "loanaccount_id": loan_account.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_loan_account(request, loanaccount_id):
    loanaccount = LoanAccount.objects.get(id=loanaccount_id)
    return render(
        request, "client/loan/account.html",
        {"client": loanaccount.client, "loanaccount": loanaccount})


@login_required
def group_loan_account(request, loanaccount_id):
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    return render(
        request, "group/loan/account.html",
        {"group": loan_account.group, "loan_account": loan_account})


@login_required
def change_loan_account_status(request, loanaccount_id):
    if request.method == "POST":
        try:
            loan_account = LoanAccount.objects.get(id=loanaccount_id)
            if loan_account.group:
                branchid = loan_account.group.branch.id
            elif loan_account.client:
                branchid = loan_account.client.branch.id
            if (
                request.user.is_admin or
                (request.user.has_perm("branch_manager") and
                 request.user.branch.id == branchid)
            ):
                loan_account.status = request.GET.get("status")
                loan_account.approved_date = datetime.datetime.now()
                loan_account.save()
                data = {"error": False, "loanaccount_id": loan_account.id}
            else:
                data = {"error": True, "loanaccount_id": loan_account.id}
            return HttpResponse(json.dumps(data))
        except LoanAccount.DoesNotExist:
            data = {"error": True}
            return HttpResponse(json.dumps(data))


@login_required
def view_grouploan_deposits(request, group_id, loanaccount_id):
    group = Group.objects.get(id=group_id)
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    receipts_list = Receipts.objects.filter(
        group=group, group_loan_account=loan_account
    ).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    count = Receipts.objects.filter(
        group=group, group_loan_account=loan_account
    ).exclude(demand_loanprinciple_amount_atinstant=0,
              demand_loaninterest_amount_atinstant=0).count()
    return render(
        request, "group/loan/list_of_loan_deposits.html",
        {"loan_account": loan_account, "receipts_list": receipts_list,
         "group": group, "count": count}
    )


@login_required
def view_groupsavings_deposits(request, group_id):
    group = Group.objects.get(id=group_id)
    savings_account = SavingsAccount.objects.get(group=group)
    receipts_list = Receipts.objects.filter(group=group).exclude(
        savingsdeposit_thrift_amount=0)
    count = Receipts.objects.filter(group=group).exclude(
        savingsdeposit_thrift_amount=0
    ).count()
    return render(
        request,
        "group/savings/list_of_savings_deposits.html",
        {
            "savings_account": savings_account,
            "receipts_list": receipts_list,
            "group": group,
            "count": count
        }
    )


@login_required
def view_groupsavings_withdrawals(request, group_id):
    group = Group.objects.get(id=group_id)
    savings_withdrawals_list = Payments.objects.filter(
        group=group, payment_type="SavingsWithdrawal")
    count = Payments.objects.filter(
        group=group, payment_type="SavingsWithdrawal").count()
    return render(request, "group/savings/list_of_savings_withdrawals.html",
                  {"count": count, "group": group,
                   "savings_withdrawals_list": savings_withdrawals_list})


@login_required
def listofclient_loan_deposits(request, client_id, loanaccount_id):
    client = Client.objects.get(id=client_id)
    loanaccount = LoanAccount.objects.get(id=loanaccount_id)
    receipts_lists = Receipts.objects.filter(
        client=client, member_loan_account=loanaccount
    ).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    return render(
        request, "client/loan/view_loan_deposits.html",
        {"loanaccount": loanaccount, "receipts_lists": receipts_lists})


@login_required
def listofclient_savings_deposits(request, client_id):
    savingsaccount = SavingsAccount.objects.get(client=client_id)
    receipts_lists = Receipts.objects.filter(
        client=client_id).exclude(savingsdeposit_thrift_amount=0)
    return render(
        request, "client/savings/list_of_savings_deposits.html",
        {"savingsaccount": savingsaccount, "receipts_lists": receipts_lists})


@login_required
def listofclient_savings_withdrawals(request, client_id):
    client = Client.objects.get(id=client_id)
    savings_withdrawals_list = Payments.objects.filter(
        client=client, payment_type="SavingsWithdrawal")
    count = Payments.objects.filter(client=client,
                                    payment_type="SavingsWithdrawal").count()
    return render(
        request, "client/savings/list_of_savings_withdrawals.html",
        {"count": count, "savings_withdrawals_list": savings_withdrawals_list,
         "client": client}
    )


@login_required
def issue_loan(request, loanaccount_id):
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    if loan_account.group:
        loan_account.loan_issued_date = datetime.datetime.now()
        loan_account.loan_issued_by = request.user
        loan_account.save()
        loanaccount_id = str(loan_account.id)
        return HttpResponseRedirect(reverse(
            "micro_admin:grouploanaccount",
            kwargs={"loanaccount_id": loanaccount_id}))
    elif loan_account.client:
        loan_account.loan_issued_date = datetime.datetime.now()
        loan_account.loan_issued_by = request.user
        loan_account.save()
        loanaccount_id = str(loan_account.id)
        return HttpResponseRedirect(reverse(
            "micro_admin:clientloanaccount",
            kwargs={'loanaccount_id': loanaccount_id}))


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


def receipts_list(request):
    receipt_list = Receipts.objects.all().order_by("-id")
    return render(request, "listof_receipts.html",
                  {"receipt_list": receipt_list})


def ledger_account(request, client_id, loanaccount_id):
    client = Client.objects.get(id=client_id)
    loanaccount = LoanAccount.objects.get(id=loanaccount_id)
    receipts_list = Receipts.objects.filter(
        client=client_id, member_loan_account=loanaccount
    ).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    return render(
        request, "client/loan/client_ledger_account.html",
        {"loanaccount": loanaccount, "receipts_list": receipts_list,
         "client": client}
    )


def general_ledger_function(request):
    query_set = Receipts.objects.all()
    query_set.query.group_by = ["date"]
    grouped_receipts_list = []
    for i in query_set:
        grouped_receipts_list.append(i)
    general_ledger_list = []
    for objreceipt in grouped_receipts_list:
        sum_sharecapital_amount = 0
        sum_entrancefee_amount = 0
        sum_membershipfee_amount = 0
        sum_bookfee_amount = 0
        sum_loanprocessingfee_amount = 0
        sum_savingsdeposit_thrift_amount = 0
        sum_fixeddeposit_amount = 0
        sum_recurringdeposit_amount = 0
        sum_loanprinciple_amount = 0
        sum_loaninterest_amount = 0
        sum_insurance_amount = 0
        total_sum = 0

        receipts_list = Receipts.objects.filter(date=objreceipt.date)
        data = {}
        data["date"] = objreceipt.date
        for receipt in receipts_list:
            sum_sharecapital_amount += d(receipt.sharecapital_amount)
            sum_entrancefee_amount += d(receipt.entrancefee_amount)
            sum_membershipfee_amount += d(receipt.membershipfee_amount)
            sum_bookfee_amount += d(receipt.bookfee_amount)
            sum_loanprocessingfee_amount += d(receipt.loanprocessingfee_amount)
            sum_savingsdeposit_thrift_amount += d(
                receipt.savingsdeposit_thrift_amount)
            sum_fixeddeposit_amount += d(receipt.fixeddeposit_amount)
            sum_recurringdeposit_amount += d(receipt.recurringdeposit_amount)
            sum_loanprinciple_amount += d(receipt.loanprinciple_amount)
            sum_loaninterest_amount += d(receipt.loaninterest_amount)
            sum_insurance_amount += d(receipt.insurance_amount)

        data["sum_sharecapital_amount"] = d(sum_sharecapital_amount)
        data["sum_entrancefee_amount"] = d(sum_entrancefee_amount)
        data["sum_membershipfee_amount"] = d(sum_membershipfee_amount)
        data["sum_bookfee_amount"] = d(sum_bookfee_amount)
        data["sum_loanprocessingfee_amount"] = d(sum_loanprocessingfee_amount)
        data["sum_savingsdeposit_thrift_amount"] = d(
            sum_savingsdeposit_thrift_amount)
        data["sum_fixeddeposit_amount"] = d(sum_fixeddeposit_amount)
        data["sum_recurringdeposit_amount"] = d(sum_recurringdeposit_amount)
        data["sum_loanprinciple_amount"] = d(sum_loanprinciple_amount)
        data["sum_loaninterest_amount"] = d(sum_loaninterest_amount)
        data["sum_insurance_amount"] = d(sum_insurance_amount)
        for key in data:
            if key != "date":
                total_sum += data[key]
        data["total_sum"] = total_sum
        general_ledger_list.append(data)
    return general_ledger_list


@login_required
def general_ledger(request):
    general_ledger_list = general_ledger_function(request)
    return render(request, "generalledger.html", {"list": general_ledger_list})


@login_required
def fixed_deposits(request):
    if request.method == "GET":
        data = {}
        data.update(csrf(request))
        return render(
            request, "client/fixed-deposits/fixed_deposit_application.html", {"data": data})
    else:
        try:
            client = Client.objects.get(
                first_name__iexact=request.POST.get("client_name"),
                account_number=request.POST.get("client_account_no"))
            form = FixedDepositForm(request.POST, request.FILES)
            if form.is_valid():
                fixed_deposit = form.save(commit=False)
                fixed_deposit.status = "Opened"
                fixed_deposit.client = client
                interest_charged = d(
                    (
                        (
                            d(fixed_deposit.fixed_deposit_amount) *
                            (d(fixed_deposit.fixed_deposit_interest_rate) / 12)
                        ) / 100
                    )
                )
                fixed_deposit_interest_charged = d(
                    d(interest_charged) * d(fixed_deposit.fixed_deposit_period)
                )
                fixed_deposit.maturity_amount = d(
                    d(fixed_deposit.fixed_deposit_amount) + d(
                        fixed_deposit_interest_charged)
                )
                fixed_deposit.fixed_deposit_interest = d(
                    d(fixed_deposit.maturity_amount) - d(
                        fixed_deposit.fixed_deposit_amount)
                )
                fixed_deposit.save()
                data = {"error": False, "fixed_deposit_id": fixed_deposit.id}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "message": form.errors}
                return HttpResponse(json.dumps(data))

        except Client.DoesNotExist:
            data = {
                "error": True,
                "messagememerr": "No Member exist with this " +
                                 "First Name and Account Number."
            }
            return HttpResponse(json.dumps(data))


@login_required
def client_fixed_deposits_profile(request, fixed_deposit_id):
    fixed_deposit = FixedDeposits.objects.get(id=fixed_deposit_id)
    return render(
        request, "client/fixed-deposits/fixed_deposits_profile.html",
        {"fixed_deposit": fixed_deposit}
    )


@login_required
def view_client_fixed_deposits(request):
    fixed_deposit_list = FixedDeposits.objects.all().order_by("-id")
    return render(
        request, "client/fixed-deposits/view_fixed_deposits.html",
        {"fixed_deposit_list": fixed_deposit_list}
    )


@login_required
def view_particular_client_fixed_deposits(request, client_id):
    client = Client.objects.get(id=client_id)
    fixed_deposit_list = FixedDeposits.objects.filter(
        client=client_id).order_by("-id")
    return render(
        request, "client/fixed-deposits/view_fixed_deposits.html",
        {"fixed_deposit_list": fixed_deposit_list, "client": client}
    )


@login_required
def client_recurring_deposits_profile(request, recurring_deposit_id):
    recurring_deposit = RecurringDeposits.objects.get(id=recurring_deposit_id)
    return render(
        request, "client/recurring-deposits/recurring_deposit_profile.html",
        {"recurring_deposit": recurring_deposit}
    )


@login_required
def view_client_recurring_deposits(request):
    recurring_deposit_list = RecurringDeposits.objects.all().order_by("-id")
    return render(
        request, "client/recurring-deposits/view_recurring_deposits.html",
        {"recurring_deposit_list": recurring_deposit_list}
    )


@login_required
def view_particular_client_recurring_deposits(request, client_id):
    client = Client.objects.get(id=client_id)
    recurring_deposit_list = RecurringDeposits.objects.filter(
        client=client_id).order_by("-id")
    return render(
        request, "client/recurring-deposits/view_recurring_deposits.html",
        {"recurring_deposit_list": recurring_deposit_list, "client": client}
    )


def get_receipts_list(receipts_list, receipt, value):
    if value > 0:
        receipts_list.append(receipt)
    return receipts_list


@login_required
def day_book_function(request, date):
    selected_date = date
    query_set = Receipts.objects.filter(date=selected_date)

    query_set.query.group_by = ["group_id"]

    grouped_receipts_list = []
    receipts_list = []

    for i in query_set:
        grouped_receipts_list.append(i.group_id)

    thrift_deposit_sum_list = []
    loanprinciple_amount_sum_list = []
    loaninterest_amount_sum_list = []
    entrancefee_amount_sum_list = []
    membershipfee_amount_sum_list = []
    bookfee_amount_sum_list = []
    loanprocessingfee_amount_sum_list = []
    insurance_amount_sum_list = []
    fixed_deposit_sum_list = []
    recurring_deposit_sum_list = []
    share_capital_amount_sum_list = []

    for group_id in grouped_receipts_list:
        if group_id:
            receipts_list = Receipts.objects.filter(
                group=group_id, date=selected_date)
            thrift_deposit_sum = 0
            loanprinciple_amount_sum = 0
            loaninterest_amount_sum = 0
            entrancefee_amount_sum = 0
            membershipfee_amount_sum = 0
            bookfee_amount_sum = 0
            loanprocessingfee_amount_sum = 0
            insurance_amount_sum = 0
            fixed_deposit_sum = 0
            recurring_deposit_sum = 0
            share_capital_amount_sum = 0

            thrift_deposit_receipts_list = []
            loanprinciple_receipts_list = []
            loaninterest_receipts_list = []
            entrancefee_receipts_list = []
            membershipfee_receipts_list = []
            bookfee_receipts_list = []
            loanprocessingfee_receipts_list = []
            insurance_receipts_list = []
            fixed_deposit_receipts_list = []
            recurring_deposit_receipts_list = []
            share_capital_receipts_list = []

            for receipt in receipts_list:
                thrift_deposit_receipts_list = get_receipts_list(
                    thrift_deposit_receipts_list, receipt,
                    receipt.savingsdeposit_thrift_amount)
                loanprinciple_receipts_list = get_receipts_list(
                    loanprinciple_receipts_list, receipt,
                    receipt.loanprinciple_amount)
                loaninterest_receipts_list = get_receipts_list(
                    loaninterest_receipts_list, receipt,
                    receipt.loaninterest_amount)
                entrancefee_receipts_list = get_receipts_list(
                    entrancefee_receipts_list, receipt,
                    receipt.entrancefee_amount)
                membershipfee_receipts_list = get_receipts_list(
                    membershipfee_receipts_list, receipt,
                    receipt.membershipfee_amount)
                bookfee_receipts_list = get_receipts_list(
                    bookfee_receipts_list, receipt, receipt.bookfee_amount)
                loanprocessingfee_receipts_list = get_receipts_list(
                    loanprocessingfee_receipts_list, receipt,
                    receipt.loanprocessingfee_amount)
                insurance_receipts_list = get_receipts_list(
                    insurance_receipts_list, receipt, receipt.insurance_amount)
                fixed_deposit_receipts_list = get_receipts_list(
                    fixed_deposit_receipts_list, receipt,
                    receipt.fixeddeposit_amount)
                recurring_deposit_receipts_list = get_receipts_list(
                    recurring_deposit_receipts_list, receipt,
                    receipt.recurringdeposit_amount)
                share_capital_receipts_list = get_receipts_list(
                    share_capital_receipts_list, receipt,
                    receipt.sharecapital_amount)

                thrift_deposit_sum += d(receipt.savingsdeposit_thrift_amount)
                loanprinciple_amount_sum += d(receipt.loanprinciple_amount)
                loaninterest_amount_sum += d(receipt.loaninterest_amount)
                entrancefee_amount_sum += d(receipt.entrancefee_amount)
                membershipfee_amount_sum += d(receipt.membershipfee_amount)
                bookfee_amount_sum += d(receipt.bookfee_amount)
                loanprocessingfee_amount_sum += d(
                    receipt.loanprocessingfee_amount)
                insurance_amount_sum += d(receipt.insurance_amount)
                fixed_deposit_sum += d(receipt.fixeddeposit_amount)
                recurring_deposit_sum += d(receipt.recurringdeposit_amount)
                share_capital_amount_sum += d(receipt.sharecapital_amount)

            group = Group.objects.get(id=group_id)
            share_capital_amount_sum_dict = {}
            share_capital_amount_sum_dict["group_name"] = group.name
            share_capital_amount_sum_dict["receipt_number"] = \
                share_capital_receipts_list
            share_capital_amount_sum_dict["share_capital_amount_sum"] = \
                share_capital_amount_sum
            share_capital_amount_sum_dict["account_number"] = \
                group.account_number
            share_capital_amount_sum_list.append(share_capital_amount_sum_dict)
            recurring_deposit_sum_dict = {}
            recurring_deposit_sum_dict["group_name"] = group.name
            recurring_deposit_sum_dict["receipt_number"] = \
                recurring_deposit_receipts_list
            recurring_deposit_sum_dict["recurring_deposit_sum"] = \
                recurring_deposit_sum
            recurring_deposit_sum_dict["account_number"] = group.account_number
            recurring_deposit_sum_list.append(recurring_deposit_sum_dict)
            fixed_deposit_sum_dict = {}
            fixed_deposit_sum_dict["group_name"] = group.name
            fixed_deposit_sum_dict["receipt_number"] = \
                fixed_deposit_receipts_list
            fixed_deposit_sum_dict["fixed_deposit_sum"] = fixed_deposit_sum
            fixed_deposit_sum_dict["account_number"] = group.account_number
            fixed_deposit_sum_list.append(fixed_deposit_sum_dict)
            thrift_deposit_sum_dict = {}
            thrift_deposit_sum_dict["group_name"] = group.name
            thrift_deposit_sum_dict["receipt_number"] = \
                thrift_deposit_receipts_list
            thrift_deposit_sum_dict["thrift_deposit_sum"] = thrift_deposit_sum
            thrift_deposit_sum_dict["account_number"] = group.account_number
            thrift_deposit_sum_list.append(thrift_deposit_sum_dict)
            loanprinciple_amount_sum_dict = {}
            loanprinciple_amount_sum_dict["group_name"] = group.name
            loanprinciple_amount_sum_dict["group_id"] = group.id
            loanprinciple_amount_sum_dict["receipt_number"] = \
                loanprinciple_receipts_list
            loanprinciple_amount_sum_dict["loanprinciple_amount_sum"] = \
                loanprinciple_amount_sum
            loanprinciple_amount_sum_dict["account_number"] = \
                group.account_number
            loanprinciple_amount_sum_list.append(loanprinciple_amount_sum_dict)
            loaninterest_amount_sum_dict = {}
            loaninterest_amount_sum_dict["group_name"] = group.name
            loaninterest_amount_sum_dict["group_id"] = group.id
            loaninterest_amount_sum_dict["receipt_number"] = \
                loaninterest_receipts_list
            loaninterest_amount_sum_dict["loaninterest_amount_sum"] = \
                loaninterest_amount_sum
            loaninterest_amount_sum_dict["account_number"] = \
                group.account_number
            loaninterest_amount_sum_list.append(loaninterest_amount_sum_dict)
            entrancefee_amount_sum_dict = {}
            entrancefee_amount_sum_dict["group_name"] = group.name
            entrancefee_amount_sum_dict["group_id"] = group.id
            entrancefee_amount_sum_dict["receipt_number"] = \
                entrancefee_receipts_list
            entrancefee_amount_sum_dict["entrancefee_amount_sum"] = \
                entrancefee_amount_sum
            entrancefee_amount_sum_dict["account_number"] = \
                group.account_number
            entrancefee_amount_sum_list.append(entrancefee_amount_sum_dict)
            membershipfee_amount_sum_dict = {}
            membershipfee_amount_sum_dict["group_name"] = group.name
            membershipfee_amount_sum_dict["group_id"] = group.id
            membershipfee_amount_sum_dict["receipt_number"] = \
                membershipfee_receipts_list
            membershipfee_amount_sum_dict["membershipfee_amount_sum"] = \
                membershipfee_amount_sum
            membershipfee_amount_sum_dict["account_number"] = \
                group.account_number
            membershipfee_amount_sum_list.append(membershipfee_amount_sum_dict)
            bookfee_amount_sum_dict = {}
            bookfee_amount_sum_dict["group_name"] = group.name
            bookfee_amount_sum_dict["group_id"] = group.id
            bookfee_amount_sum_dict["receipt_number"] = bookfee_receipts_list
            bookfee_amount_sum_dict["bookfee_amount_sum"] = bookfee_amount_sum
            bookfee_amount_sum_dict["account_number"] = group.account_number
            bookfee_amount_sum_list.append(bookfee_amount_sum_dict)
            loanprocessingfee_sum_dict = {}
            loanprocessingfee_sum_dict["group_name"] = group.name
            loanprocessingfee_sum_dict["group_id"] = group.id
            loanprocessingfee_sum_dict["receipt_number"] = \
                loanprocessingfee_receipts_list
            loanprocessingfee_sum_dict["loanprocessingfee_amount_sum"] = \
                loanprocessingfee_amount_sum
            loanprocessingfee_sum_dict["account_number"] = \
                group.account_number
            loanprocessingfee_amount_sum_list.append(
                loanprocessingfee_sum_dict)
            insurance_amount_sum_dict = {}
            insurance_amount_sum_dict["group_name"] = group.name
            insurance_amount_sum_dict["group_id"] = group.id
            insurance_amount_sum_dict["receipt_number"] = \
                insurance_receipts_list
            insurance_amount_sum_dict["insurance_amount_sum"] = \
                insurance_amount_sum
            insurance_amount_sum_dict["account_number"] = group.account_number
            insurance_amount_sum_list.append(insurance_amount_sum_dict)
        else:
            receipts_list = Receipts.objects.filter(
                date=selected_date, group=0)
            thrift_deposit_sum = 0
            loanprinciple_amount_sum = 0
            loaninterest_amount_sum = 0
            entrancefee_amount_sum = 0
            membershipfee_amount_sum = 0
            bookfee_amount_sum = 0
            loanprocessingfee_amount_sum = 0
            insurance_amount_sum = 0
            fixed_deposit_sum = 0
            recurring_deposit_sum = 0
            share_capital_amount_sum = 0

            for receipt in receipts_list:
                thrift_deposit_sum = d(receipt.savingsdeposit_thrift_amount)
                loanprinciple_amount_sum = d(receipt.loanprinciple_amount)
                loaninterest_amount_sum = d(receipt.loaninterest_amount)
                entrancefee_amount_sum = d(receipt.entrancefee_amount)
                membershipfee_amount_sum = d(receipt.membershipfee_amount)
                bookfee_amount_sum = d(receipt.bookfee_amount)
                loanprocessingfee_amount_sum = \
                    d(receipt.loanprocessingfee_amount)
                insurance_amount_sum = d(receipt.insurance_amount)
                fixed_deposit_sum = d(receipt.fixeddeposit_amount)
                recurring_deposit_sum = d(receipt.recurringdeposit_amount)
                share_capital_amount_sum = d(receipt.sharecapital_amount)

                recurring_deposit_sum_dict = {}
                recurring_deposit_sum_dict["group_name"] = \
                    receipt.client.first_name
                recurring_deposit_sum_dict["recurring_deposit_sum"] = \
                    recurring_deposit_sum
                recurring_deposit_sum_dict["account_number"] = \
                    receipt.client.account_number
                recurring_deposit_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                recurring_deposit_sum_list.append(recurring_deposit_sum_dict)
                share_capital_sum_dict = {}
                share_capital_sum_dict["group_name"] = \
                    receipt.client.first_name
                share_capital_sum_dict["share_capital_amount_sum"] = \
                    share_capital_amount_sum
                share_capital_sum_dict["account_number"] = \
                    receipt.client.account_number
                share_capital_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                share_capital_amount_sum_list.append(share_capital_sum_dict)
                fixed_deposit_sum_dict = {}
                fixed_deposit_sum_dict["group_name"] = \
                    receipt.client.first_name
                fixed_deposit_sum_dict["fixed_deposit_sum"] = \
                    fixed_deposit_sum
                fixed_deposit_sum_dict["account_number"] = \
                    receipt.client.account_number
                fixed_deposit_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                fixed_deposit_sum_list.append(fixed_deposit_sum_dict)
                thrift_deposit_sum_dict = {}
                thrift_deposit_sum_dict["group_name"] = \
                    receipt.client.first_name
                thrift_deposit_sum_dict["thrift_deposit_sum"] = \
                    thrift_deposit_sum
                thrift_deposit_sum_dict["account_number"] = \
                    receipt.client.account_number
                thrift_deposit_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                thrift_deposit_sum_list.append(thrift_deposit_sum_dict)
                loanprinciple_amount_sum_dict = {}
                loanprinciple_amount_sum_dict["group_name"] = \
                    receipt.client.first_name
                loanprinciple_amount_sum_dict["loanprinciple_amount_sum"] = \
                    loanprinciple_amount_sum
                loanprinciple_amount_sum_dict["account_number"] = \
                    receipt.client.account_number
                loanprinciple_amount_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                loanprinciple_amount_sum_list.append(
                    loanprinciple_amount_sum_dict)
                loaninterest_sum_dict = {}
                loaninterest_sum_dict["group_name"] = \
                    receipt.client.first_name
                loaninterest_sum_dict["loaninterest_amount_sum"] = \
                    loaninterest_amount_sum
                loaninterest_sum_dict["account_number"] = \
                    receipt.client.account_number
                loaninterest_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                loaninterest_amount_sum_list.append(loaninterest_sum_dict)
                entrancefee_sum_dict = {}
                entrancefee_sum_dict["group_name"] = \
                    receipt.client.first_name
                entrancefee_sum_dict["entrancefee_amount_sum"] = \
                    entrancefee_amount_sum
                entrancefee_sum_dict["account_number"] = \
                    receipt.client.account_number
                entrancefee_sum_dict["receipt_number"] = receipt.receipt_number
                entrancefee_amount_sum_list.append(entrancefee_sum_dict)
                membershipfee_sum_dict = {}
                membershipfee_sum_dict["group_name"] = \
                    receipt.client.first_name
                membershipfee_sum_dict["membershipfee_amount_sum"] = \
                    membershipfee_amount_sum
                membershipfee_sum_dict["account_number"] = \
                    receipt.client.account_number
                membershipfee_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                membershipfee_amount_sum_list.append(membershipfee_sum_dict)
                bookfee_sum_dict = {}
                bookfee_sum_dict["group_name"] = receipt.client.first_name
                bookfee_sum_dict["bookfee_amount_sum"] = bookfee_amount_sum
                bookfee_sum_dict["account_number"] = \
                    receipt.client.account_number
                bookfee_sum_dict["receipt_number"] = receipt.receipt_number
                bookfee_amount_sum_list.append(bookfee_sum_dict)
                loanprocessingfee_sum_dict = {}
                loanprocessingfee_sum_dict["group_name"] = \
                    receipt.client.first_name
                loanprocessingfee_sum_dict["loanprocessingfee_amount_sum"] = \
                    loanprocessingfee_amount_sum
                loanprocessingfee_sum_dict["account_number"] = \
                    receipt.client.account_number
                loanprocessingfee_sum_dict["receipt_number"] = \
                    receipt.receipt_number
                loanprocessingfee_amount_sum_list.append(
                    loanprocessingfee_sum_dict)
                insurance_sum_dict = {}
                insurance_sum_dict["group_name"] = \
                    receipt.client.first_name
                insurance_sum_dict["insurance_amount_sum"] = \
                    insurance_amount_sum
                insurance_sum_dict["account_number"] = \
                    receipt.client.account_number
                insurance_sum_dict["receipt_number"] = receipt.receipt_number
                insurance_amount_sum_list.append(insurance_sum_dict)

    total_dict = {}
    total_recurring_deposit_sum = 0
    for dictionary in recurring_deposit_sum_list:
        total_recurring_deposit_sum += dictionary["recurring_deposit_sum"]
    total_dict["total_recurring_deposit_sum"] = total_recurring_deposit_sum
    total_share_capital_amount_sum = 0
    for dictionary in share_capital_amount_sum_list:
        total_share_capital_amount_sum += \
            dictionary["share_capital_amount_sum"]
    total_dict["total_share_capital_amount_sum"] = \
        total_share_capital_amount_sum
    total_fixed_deposit_sum = 0
    for dictionary in fixed_deposit_sum_list:
        total_fixed_deposit_sum += dictionary["fixed_deposit_sum"]
    total_dict["total_fixed_deposit_sum"] = total_fixed_deposit_sum
    total_thrift_deposit_sum = 0
    for dictionary in thrift_deposit_sum_list:
        total_thrift_deposit_sum += dictionary["thrift_deposit_sum"]
    total_dict["total_thrift_deposit_sum"] = total_thrift_deposit_sum
    total_loanprinciple_amount_sum = 0
    for dictionary in loanprinciple_amount_sum_list:
        total_loanprinciple_amount_sum += \
            dictionary["loanprinciple_amount_sum"]
    total_dict["total_loanprinciple_amount_sum"] = \
        total_loanprinciple_amount_sum
    total_loaninterest_amount_sum = 0
    for dictionary in loaninterest_amount_sum_list:
        total_loaninterest_amount_sum += dictionary["loaninterest_amount_sum"]
    total_dict["total_loaninterest_amount_sum"] = total_loaninterest_amount_sum
    total_entrancefee_amount_sum = 0
    for dictionary in entrancefee_amount_sum_list:
        total_entrancefee_amount_sum += dictionary["entrancefee_amount_sum"]
    total_dict["total_entrancefee_amount_sum"] = total_entrancefee_amount_sum
    total_membershipfee_amount_sum = 0
    for dictionary in membershipfee_amount_sum_list:
        total_membershipfee_amount_sum += \
            dictionary["membershipfee_amount_sum"]
    total_dict["total_membershipfee_amount_sum"] = \
        total_membershipfee_amount_sum
    total_bookfee_amount_sum = 0
    for dictionary in bookfee_amount_sum_list:
        total_bookfee_amount_sum += dictionary["bookfee_amount_sum"]
    total_dict["total_bookfee_amount_sum"] = total_bookfee_amount_sum
    total_loanprocessingfee_amount_sum = 0
    for dictionary in loanprocessingfee_amount_sum_list:
        total_loanprocessingfee_amount_sum += \
            dictionary["loanprocessingfee_amount_sum"]
    total_dict["total_loanprocessingfee_amount_sum"] = \
        total_loanprocessingfee_amount_sum
    total_insurance_amount_sum = 0
    for dictionary in insurance_amount_sum_list:
        total_insurance_amount_sum += dictionary["insurance_amount_sum"]
    total_dict["total_insurance_amount_sum"] = total_insurance_amount_sum

    total = 0
    for key in total_dict:
        total += total_dict[key]

    payments_list = Payments.objects.filter(date=selected_date)
    travellingallowance_list = []
    loans_list = []
    paymentofsalary_list = []
    printingcharges_list = []
    stationarycharges_list = []
    othercharges_list = []
    savingswithdrawal_list = []
    fixedwithdrawal_list = []
    recurringwithdrawal_list = []
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
    dict_payments = {}
    travellingallowance_sum = 0
    loans_sum = 0
    paymentofsalary_sum = 0
    printingcharges_sum = 0
    stationarycharges_sum = 0
    othercharges_sum = 0
    savingswithdrawal_sum = 0
    fixedwithdrawal_sum = 0
    recurringwithdrawal_sum = 0
    for payment in travellingallowance_list:
        travellingallowance_sum += d(payment.total_amount)
    dict_payments["travellingallowance_sum"] = travellingallowance_sum
    for payment in loans_list:
        loans_sum += d(payment.total_amount)
    dict_payments["loans_sum"] = loans_sum
    for payment in paymentofsalary_list:
        paymentofsalary_sum += d(payment.total_amount)
    dict_payments["paymentofsalary_sum"] = paymentofsalary_sum
    for payment in printingcharges_list:
        printingcharges_sum += d(payment.total_amount)
    dict_payments["printingcharges_sum"] = printingcharges_sum
    for payment in stationarycharges_list:
        stationarycharges_sum += d(payment.total_amount)
    dict_payments["stationarycharges_sum"] = stationarycharges_sum
    for payment in othercharges_list:
        othercharges_sum += d(payment.total_amount)
    dict_payments["othercharges_sum"] = othercharges_sum
    for payment in savingswithdrawal_list:
        savingswithdrawal_sum += d(payment.total_amount)
    dict_payments["savingswithdrawal_sum"] = savingswithdrawal_sum
    for payment in fixedwithdrawal_list:
        fixedwithdrawal_sum += d(payment.total_amount)
    dict_payments["fixedwithdrawal_sum"] = fixedwithdrawal_sum
    for payment in recurringwithdrawal_list:
        recurringwithdrawal_sum += d(payment.total_amount)
    dict_payments["recurringwithdrawal_sum"] = recurringwithdrawal_sum

    total_payments = 0
    for key in dict_payments:
        total_payments += dict_payments[key]

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


@login_required
def view_day_book(request):
    if request.method == "POST":
        date = datetime.datetime.strptime(
            request.POST.get("date"), "%m/%d/%Y").strftime("%Y-%m-%d")
    else:
        if request.GET.get("date"):
            date = request.GET.get("date")
        else:
            date = datetime.datetime.now().date()

    # date = str(date)
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

    date_formated = datetime.datetime.strptime(
        str(selected_date), "%Y-%m-%d").strftime("%m/%d/%Y")
    return render(
        request,
        "day_book.html",
        {
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
            "loanprocessingfee_amount_sum_list":
                loanprocessingfee_amount_sum_list,
        })


@login_required
def recurring_deposits(request):
    if request.method == "GET":
        return render(request, "client/recurring-deposits/application.html")
    else:
        try:
            client = Client.objects.get(
                first_name__iexact=request.POST.get("client_name"),
                account_number=request.POST.get("client_account_no"))
            form = ReccuringDepositForm(request.POST, request.FILES)
            if form.is_valid():
                recurring_deposit = form.save(commit=False)
                recurring_deposit.status = "Opened"
                recurring_deposit.client = client
                recurring_deposit.save()
                data = {
                    "error": False,
                    "recurring_deposit_id": recurring_deposit.id}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "message": form.errors}
                return HttpResponse(json.dumps(data))
        except Client.DoesNotExist:
            data = {
                "error": True,
                "messagememerr": "No Member exist with this " +
                                 "Name and Account Number."}
            return HttpResponse(json.dumps(data))


@login_required
def payments_list(request):
    payments_list = Payments.objects.all().order_by("-id")
    return render(request, "list_of_payments.html",
                  {"payments_list": payments_list})


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


@login_required
def view_group_loanslist(request, group_id):
    group = Group.objects.get(id=group_id)
    loan_accounts_list = LoanAccount.objects.filter(group=group)
    loan_accounts_count = LoanAccount.objects.filter(group=group).count()
    return render(
        request,
        "group/loan/list_of_loan_accounts.html",
        {
            "group": group,
            "loan_accounts_list": loan_accounts_list,
            "loan_accounts_count": loan_accounts_count
        }
    )


@login_required
def view_client_loanslist(request, client_id):
    client = Client.objects.get(id=client_id)
    loan_accounts_list = LoanAccount.objects.filter(client=client)
    loan_accounts_count = LoanAccount.objects.filter(client=client).count()
    return render(
        request,
        "client/loan/list_of_loan_accounts.html",
        {
            "client": client,
            "loan_accounts_list": loan_accounts_list,
            "loan_accounts_count": loan_accounts_count
        })


@login_required
def clientledger_csvdownload(request, client_id):
    client = Client.objects.get(id=client_id)
    receipts_list = Receipts.objects.filter(client=client_id).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0)
    try:
        response = HttpResponse(content_type='application/x-download')
        response['Content-Disposition'] = 'attachment; filename=' + \
            client.first_name + client.last_name + "_ledger.csv"
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))
        group = client.group_set.get()
        writer.writerow([
            smart_str(client.id),
            smart_str(client.first_name),
            smart_str(group.name),
        ])
        writer.writerow([
            smart_str(u"Date"),
            smart_str(u"Recepit No"),
            smart_str(u"Demand Principal"),
            smart_str(u"Demand Interest"),
            smart_str(u"Demand Peenal Interest"),
            smart_str(u"Collecton Principal"),
            smart_str(u"Collecton Interest"),
            smart_str(u"Collecton Peenal Interest"),
            smart_str(u"Balance Principal"),
            smart_str(u"Balance Interest"),
            smart_str(u"Balance Peenal Interest"),
            smart_str(u"Loan Outstanding"),
        ])
        for receipt in receipts_list:
            var1 = d(receipt.demand_loanprinciple_amount_atinstant)
            var2 = d(receipt.loanprinciple_amount)
            if var1 > var2:
                balance_principle = d(d(var1) - d(var2))
            else:
                balance_principle = 0

            var4 = d(receipt.demand_loaninterest_amount_atinstant)
            var5 = d(receipt.loaninterest_amount)
            if var4 > var5:
                balance_interest = d(d(var4) - d(var5))
            else:
                balance_interest = 0
            writer.writerow([
                smart_str(receipt.date),
                smart_str(receipt.receipt_number),
                smart_str(receipt.demand_loanprinciple_amount_atinstant),
                smart_str(receipt.demand_loaninterest_amount_atinstant),
                smart_str("0"),
                smart_str(receipt.loanprinciple_amount),
                smart_str(receipt.loaninterest_amount),
                smart_str("0"),
                smart_str(balance_principle),
                smart_str(balance_interest),
                smart_str("0"),
                smart_str(receipt.principle_loan_balance_atinstant),
            ])
        return response
    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)


@login_required
def clientledger_exceldownload(request, client_id):
    client = Client.objects.get(id=client_id)
    receipts_list = Receipts.objects.filter(client=client_id).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0)
    try:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=' + \
            client.first_name + client.last_name + "_ledger.xls"
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("Ledger")

        row_num = 0

        columns = [
            (u"Date", 1000),
            (u"Receipt Number", 1000),
            (u"Demand Principal", 2000),
            (u"Demand Interest", 2000),
            (u"Demand Peenal Interest", 2000),
            (u"Collection Principal", 2000),
            (u"Collection Interest", 2000),
            (u"Collection Peenal Interest", 2000),
            (u"Balance Principal", 2000),
            (u"Balance Interest", 2000),
            (u"Balance Peenal Interest", 2000),
            (u"Loan Outstanding", 2000),
        ]

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        for col_num in xrange(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            ws.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1

        for receipt in receipts_list:
            row_num += 1

            var1 = d(receipt.demand_loanprinciple_amount_atinstant)
            var2 = d(receipt.loanprinciple_amount)
            if var1 > var2:
                balance_principle = d(d(var1) - d(var2))
            else:
                balance_principle = 0

            var4 = d(receipt.demand_loaninterest_amount_atinstant)
            var5 = d(receipt.loaninterest_amount)
            if var4 > var5:
                balance_interest = d(d(var4) - d(var5))
            else:
                balance_interest = 0

            row = [
                str(receipt.date),
                receipt.receipt_number,
                receipt.demand_loanprinciple_amount_atinstant,
                receipt.demand_loaninterest_amount_atinstant,
                0,
                receipt.loanprinciple_amount,
                receipt.loaninterest_amount,
                0,
                balance_principle,
                balance_interest,
                0,
                receipt.principle_loan_balance_atinstant,
            ]
            for col_num in xrange(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)


@login_required
def clientledger_pdfdownload(request, client_id):
    client = Client.objects.get(id=client_id)
    receipts_list = Receipts.objects.filter(client=client_id).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0)
    try:
        # template = get_template("pdfledger.html")
        context = Context({
            'pagesize': 'A4', "receipts_list": receipts_list,
            "client": client, "mediaroot": settings.MEDIA_ROOT})
        return render(request, 'pdfledger.html', context)
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


@login_required
def general_ledger_pdfdownload(request):
    general_ledger_list = general_ledger_function(request)
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


@login_required
def daybook_pdfdownload(request, date):
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


@login_required
def user_change_password(request, user_id):
    if request.method == "GET":
        user = User.objects.get(id=user_id)
        return render(request, "user_change_password.html", {"user": user})
    elif request.method == "POST":
        user = User.objects.get(id=user_id)
        user = authenticate(username=user.username,
                            password=request.POST.get("current_password"))
        if user is not None:
            new_password = request.POST.get("new_password")
            new_pwd_length = len(new_password)
            if new_pwd_length < 1:
                data = {
                    "error": True, "newpwderror": "Password cannot be blank."
                }
                return HttpResponse(json.dumps(data))
            elif new_pwd_length < 5:
                data = {
                    "error": True,
                    "newpwderror": "Your password must be at " +
                                   "least 5 characters long."
                }
                return HttpResponse(json.dumps(data))
            else:
                confirm_new_password = request.POST.get("confirm_new_password")
                if new_password != confirm_new_password:
                    data = {
                        "error": True,
                        "matchpwdserror": "Password and Confirm " +
                                          "Password don't match."
                    }
                    return HttpResponse(json.dumps(data))
                elif new_password == confirm_new_password:
                    user.set_password(new_password)
                    user.save()
                    data = {"error": False}
                    return HttpResponse(json.dumps(data))
        else:
            data = {
                "error": True,
                "currentpwderror": "Entered Current Password is incorrect."}
            return HttpResponse(json.dumps(data))


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

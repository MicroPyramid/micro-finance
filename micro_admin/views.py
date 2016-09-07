import json
import datetime
import decimal
# import csv

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
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
    RecurringDeposits, USER_ROLES, ClientBranchTransfer, Menu, Page, GroupMemberLoanAccount)
from micro_admin.forms import (
    BranchForm, UserForm, GroupForm, ClientForm, AddMemberForm,
    ReceiptForm, FixedDepositForm, PaymentForm,
    ReccuringDepositForm, ChangePasswordForm, GroupMeetingsForm, MenuForm, PageForm, UpdateClientProfileForm)
from micro_admin.mixins import UserPermissionRequiredMixin, BranchAccessRequiredMixin, BranchManagerRequiredMixin, ContentManagerRequiredMixin
from django.db.models.aggregates import Max


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

    def dispatch(self, request, *args, **kwargs):
        # Checking the permissions
        if not self.request.user.is_admin:
            return HttpResponseRedirect(reverse("micro_admin:viewbranch"))

        return super(UpdateBranchView, self).dispatch(
            request, *args, **kwargs)

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


class UpdateClientView(LoginRequiredMixin, BranchManagerRequiredMixin, UpdateView):
    pk = 'pk'
    model = Client
    form_class = ClientForm
    template_name = "client/edit.html"

    def get_form_kwargs(self):
        kwargs = super(UpdateClientView, self).get_form_kwargs()
        client_obj = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        kwargs.update({'user': self.request.user, 'client': client_obj})
        return kwargs

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


class UpdateClientProfileView(LoginRequiredMixin, BranchManagerRequiredMixin, UpdateView):
    pk = 'pk'
    model = Client
    form_class = UpdateClientProfileForm
    template_name = "client/update-profile.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateClientProfileView, self).get_context_data(**kwargs)
        context['photo'] = str(self.object.photo).split('/')[-1] if self.object.photo else None
        context['signature'] = str(self.object.signature).split('/')[-1] if self.object.signature else None
        return context

    def form_valid(self, form):
        self.object.photo = self.request.FILES.get("photo")
        self.object.signature = self.request.FILES.get("signature")
        self.object.save()
        return JsonResponse({
            "error": False,
            "success_url": reverse('micro_admin:clientprofile', kwargs={"pk": self.object.id})
        })

    def form_invalid(self, form):
        data = {"error": True, "errors": form.errors}
        return JsonResponse(data)


class ClientsListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "client/list.html"


class ClientInactiveView(LoginRequiredMixin, BranchManagerRequiredMixin, View):

    def get_object(self):
        return get_object_or_404(Client, id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        client = self.get_object()
        if client.is_active:
            count = 0
            loans = LoanAccount.objects.filter(client=client)
            print (loans)
            for loan in loans:
                if loan.status == "Closed":
                    count += 1
            if count == loans.count():
                client.is_active = False
                client.save()
            else:
                raise Http404("Oops! Member is involved in loan, Unable to delete.")
        else:
            client.is_active = True
            client.save()
        return HttpResponseRedirect(reverse("micro_admin:viewclient"))

from django.contrib.auth.models import Permission, ContentType
# ------------------------------------------- #
# User Model views
class CreateUserView(LoginRequiredMixin, CreateView):
    form_class = UserForm
    template_name = "user/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateUserView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['userroles'] = dict(USER_ROLES).keys()
        contenttype = ContentType.objects.get_for_model(self.request.user)
        permissions = Permission.objects.filter(content_type_id=contenttype, codename__in=["branch_manager", 'content_manager'])
        context['permissions'] = permissions
        return context

    def form_valid(self, form):
        user = form.save()
        if len(self.request.POST.getlist("user_permissions")):
            user.user_permissions.add(
                *self.request.POST.getlist("user_permissions"))
        if self.request.POST.get("user_roles") == "BranchManager":
            if not user.user_permissions.filter(id__in=self.request.POST.getlist("user_permissions")).exists():
                user.user_permissions.add(Permission.objects.get(codename="branch_manager"))
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
        contenttype = ContentType.objects.get_for_model(self.request.user)
        permissions = Permission.objects.filter(content_type_id=contenttype, codename__in=["branch_manager", 'content_manager'])
        context['permissions'] = permissions
        return context

    def form_valid(self, form):
        selected_user = User.objects.get(id=self.kwargs.get('pk'))
        if not (
           self.request.user.is_admin or self.request.user == selected_user or
           (
               self.request.user.has_perm("branch_manager") and
               self.request.user.branch == selected_user.branch
           )):
            return JsonResponse({
                "error": True,
                "message": "You are unbale to Edit this staff details.",
                "success_url": reverse('micro_admin:userslist')
            })
        else:
            user = form.save()
            if len(self.request.POST.getlist("user_permissions")):
                user.user_permissions.clear()
                user.user_permissions.add(
                    *self.request.POST.getlist("user_permissions"))
            if self.request.POST.get("user_roles") == "BranchManager":
                if not user.user_permissions.filter(id__in=self.request.POST.getlist("user_permissions")).exists():
                    user.user_permissions.add(Permission.objects.get(codename="branch_manager"))

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
        group_loan_accounts = LoanAccount.objects.filter(group=group, group__account_number=group.account_number, client__isnull=True)
        count = 0
        for group_loan_account in group_loan_accounts:
            if GroupMemberLoanAccount.objects.filter(group_loan_account=group_loan_account, client=client, status="Closed").exists():
                count += 1
                if count == group_loan_accounts:

                    group.clients.remove(client)
                    client.status = "UnAssigned"
                    client.save()
                    return HttpResponseRedirect(reverse('micro_admin:groupprofile', kwargs={'group_id': group.id}))
            else:
                raise Http404("Oops! Unable to delete this Member, Group Loan Not yet Closed.")


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


class AddMenuView(LoginRequiredMixin, CreateView):
    form_class = MenuForm
    template_name = "contentmanagement/menu/add.html"

    def get_context_data(self, **kwargs):
        context = super(AddMenuView, self).get_context_data(**kwargs)
        context['parent'] = Menu.objects.filter(parent=None).order_by('lvl')
        return context

    def form_valid(self, form):
        new_menu = form.save(commit=False)
        if new_menu.status:
            new_menu.status = 'on'

        menu_count = Menu.objects.filter(parent=new_menu.parent).count()
        new_menu.lvl = menu_count + 1
        if new_menu.url[-1] != '/':
            new_menu.url = new_menu.url + '/'

        new_menu.save()
        return JsonResponse({
            "error": False})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class MenuListView(LoginRequiredMixin, ListView):
    model = Menu
    template_name = "contentmanagement/menu/list.html"
    context_object_name = 'menu_list'

    def get_queryset(self):
        return Menu.objects.filter(parent=None).order_by('lvl')


class UpdateMenuView(LoginRequiredMixin, ContentManagerRequiredMixin, UpdateView):
    pk_url_kwarg = 'pk'
    model = Menu
    form_class = MenuForm
    context_object_name = 'current_menu'
    template_name = "contentmanagement/menu/edit.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateMenuView, self).get_context_data(**kwargs)
        context['parent'] = Menu.objects.filter(parent=None).order_by('lvl')
        return context

    def form_valid(self, form):
        current_menu = get_object_or_404(Menu, pk=self.kwargs.get('pk'))
        current_parent = current_menu.parent
        updated_menu = form.save(commit=False)
        if updated_menu.parent != current_parent:
            try:
                if updated_menu.parent.id == updated_menu.id:
                    data = {'error': True, 'response': {
                        'parent': 'You can not choose the same as parent'}}
                    return HttpResponse(
                        json.dumps(data),
                        content_type='application/json; charset=utf-8')
            except Exception:
                pass

            lnk_count = Menu.objects.filter(
                parent=updated_menu.parent).count()
            updated_menu.lvl = lnk_count + 1
            lvlmax = Menu.objects.filter(
                parent=current_parent).aggregate(Max('lvl'))['lvl__max']
            if lvlmax != 1:
                for i in Menu.objects.filter(parent=current_parent,
                                             lvl__gt=current_menu.lvl,
                                             lvl__lte=lvlmax):
                    i.lvl = i.lvl - 1
                    i.save()
        if updated_menu.url[-1] != '/':
            updated_menu.url = updated_menu.url + '/'

        if self.request.POST.get('status', ''):
            updated_menu.status = 'on'

        updated_menu.save()
        return JsonResponse({
            "error": False
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class DeleteMenuView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.has_perm('content_manager'):
            menu = get_object_or_404(Menu, id=kwargs.get('pk'))
            menu.delete()
            return HttpResponseRedirect(reverse('micro_admin:list_menu'))
        raise Http404("Oops! Unable to delete the menu")


class ChangeMenuStatusView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        menu = get_object_or_404(Menu, pk=kwargs.get('pk'))
        if menu.status == "on":
            menu.status = "off"
        else:
            menu.status = "on"
        menu.save()
        return HttpResponseRedirect(reverse('micro_admin:list_menu'))


class MenuOrderView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        curr_link = get_object_or_404(Menu, pk=kwargs.get('pk'))
        link_parent = curr_link.parent
        if self.request.GET.get('mode') == 'down':
            lvlmax = Menu.objects.filter(
                parent=kwargs.get('pk')).aggregate(Max('lvl'))['lvl__max']
            if lvlmax == curr_link.lvl:
                data = {'error': True, 'message': 'You cant move down.'}
            count = Menu.objects.all().count()
            if count == curr_link.lvl:
                data = {'error': True, 'message': 'You cant move down.'}
            else:
                try:
                    down_link = Menu.objects.get(
                        parent=link_parent, lvl=curr_link.lvl + 1)
                    curr_link.lvl = curr_link.lvl + 1
                    down_link.lvl = down_link.lvl - 1
                    curr_link.save()
                    down_link.save()
                except ObjectDoesNotExist:
                    pass
                data = {'error': False}
        else:
            count = Menu.objects.all().count()
            if curr_link.lvl == 1:
                data = {'error': True, 'message': 'You cant move up.'}
            else:
                try:
                    up_link = Menu.objects.get(
                        parent=link_parent, lvl=curr_link.lvl - 1)
                    curr_link.lvl = curr_link.lvl - 1
                    up_link.lvl = up_link.lvl + 1
                    curr_link.save()
                    up_link.save()
                except ObjectDoesNotExist:
                    pass
                data = {'error': False}
        return HttpResponse(
            json.dumps(data), content_type='application/json; charset=utf-8')


class PageListView(LoginRequiredMixin, ListView):
    model = Page
    template_name = "contentmanagement/pages/list.html"
    context_object_name = 'pages_list'

    def get_queryset(self):
        return Page.objects.all().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(PageListView, self).get_context_data(**kwargs)
        context['HTTP_HOST'] = self.request.META.get('HTTP_HOST')
        return context


class AddPageView(LoginRequiredMixin, CreateView):
    form_class = PageForm
    template_name = "contentmanagement/pages/add.html"

    def form_valid(self, form):
        form.save()
        return JsonResponse({
            "error": False})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class UpdatePageView(LoginRequiredMixin, ContentManagerRequiredMixin, UpdateView):
    pk_url_kwarg = 'pk'
    model = Page
    form_class = PageForm
    context_object_name = 'current_page'
    template_name = "contentmanagement/pages/add.html"

    def form_valid(self, form):
        form.save()
        return JsonResponse({
            "error": False
        })

    def form_invalid(self, form):
        return JsonResponse({"error": True, "errors": form.errors})


class DeletePageView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.has_perm('content_manager'):
            page = get_object_or_404(Page, id=kwargs.get('pk'))
            page.delete()
            return HttpResponseRedirect(reverse('micro_admin:list_page'))
        raise Http404("Oops! Unable to delete the page")


class ChangePageStatusView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        page = get_object_or_404(Page, pk=kwargs.get('pk'))
        if page.is_active:
            page.is_active = False
        else:
            page.is_active = True
        page.save()
        return HttpResponseRedirect(reverse('micro_admin:list_page'))

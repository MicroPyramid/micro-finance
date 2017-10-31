import datetime
import decimal
# import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import login, authenticate, logout
# from django.views.generic.detail import BaseDetailView
# from django.utils.encoding import smart_str
from django.template import Context
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
    LoanAccount, Receipts, FixedDeposits, Payments,
    RecurringDeposits, USER_ROLES, GroupMemberLoanAccount)
from micro_admin.forms import (
    BranchForm, UserForm, GroupForm, ClientForm, AddMemberForm,
    FixedDepositForm, ReccuringDepositForm, ChangePasswordForm,
    GroupMeetingsForm, UpdateClientProfileForm)
from micro_admin.mixins import BranchAccessRequiredMixin, BranchManagerRequiredMixin
from django.contrib.auth.models import Permission, ContentType
# from weasyprint import HTML, CSS
from django.template.loader import get_template

d = decimal.Decimal


def index(request):
    if request.user.is_authenticated():
        receipts_list = Receipts.objects.all().order_by("-id")
        payments_list = Payments.objects.all().order_by("-id")
        fixed_deposits_list = FixedDeposits.objects.all().order_by('-id')
        recurring_deposits_list = RecurringDeposits.objects.all().order_by('-id')
        branches_count = Branch.objects.count()
        staff_count = User.objects.count()
        groups_count = Group.objects.count()
        clients_count = Client.objects.count()
        return render(request, "index.html", {"user": request.user,
                      "receipts": receipts_list, "payments": payments_list,
                      "fixed_deposits": fixed_deposits_list, "groups_count": groups_count,
                      "branches_count": branches_count, "clients_count": clients_count,
                      "staff_count": staff_count, "recurring_deposits": recurring_deposits_list})
    return render(request, "login.html")


def getin(request):
    if request.method == 'POST':
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
    else:
        if request.user.is_authenticated():
            return render(request, 'index.html', {'user': request.user})
        return render(request, "login.html")


def getout(request):
    logout(request)
    return redirect("micro_admin:login")


def transactions(request):
    return render(request, "transactions.html")


def deposits(request):
    return render(request, "deposits.html")


def reports(request):
    return render(request, "reports.html")


# --------------------------------------------------- #
# Branch Model class Based View #
def create_branch_view(request):
    form = BranchForm()
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save()
            return JsonResponse({
                "error": False,
                "success_url": reverse('micro_admin:branchprofile', kwargs={"pk": branch.id})
            })
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    return render(request, "branch/create.html", {'form': form})


def update_branch_view(request, pk):
    form = BranchForm()
    branch = get_object_or_404(Branch, id=pk)
    if not request.user.is_admin:
        return HttpResponseRedirect(reverse("micro_admin:viewbranch"))
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            branch = form.save()
            return JsonResponse({
                "error": False, "success_url": reverse('micro_admin:branchprofile', kwargs={'pk': branch.id})
            })
        else:

            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "branch/edit.html", {'form': form, 'branch': branch})


def branch_profile_view(request, pk):
    branch = get_object_or_404(Branch, id=pk)
    return render(request, "branch/view.html", {'branch': branch})


def branch_list_view(request):
    branch_list = Branch.objects.all()
    return render(request, "branch/list.html", {'branch_list': branch_list})


def branch_inactive_view(request, pk):
    if request.user.is_admin:
        branch = get_object_or_404(Branch, id=pk)
        if branch.is_active:
            branch.is_active = False
        else:
            branch.is_active = True
        branch.save()
    return HttpResponseRedirect(reverse('micro_admin:viewbranch'))
# --------------------------------------------------- #


# --------------------------------------------------- #
# Clinet model views
def create_client_view(request):
    branches = Branch.objects.all()
    form = ClientForm()
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.save()
            return JsonResponse({
                "error": False,
                "success_url": reverse('micro_admin:clientprofile', kwargs={"pk": client.id})
            })
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    return render(request, "client/create.html", {'branches': branches, 'client_roles': CLIENT_ROLES})


def client_profile_view(request, pk):
    client = get_object_or_404(Client, id=pk)
    return render(request, "client/profile.html", {'client': client})


def update_client_view(request, pk):
    form = ClientForm()
    branches = Branch.objects.all()
    client_obj = get_object_or_404(Client, id=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, user=request.user, client=client_obj, instance=client_obj)
        if form.is_valid():
            client = form.save()
            return JsonResponse({
                "error": False,
                "success_url": reverse('micro_admin:clientprofile', kwargs={"pk": client.id})
            })
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    return render(request, "client/edit.html", {'branches': branches, 'client_roles': CLIENT_ROLES, 'client':client_obj})


def updateclientprofileview(request, pk):
    form = UpdateClientProfileForm()
    client_obj = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = UpdateClientProfileForm(request.POST)
        if form.is_valid():
            client_obj.photo = request.FILES.get("photo")
            client_obj.signature = request.FILES.get("signature")
            client_obj.save()
            return JsonResponse({
                "error": False,
                "success_url": reverse('micro_admin:clientprofile', kwargs={"pk": client_obj.id})
            })
        else:
            data = {"error": True, "errors": form.errors}
            return JsonResponse(data)

    photo = str(client_obj.photo).split('/')[-1] if client_obj.photo else None
    signature = str(client_obj.signature).split('/')[-1] if client_obj.signature else None

    return render(request, "client/update-profile.html", {
        'form': form, 'photo': photo, 'signature': signature})


def clients_list_view(request):
    client_list = Client.objects.all()
    return render(request, "client/list.html", {'client_list': client_list})


def client_inactive_view(request, pk):
    client = get_object_or_404(Client, id=pk)
    if client.is_active:
        count = 0
        loans = LoanAccount.objects.filter(client=client)
        savings_account = SavingsAccount.objects.filter(client=client).last()
        if (loans and savings_account) or savings_account or loans:
            if loans and savings_account:
                if savings_account and savings_account.savings_balance != 0:
                    raise Http404("Oops! Member is involved in savings, Unable to delete.")
                # elif loans and loans.count() != loans.filter(status='Closed').count():
                elif loans and loans.count() != loans.filter(total_loan_balance=0).count():
                    raise Http404("Oops! Member is involved in loan, Unable to delete.")
                else:
                    client.is_active = False
                    client.save()
                    # return HttpResponseRedirect(reverse("micro_admin:viewclient")
            elif savings_account:
                if savings_account.savings_balance != 0:
                    raise Http404("Oops! Member is involved in savings, Unable to delete.")
                else:
                    client.is_active = False
                    client.save()
            elif loans:
                for loan in loans:
                    if loan.total_loan_balance == 0:
                        count += 1
                        if count == loans.count():
                            client.is_active = False
                            client.save()
                    else:
                        raise Http404("Oops! Member is involved in loan, Unable to delete.")
            else:
                client.is_active = True
                client.save()
        else:
            client.is_active = False
            client.save()
    return HttpResponseRedirect(reverse("micro_admin:viewclient"))

# ------------------------------------------- #
# User Model views


def create_user_view(request):
    branches = Branch.objects.all()
    contenttype = ContentType.objects.get_for_model(request.user)
    permissions = Permission.objects.filter(content_type_id=contenttype, codename__in=["branch_manager"])
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            if len(request.POST.getlist("user_permissions")):
                user.user_permissions.add(
                    *request.POST.getlist("user_permissions"))
            if request.POST.get("user_roles") == "BranchManager":
                if not user.user_permissions.filter(id__in=request.POST.getlist("user_permissions")).exists():
                    user.user_permissions.add(Permission.objects.get(codename="branch_manager"))
            return JsonResponse({
                "error": False,
                "success_url": reverse('micro_admin:userprofile', kwargs={"pk": user.id})
            })
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "user/create.html", {
        'form': form, 'userroles': USER_ROLES, 'branches': branches, 'permissions': permissions})


def update_user_view(request, pk):
    branch = Branch.objects.all()
    contenttype = ContentType.objects.get_for_model(request.user)
    permissions = Permission.objects.filter(content_type_id=contenttype, codename__in=["branch_manager"])
    form = UserForm()
    selected_user = User.objects.get(id=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=selected_user)
        if form.is_valid():
            if not (
               request.user.is_admin or request.user == selected_user or
               (
                   request.user.has_perm("branch_manager") and
                   request.user.branch == selected_user.branch
               )):
                return JsonResponse({
                    "error": True,
                    "message": "You are unbale to Edit this staff details.",
                    "success_url": reverse('micro_admin:userslist')
                })
            else:
                user = form.save()
                user.user_permissions.clear()
                user.user_permissions.add(*request.POST.getlist("user_permissions"))
                if request.POST.get("user_roles") == "BranchManager":
                    if not user.user_permissions.filter(id__in=request.POST.getlist("user_permissions")).exists():
                        user.user_permissions.add(Permission.objects.get(codename="branch_manager"))

                return JsonResponse({
                    "error": False,
                    "success_url": reverse('micro_admin:userprofile', kwargs={"pk": user.id})
                })
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "user/edit.html", {
        'form': form, 'userroles': USER_ROLES, 'branch': branch, 'permissions': permissions, 'selecteduser': selected_user})


def user_profile_view(request, pk):
    selecteduser = get_object_or_404(User, id=pk)
    return render(request, "user/profile.html", {'selecteduser': selecteduser})


def users_list_view(request):
    list_of_users = User.objects.filter(is_admin=0)
    return render(request, "user/list.html", {'list_of_users': list_of_users})


def user_inactive_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if (request.user.is_admin or (request.user.has_perm("branch_manager") and
                                  request.user.branch == user.branch)):
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
    return HttpResponseRedirect(reverse('micro_admin:userslist'))

# ------------------------------------------------- #


def create_group_view(request):
    branches = Branch.objects.all()
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            return JsonResponse({
                "error": False,
                "success_url": reverse('micro_admin:groupprofile', kwargs={"group_id": group.id})
            })
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "group/create.html", {'form': form, 'branches': branches})


def group_profile_view(request, group_id):
    group_obj = Group.objects.filter(id=group_id).first()
    clients_list = group_obj.clients.all()
    group_mettings = GroupMeetings.objects.filter(group_id=group_obj.id).order_by('-id')
    clients_count = len(clients_list)
    latest_group_meeting = group_mettings.first() if group_mettings else None
    return render(request, "group/profile.html", {
        'clients_list': clients_list, 'clients_count': clients_count, 'latest_group_meeting': latest_group_meeting, 'group': group_obj})


def groups_list_view(request):
    groups_list = Group.objects.all().prefetch_related("clients", "staff", "branch")

    return render(request, "group/list.html", {'groups_list': groups_list})


def group_inactive_view(request, group_id):
    group = Group.objects.filter(id=group_id)
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


def group_assign_staff_view(request, group_id):
    group = Group.objects.filter(id=group_id).first()
    users_list = User.objects.filter(is_admin=0)
    if request.method == 'POST':
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

    return render(request, "group/assign_staff.html", {'users_list': users_list, 'group': group})


def group_add_members_view(request, group_id):
    form = AddMemberForm()
    clients_list = Client.objects.filter(status="UnAssigned", is_active=1)
    group = Group.objects.filter(id=group_id).first()
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            client_ids = request.POST.getlist("clients")
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
        else:
            return JsonResponse({"error": True, "message": form.errors})

    return render(request, "group/add_member.html", {'form': form, 'clients_list': clients_list, 'group': group})


def group_members_list_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    clients_list = group.clients.all()

    return render(request, "group/view-members.html", {'group': group, 'clients_list': clients_list})


def group_remove_members_view(request, group_id, client_id):
    group = Group.objects.filter(id=group_id)
    client = get_object_or_404(Client, id=client_id)
    group_loan_accounts = LoanAccount.objects.filter(group=group, group__account_number=group.account_number, client__isnull=True)
    group_savings_account = SavingsAccount.objects.filter(group=group, group__account_number=group.account_number, client__isnull=True).last()
    client_savings_account = SavingsAccount.objects.filter(client=client).last()
    count = 0
    if (group_loan_accounts and (group_savings_account and client_savings_account)) or\
            (group_savings_account and client_savings_account) or group_loan_accounts:
        if group_loan_accounts and (client_savings_account and client_savings_account):
            if client_savings_account.savings_balance != 0:
                raise Http404("Oops! Unable to delete this Member, Savings Account Not yet Closed.")
            elif group_loan_accounts and group_loan_accounts.count() != GroupMemberLoanAccount.objects.filter(
                    group_loan_account__in=group_loan_accounts, client=client, total_loan_balance=0).count():
                raise Http404("Oops! Unable to delete this Member, Group Loan Not yet Closed.")
            else:
                group.clients.remove(client)
                client.status = "UnAssigned"
                client.save()
        elif group_savings_account and client_savings_account:
            if not client_savings_account.savings_balance == 0:
                raise Http404("Oops! Unable to delete this Member, Savings Account Not yet Closed.")
            else:
                group.clients.remove(client)
                client.status = "UnAssigned"
                client.save()
            #     return HttpResponseRedirect(reverse('micro_admin:groupprofile', kwargs={'group_id': group.id}))
        elif group_loan_accounts:
            for group_loan_account in group_loan_accounts:
                # if not GroupMemberLoanAccount.objects.filter(group_loan_account=group_loan_account, client=client, status="Closed").exists():
                if not GroupMemberLoanAccount.objects.filter(group_loan_account=group_loan_account, client=client, total_loan_balance=0).exists():
                    raise Http404("Oops! Unable to delete this Member, Group Loan Not yet Closed.")
                else:
                    count += 1
                    if count == group_loan_accounts:

                        group.clients.remove(client)
                        client.status = "UnAssigned"
                        client.save()
                    #     return HttpResponseRedirect(reverse('micro_admin:groupprofile', kwargs={'group_id': group.id}))
    return HttpResponseRedirect(reverse('micro_admin:groupprofile', kwargs={'group_id': group.id}))


def group_meetings_list_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_meetings = GroupMeetings.objects.filter(group=group).order_by('-id')

    return render(request, "group/meetings/list.html", {'group': group, 'group_meetings': group_meetings})


def group_meetings_add_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = GroupMeetingsForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.group = group
            meeting.save()
            return JsonResponse({"error": False, "group_id": group.id})
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "group/meetings/add.html", {'group': group})


def receipts_list(request):
    receipt_list = Receipts.objects.all().order_by("-id")
    return render(request, "listof_receipts.html", {'receipt_list': receipt_list})


def general_ledger(request):
    ledgers_list = Receipts.objects.all().values("date").distinct().order_by("-date").annotate(
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

    return render(request, "generalledger.html", {'ledgers_list': ledgers_list})


def fixed_deposits_view(request):
    form = FixedDepositForm()
    if request.method == 'POST':
        form = FixedDepositForm(request.POST, request.FILES)
        if form.is_valid():
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
            url = reverse('micro_admin:clientfixeddepositsprofile', kwargs={"fixed_deposit_id": fixed_deposit.id})
            return JsonResponse({"error": False, "success_url": url})
        else:
            return JsonResponse({"error": True, "message": form.errors})

    return render(request, "client/fixed-deposits/fixed_deposit_application.html", {'form': form})


def client_fixed_deposits_profile(request, fixed_deposit_id):
    fixed_deposits = FixedDeposits.objects.get(id=fixed_deposit_id)
    return render(request, "client/fixed-deposits/fixed_deposits_profile.html", {'fixed_deposit': fixed_deposits})


def view_client_fixed_deposits(request):
    fixed_deposits = FixedDeposits.objects.all()
    return render(request, "client/fixed-deposits/view_fixed_deposits.html", {
        'fixed_deposits': fixed_deposits})


def view_particular_client_fixed_deposits(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client_fixed_deposits = FixedDeposits.objects.filter(client=client).order_by("-id")

    return render(request, "client/fixed-deposits/view_fixed_deposits.html", {
        'client': client, 'client_fixed_deposits': client_fixed_deposits})


def client_recurring_deposits_profile(request, recurring_deposit_id):
    recurring_deposit = RecurringDeposits.objects.get(id=recurring_deposit_id)
    return render(request, "client/recurring-deposits/recurring_deposit_profile.html", {
        'recurring_deposit': recurring_deposit})


def view_client_recurring_deposits(request):
    recurring_deposit_list = RecurringDeposits.objects.all().order_by("-id")
    return render(request, "client/recurring-deposits/view_recurring_deposits.html", {
        'recurring_deposit_list': recurring_deposit_list})


def view_particular_client_recurring_deposits(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    recurring_deposit_list = RecurringDeposits.objects.filter(client=client).order_by("-id")

    return render(request, "client/recurring-deposits/view_recurring_deposits.html", {
        'recurring_deposit_list': recurring_deposit_list})


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


def day_book_view(request):
    if request.GET.get("date"):
        try:
            date = datetime.datetime.strptime(request.GET.get("date"), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return render(request, "day_book.html", {"error_message": "Invalid date."})
    else:
        date = datetime.datetime.now().date()
    return render(request, "day_book.html", {'date': date})
    if request.method == 'POST':
        try:
            date = datetime.datetime.strptime(request.POST.get("date"), "%m/%d/%Y").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return render(request, "day_book.html", {"error_message": "Invalid date."})

        return render(request, "day_book.html", {'date': date})

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


def recurring_deposits_view(request):
    form = ReccuringDepositForm()
    if request.method == 'POST':
        form = ReccuringDepositForm(request.POST, request.FILES)
        if form.is_valid():
            recurring_deposit = form.save(commit=False)
            recurring_deposit.status = "Opened"
            recurring_deposit.client = form.client
            recurring_deposit.save()
            url = reverse('micro_admin:clientrecurringdepositsprofile',
                          kwargs={"recurring_deposit_id": recurring_deposit.id})
            return JsonResponse({"error": False, "success_url": url})
        else:
            return JsonResponse({"error": True, "message": form.errors})

    return render(request, "client/recurring-deposits/application.html", {'form': form})


def payments_list(request):
    payments_list = Payments.objects.all().order_by("-id")
    return render(request, "list_of_payments.html", {'payments_list': payments_list})


# def general_ledger_pdf_download(request):

#     def get(self, request, *args, **kwargs):
#         general_ledger_list = general_ledger_function()
#         print (general_ledger_list)
#         try:
#             template = get_template("pdfgeneral_ledger.html")
#             # context = Context(
#             #     {'pagesize': 'A4', "list": general_ledger_list,
#             #      "mediaroot": settings.MEDIA_ROOT})
#             context = dict(
#                 {'pagesize': 'A4', "list": general_ledger_list,
#                  "mediaroot": settings.MEDIA_ROOT})
#             # return render(request, 'pdfgeneral_ledg
#             # # return render(request, 'pdfgeneral_ledger.html', context)
#             # html = template.render(context)
#             # result = StringIO.StringIO()
#             # # pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
#             # if not pdf.err:
#             #     return HttpResponse(result.getvalue(),
#             #                         content_type='application/pdf')
#             # else:
#             #     return HttpResponse('We had some errors')
#             # html = template.render(context)
#             # import pdfkit

#             # pdfkit.from_string(html, 'out.pdf')
#             # pdf = open("out.pdf")
#             # response = HttpResponse(pdf.read(), content_type='application/pdf')
#             # response['Content-Disposition'] = 'attachment; filename=General Ledger.pdf'
#             # pdf.close()
#             # os.remove("out.pdf")
#             # return response
#             html_template = get_template("pdfgeneral_ledger.html")
#             context = dict({
#                'pagesize': 'A4',
#                "list": general_ledger_list,
#                "mediaroot": settings.MEDIA_ROOT
#                })
#             rendered_html = html_template.render(context).encode(encoding="UTF-8")
#             pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(settings.COMPRESS_ROOT + '/css/mf.css'), CSS(settings.COMPRESS_ROOT + '/css/pdf_stylesheet.css')])

#             http_response = HttpResponse(pdf_file, content_type='application/pdf')
#             http_response['Content-Disposition'] = 'filename="report.pdf"'

#             return http_response

#         except Exception as err:
#             errmsg = "%s" % (err)
#             return HttpResponse(errmsg)


def daybook_pdf_download(request):
    date = request.GET.get("date")
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
        context = dict(
            {'pagesize': 'A4',
             "mediaroot": settings.MEDIA_ROOT,
             "receipts_list": receipts_list, "total_payments": total_payments,
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
        # return render(request, 'pdf_daybook.html', context)
        # html = template.render(context)
        # result = StringIO.StringIO()
        # # pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
        # if not pdf.err:
        #     return HttpResponse(result.getvalue(),
        #                         content_type='application/pdf')
        # else:
        #     return HttpResponse('We had some errors')
        html_template = get_template("pdf_daybook.html")
        # context = Context({
        #    'pagesize': 'A4',
        #    "list": general_ledger_list,
        #    "mediaroot": settings.MEDIA_ROOT
        #    })
        rendered_html = html_template.render(context).encode(encoding="UTF-8")
        pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(
            settings.COMPRESS_ROOT + '/css/mf.css'), CSS(settings.COMPRESS_ROOT + '/css/pdf_stylesheet.css')])

        http_response = HttpResponse(pdf_file, content_type='application/pdf')
        http_response['Content-Disposition'] = 'filename="report.pdf"'

        return http_response

    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)
    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)


def user_change_password(request):
    form = ChangePasswordForm()
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data.get("new_password"))
            user.save()
            return JsonResponse({"error": False, "message": "You have changed your password!"})
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "user_change_password.html", {'form': form})

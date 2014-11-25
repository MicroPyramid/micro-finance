from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import login, authenticate, logout
import json
from micro_admin.models import User, Branch, Group, Client, CLIENT_ROLES, GroupMeetings, SavingsAccount, SavingsTransactions, LoanAccount, LoanTransactions
from micro_admin.forms import BranchForm, UserForm, EditbranchForm, GroupForm, ClientForm, AddMemberForm, EditclientForm, GroupSavingsAccountForm, GroupLoanAccountForm, ClientSavingsAccountForm, ClientLoanAccountForm
from django.contrib.auth.decorators import login_required
import datetime
import decimal


def index(request):
    data = {}
    data.update(csrf(request))
    return render_to_response("login.html",data)


def user_login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                data = {"error":False,"message":"Loggedin Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error":True, "message":"User is not active."}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":"Username and Password were incorrect."}
            return HttpResponse(json.dumps(data))
    else:
        if request.user.is_authenticated():
            username = request.user
            user = User.objects.get(username=username)
            return render(request, "index.html", {"user": user})


@login_required
def user_logout(request):
    if not request.user.is_authenticated():
        return HttpResponse("")
    logout(request)
    return HttpResponseRedirect("/")


@login_required
def create_branch(request):
    if request.method == "GET":
        data = {}
        return render(request, "createbranch.html", {"data":data})
    else:
        form = BranchForm(request.POST)
        if form.is_valid():
            name = request.POST.get("name")
            datestring_format = datetime.datetime.strptime(request.POST.get("opening_date"),"%m/%d/%Y").strftime("%Y-%m-%d")
            dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            opening_date = dateconvert
            country = request.POST.get("country")
            state = request.POST.get("state")
            district = request.POST.get("district")
            city = request.POST.get("city")
            area = request.POST.get("area")
            phone_number = request.POST.get("phone_number")
            pincode = request.POST.get("pincode")
            branch = Branch.objects.create(name=name,opening_date=opening_date,country=country,state=state,district=district,city=city,area=area,phone_number=phone_number,pincode=pincode)
            data = {"error":False, "branch_id":branch.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def edit_branch(request, branch_id):
    if request.method == "GET":
        branch = Branch.objects.get(id=branch_id)
        return render(request, "editbranchdetails.html", {"branch":branch, "branch_id":branch_id})
    else:
        form = EditbranchForm(request.POST)
        if form.is_valid():
            branch = Branch.objects.get(id=branch_id)
            branch.country = request.POST.get("country")
            branch.state = request.POST.get("state")
            branch.district = request.POST.get("district")
            branch.city = request.POST.get("city")
            branch.area = request.POST.get("area")
            branch.phone_number = request.POST.get("phone_number")
            branch.pincode = request.POST.get("pincode")
            branch.save()
            data = {"error":False, "branch_id":branch.id}
            return HttpResponse(json.dumps(data))


@login_required
def branch_profile(request,branch_id):
    branch = Branch.objects.get(id=branch_id)
    return render(request,"branchprofile.html", {"branch":branch})


@login_required
def view_branch(request):
    branch_list = Branch.objects.all()
    return render(request,"viewbranch.html",{"branch_list":branch_list})


@login_required
def delete_branch(request,branch_id):
    branch = Branch.objects.get(id=branch_id)
    branch_list = Branch.objects.all()
    branch.delete()
    return render(request,"viewbranch.html", {"branch_list":branch_list})


@login_required
def create_client(request):
    if request.method == "GET":
        data = {}
        branch = Branch.objects.all()
        return render(request,"createclient.html", {"data":data, "branch":branch})
    else:
        form = ClientForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            account_number = request.POST.get("account_number")
            blood_group = request.POST.get("blood_group")
            gender = request.POST.get("gender")
            client_role = request.POST.get("client_role")
            occupation = request.POST.get("occupation")
            annual_income = request.POST.get("annual_income")
            country = request.POST.get("country")
            state = request.POST.get("state")
            district = request.POST.get("district")
            city = request.POST.get("city")
            area = request.POST.get("area")
            mobile = request.POST.get("mobile")
            pincode = request.POST.get("pincode")
            branch = Branch.objects.get(id=request.POST.get('branch'))
            birth_datestring_format = datetime.datetime.strptime(request.POST.get("date_of_birth"),'%m/%d/%Y').strftime('%Y-%m-%d')
            birth_dateconvert = datetime.datetime.strptime(birth_datestring_format, "%Y-%m-%d")
            date_of_birth = birth_dateconvert
            datestring_format = datetime.datetime.strptime(request.POST.get("date_of_birth"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            joined_date = dateconvert
            client = Client.objects.create(branch=branch, first_name=first_name, last_name=last_name, email=email, created_by=created_by, account_number=account_number, blood_group=blood_group, gender=gender, client_role=client_role, occupation=occupation, annual_income=annual_income, country=country, state=state, district=district, city=city, area=area, mobile=mobile, pincode=pincode, date_of_birth=date_of_birth, joined_date=joined_date)
            data = {"error":False, "client_id":client.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_profile(request,client_id):
    client = Client.objects.get(id=client_id)
    branch = Branch.objects.all()
    return render(request,"clientprofile.html", {"client":client, "branch":branch})


@login_required
def edit_client(request,client_id):
    if request.method =="GET":
        client = Client.objects.get(id=client_id)
        l = []
        for i in CLIENT_ROLES:
            l.append(i[0])
        branch = Branch.objects.all()
        return render(request,"editclient.html", {"client":client, "branch":branch, "client_id":client_id, "CLIENT_ROLES":CLIENT_ROLES, "l":l})
    else:
        form = EditclientForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(id=client_id)
            client.client_role = request.POST.get("client_role")
            client.occupation = request.POST.get("occupation")
            client.blood_group = request.POST.get("blood_group")
            client.annual_income = request.POST.get("annual_income")
            client.email = request.POST.get("email")
            client.mobile = request.POST.get("mobile")
            client.country = request.POST.get("country")
            client.state = request.POST.get("state")
            client.district = request.POST.get("district")
            client.city = request.POST.get("city")
            client.area = request.POST.get("area")
            client.pincode = request.POST.get("pincode")
            client.save()
            data = {"error":False, "client_id":client.id}
            return HttpResponse(json.dumps(data))


@login_required
def update_clientprofile(request,client_id):
    if request.method == "GET":
        client = Client.objects.get(id=client_id)
        return render(request,"updateclientprofile.html",{"client":client, "client_id":client_id})
    else:
        client = Client.objects.get(id=client_id)
        client.photo=request.FILES.get("photo")
        client.signature = request.FILES.get("signature")
        client.save()
        return HttpResponseRedirect('/clientprofile/'+client_id+'/')


@login_required
def view_client(request):
    branch_list = Branch.objects.all()
    client_list = Client.objects.all()
    group = Group.objects.all()
    return render(request,"viewclient.html",{"branch_list":branch_list, "client_list":client_list, "group":group})


@login_required
def delete_client(request,client_id):
    client = Client.objects.get(id=client_id)
    client_list = Client.objects.all()
    client.delete()
    return render(request,"viewclient.html", {"client_list":client_list})


@login_required
def create_user(request):
    if request.method == "GET":
        data = {}
        branches = Branch.objects.all()
        return render(request, "createuser.html", {"data":data, "branches":branches})
    else:
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user_name = request.POST.get("username")
            user_password = request.POST.get("password")
            email = request.POST.get("email")
            user = User.objects.create_user(username=user_name, email=email, password=user_password, branch=Branch.objects.get(id=request.POST.get('branch')))
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.gender = request.POST.get("gender")
            user.user_roles = request.POST.get("user_roles")
            user.country = request.POST.get("country")
            user.state = request.POST.get("state")
            user.district = request.POST.get("district")
            user.city = request.POST.get("city")
            user.area = request.POST.get("area")
            user.pincode = request.POST.get("pincode")
            date_of_birth1 = request.POST.get("date_of_birth")
            mobile1 = request.POST.get("mobile")
            if mobile1:
                user.mobile = mobile1
            if date_of_birth1:
                datestring_format = datetime.datetime.strptime(request.POST.get("date_of_birth"),"%m/%d/%Y").strftime('%Y-%m-%d')
                dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
                user.date_of_birth = dateconvert
            user.save()
            data = {"error":False, "user_id":user.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":user_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def edit_user(request, user_id):
    if request.method == "GET":
        user = User.objects.get(id=user_id)
        return render(request, "edituser.html", {"user":user, "user_id":user.id})
    else:
        user = User.objects.get(id=user_id)
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.country = request.POST.get("country")
        user.state = request.POST.get("state")
        user.district = request.POST.get("district")
        user.city = request.POST.get("city")
        user.area = request.POST.get("area")
        user.pincode = request.POST.get("pincode")
        mobile1 = request.POST.get("mobile")
        if mobile1:
            user.mobile = mobile1
        user.save()
        data = {"error":False, "user_id":user.id}
        return HttpResponse(json.dumps(data))


@login_required
def user_profile(request, user_id):
    selecteduser = User.objects.get(id=user_id)
    return render(request, "userprofile.html", {"selecteduser":selecteduser})


@login_required
def users_list (request):
    list_of_users = User.objects.filter(is_admin=0)
    return render(request,"listofusers.html", {"list_of_users":list_of_users})


@login_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    list_of_users = User.objects.filter(is_admin=0)
    return render(request, "listofusers.html", {"list_of_users":list_of_users})


@login_required
def create_group(request):
    if request.method == "GET":
        data = {}
        branches = Branch.objects.all()
        return render(request, "creategroup.html", {"data":data, "branches":branches})
    else:
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            name = request.POST.get("name")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            account_number = request.POST.get("account_number")
            datestring_format = datetime.datetime.strptime(request.POST.get("activation_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            activation_date = dateconvert
            branch = Branch.objects.get(id=request.POST.get("branch"))
            group = Group.objects.create(name=name, created_by=created_by, account_number=account_number, activation_date=activation_date, branch=branch)
            data = {"error":False, "group_id":group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":group_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def group_profile(request, group_id):
    group = Group.objects.get(id=group_id)
    clients_list = group.clients.all()
    clients_count = group.clients.all().count()
    if GroupMeetings.objects.filter(group_id=group.id):
        latest_group_meeting = GroupMeetings.objects.filter(group_id=group.id).order_by('-id')[0]
        return render(request, "groupprofile.html", {"group":group, "clients_list":clients_list, "clients_count":clients_count, "latest_group_meeting":latest_group_meeting})
    else:
        return render(request, "groupprofile.html", {"group":group, "clients_list":clients_list, "clients_count":clients_count})


@login_required
def assign_staff_to_group(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        users_list = User.objects.filter(is_admin=0)
        return render(request, "assignstaff.html", {"group":group, "users_list":users_list})
    else:
        staff_id = request.POST.get("staff")
        user = User.objects.get(id=staff_id)
        group = Group.objects.get(id=group_id)
        group.staff = user
        group.save()
        data = {"error":False, "group_id":group.id}
        return HttpResponse(json.dumps(data))


@login_required
def addmembers_to_group(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        clients_list = Client.objects.filter(status="UnAssigned", is_active=1)
        return render(request, "addmember.html", {"group":group, "clients_list":clients_list})
    else:
        addmember_form = AddMemberForm(request.POST)
        if addmember_form.is_valid():
            group = Group.objects.get(id=group_id)
            clients = request.POST.getlist("clients")
            for client in clients:
                client = Client.objects.get(id=client)
                group.clients.add(client)
                group.save()
                client.status = "Assigned"
                client.save()
            data = {"error":False, "group_id":group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":addmember_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def viewmembers_under_group(request, group_id):
    group = Group.objects.get(id=group_id)
    clients_list = group.clients.all()
    clients_count = group.clients.all().count()
    return render(request, "viewmembers.html", {"group":group, "clients_list":clients_list, "clients_count":clients_count})


@login_required
def groups_list(request):
    groups_list = Group.objects.all()
    return render(request, "listofgroups.html", {"groups_list":groups_list})


@login_required
def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if group.staff and group.clients.all().count():
        return HttpResponse("This group can't be deleted")
    else:
        if not group.staff and not group.clients.all().count():
            group.delete()
            return HttpResponse("Group deleted successfully")


@login_required
def removemembers_from_group(request, group_id, client_id):
    group = Group.objects.get(id=group_id)
    client = Client.objects.get(id=client_id)
    group.clients.remove(client)
    group.save()
    client.status = "UnAssigned"
    client.save()
    return HttpResponseRedirect('/groupprofile/'+group_id+'/')


@login_required
def group_meetings(request, group_id):
    group = Group.objects.get(id=group_id)
    return HttpResponse("List of Group of Meetings")


@login_required
def add_group_meeting(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        if GroupMeetings.objects.filter(group_id=group.id):
            latest_group_meeting = GroupMeetings.objects.filter(group_id=group.id).order_by('-id')[0]
            return render(request, "add_group_meeting.html", {"group":group, "latest_group_meeting":latest_group_meeting})
        else:
            return render(request, "add_group_meeting.html", {"group":group})
    else:
        group = Group.objects.get(id=group_id)
        datestring_format = datetime.datetime.strptime(request.POST.get("meeting_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
        dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
        meeting_date = dateconvert
        meeting_time = request.POST.get("meeting_time")
        group_meeting = GroupMeetings.objects.create(meeting_date=meeting_date, meeting_time=meeting_time, group=group)
        return HttpResponseRedirect('/groupprofile/'+group_id+'/')


@login_required
def client_savings_application(request, client_id):
    if request.method == "GET":
        client = Client.objects.get(id=client_id)
        count = SavingsAccount.objects.all().count()
        account_no = "%s%s%d" % ("00B00", client.branch.id,count+1)
        return render(request, "client_savings_application.html", {"client":client, "account_no":account_no})
    else:
        form = ClientSavingsAccountForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(id=client_id)
            account_no = request.POST.get("account_no")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            datestring_format = datetime.datetime.strptime(request.POST.get("opening_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            opening_date = dateconvert
            min_required_balance = request.POST.get("min_required_balance")
            annual_interest_rate = request.POST.get("annual_interest_rate")
            savingsaccount = SavingsAccount.objects.create(account_no=account_no, client=client, status="Applied", created_by=created_by, opening_date=opening_date, min_required_balance=min_required_balance, annual_interest_rate=annual_interest_rate)
            if request.POST.get("savings_balance"):
                savingsaccount.savings_balance = request.POST.get("savings_balance")
                savingsaccount.save()
            data = {"error":False, "client_id":client.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_savings_account(request,client_id):
    client = Client.objects.get(id=client_id)
    savingsaccount = SavingsAccount.objects.get(client=client)
    return render(request, "client_savings_account.html", {"client":client, "savingsaccount":savingsaccount})


@login_required
def group_savings_application(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        count = SavingsAccount.objects.all().count()
        account_no = "%s%s%d" % ("00B00",group.branch.id,count+1)
        return render(request, "group_savings_application.html", {"group":group, "account_no":account_no})
    else:
        group_savingsaccount_form = GroupSavingsAccountForm(request.POST)
        if group_savingsaccount_form.is_valid():
            group = Group.objects.get(id=group_id)
            account_no = request.POST.get("account_no")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            datestring_format = datetime.datetime.strptime(request.POST.get("opening_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            opening_date = dateconvert
            min_required_balance = request.POST.get("min_required_balance")
            annual_interest_rate = request.POST.get("annual_interest_rate")
            savings_balance = request.POST.get("savings_balance")
            if decimal.Decimal(savings_balance) >= decimal.Decimal(min_required_balance) :
                savings_account = SavingsAccount.objects.create(account_no=account_no, group=group, created_by=created_by, status="Applied", opening_date=opening_date, min_required_balance=min_required_balance, annual_interest_rate=annual_interest_rate)
                savings_account.savings_balance = request.POST.get("savings_balance")
                savings_account.total_deposits = request.POST.get("savings_balance")
                savings_account.save()
                data = {"error":False, "group_id":group.id}
                return HttpResponse(json.dumps(data))
            elif decimal.Decimal(savings_balance) < decimal.Decimal(min_required_balance) :
                data = {"error":True, "message":"Balance should be greater than or equal to minimun required balance"}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":group_savingsaccount_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def group_savings_account(request, group_id):
    group = Group.objects.get(id=group_id)
    savings_account = SavingsAccount.objects.get(group=group)
    return render(request, "group_savings_account.html", {"group":group, "savings_account":savings_account})


@login_required
def approve_savings(request, savingsaccount_id):
    if request.method == "POST":
        savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
        if savings_account.group:
            savings_account.status = "Approved"
            savings_account.save()
            data = {"error":False, "group_id":savings_account.group.id}
            return HttpResponse(json.dumps(data))

        elif savings_account.client:
            savings_account.status = "Approved"
            savings_account.save()
            data = {"error":False, "client_id":savings_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def reject_savings(request, savingsaccount_id):
    if request.method == "POST":
        savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
        if savings_account.group:
            savings_account.status = "Rejected"
            savings_account.save()
            data = {"error":False, "group_id":savings_account.group.id}
            return HttpResponse(json.dumps(data))

        elif savings_account.client:
            savings_account.status = "Rejected"
            savings_account.save()
            data = {"error":False, "client_id":savings_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def close_savings(request, savingsaccount_id):
    if request.method == "POST":
        savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
        if savings_account.group:
            savings_account.status = "Closed"
            savings_account.save()
            data = {"error":False, "group_id":savings_account.group.id}
            return HttpResponse(json.dumps(data))

        elif savings_account.client:
            savings_account.status = "Closed"
            savings_account.save()
            data = {"error":False, "client_id":savings_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def withdraw_savings(request, savingsaccount_id):
    if request.method == "POST":
        savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
        if savings_account.group:
            savings_account.status = "Withdrawn"
            savings_account.save()
            data = {"error":False, "group_id":savings_account.group.id}
            return HttpResponse(json.dumps(data))

        elif savings_account.client:
            savings_account.status = "Withdrawn"
            savings_account.save()
            data = {"error":False, "client_id":savings_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def group_savings_transactions(request, savingsaccount_id):
    if request.method == "POST":
        savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
        staff = User.objects.get(username=request.user)
        transaction_type = request.POST.get("transaction_type")
        transaction_amount = request.POST.get("transaction_amount")
        if savings_account.group:
            if request.POST.get("transaction_type") == "Deposit":
                savings_transactions = SavingsTransactions.objects.create(savings_account=savings_account, transaction_type=transaction_type, transaction_amount=transaction_amount, staff=staff)
                savings_account.savings_balance += decimal.Decimal(transaction_amount)
                savings_account.total_deposits += decimal.Decimal(transaction_amount)
                savings_account.save()
                data = {"error":False, "group_id":savings_account.group.id}
                return HttpResponse(json.dumps(data))

            elif request.POST.get("transaction_type") == "Withdraw":
                savings_transactions = SavingsTransactions.objects.create(savings_account=savings_account, transaction_type=transaction_type, transaction_amount=transaction_amount, staff=staff)
                savings_account.savings_balance -= decimal.Decimal(transaction_amount)
                savings_account.total_withdrawals += decimal.Decimal(transaction_amount)
                savings_account.save()
                data = {"error":False, "group_id":savings_account.group.id}
                return HttpResponse(json.dumps(data))
        else:
            return HttpResponse("No Group")


@login_required
def group_loan_application(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        count = LoanAccount.objects.all().count()
        account_no = "%s%s%d" % ("00B00",group.branch.id,count+1)
        return render(request, "group_loan_application.html", {"group":group, "account_no":account_no})
    else:
        group_loanaccount_form = GroupLoanAccountForm(request.POST)
        if group_loanaccount_form.is_valid():
            group = Group.objects.get(id=group_id)
            account_no = request.POST.get("account_no")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            loan_amount = request.POST.get("loan_amount")
            loan_repayment_period = request.POST.get("loan_repayment_period")
            loan_repayment_every = request.POST.get("loan_repayment_every")
            annual_interest_rate = request.POST.get("annual_interest_rate")
            loanpurpose_description = request.POST.get("loanpurpose_description")
            loan_account = LoanAccount.objects.create(account_no=account_no, group=group, created_by=created_by, status="Applied", loan_amount=loan_amount, loan_repayment_period=loan_repayment_period, loan_repayment_every=loan_repayment_every, annual_interest_rate=annual_interest_rate, loanpurpose_description=loanpurpose_description)
            loan_account.interest_charged = decimal.Decimal((decimal.Decimal(loan_account.loan_amount) * decimal.Decimal(int(loan_account.loan_repayment_period) / 12) * decimal.Decimal(loan_account.annual_interest_rate)) / 100)
            total_loan_repayable = decimal.Decimal(loan_account.interest_charged) + decimal.Decimal(loan_account.loan_amount)
            loan_account.loan_repayment_amount = decimal.Decimal(int(loan_account.loan_repayment_every) * (decimal.Decimal(total_loan_repayable) / decimal.Decimal(loan_account.loan_repayment_period)))
            loan_account.total_loan_balance = decimal.Decimal(decimal.Decimal(loan_account.interest_charged) + decimal.Decimal(loan_account.loan_amount))
            loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":group_loanaccount_form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def clientsavingstransaction(request,savingsaccount_id,client_id):
    if request.method == "POST":
        client = Client.objects.get(id=client_id)
        savingsaccount = SavingsAccount.objects.get(client=client)
        if savingsaccount.status == "Approved":
            transaction_type = request.POST.get("transaction_type")
            staff = User.objects.get(username=request.user)
            if transaction_type == "Deposit":
                transaction_amount = request.POST.get("transaction_amount")
                savingstransactions = SavingsTransactions.objects.create(staff=staff, transaction_type=transaction_type, savings_account=savingsaccount, transaction_amount=transaction_amount)
                savings_balance = savingsaccount.savings_balance
                savingsaccount.savings_balance = decimal.Decimal(savings_balance) + decimal.Decimal(transaction_amount)
                savingsaccount.save()
                savingsaccount.total_deposits = savingsaccount.savings_balance
                savingsaccount.save()
                data = {"error":False, "client_id":client_id}
                return HttpResponse(json.dumps(data))

            elif transaction_type == "Withdraw":
                transaction_amount = request.POST.get("transaction_amount")
                savingstransactions = SavingsTransactions.objects.create(staff=staff, transaction_type=transaction_type, savings_account=savingsaccount, transaction_amount=transaction_amount)
                savings_balance = savingsaccount.savings_balance
                savingsaccount.savings_balance = decimal.Decimal(savings_balance) - decimal.Decimal(transaction_amount)
                savingsaccount.save()
                savingsaccount.total_withdrawals = decimal.Decimal(savingsaccount.total_withdrawals) + decimal.Decimal(transaction_amount)
                savingsaccount.save()
                data = {"error":False, "client_id":client_id}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error":True, "message":"Not Deposited", "client_id":client_id}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error":True,"message_pending":"Savings Account is under pending for approval", "client_id":client_id}
            return HttpResponse(json.dumps(data))


@login_required
def client_loan_application(request, client_id):
    if request.method == "GET":
        client = Client.objects.get(id=client_id)
        count = LoanAccount.objects.all().count()
        account_no = "%s%s%d" % ("00B00",client.branch.id,count+1)
        return render(request, "client_loan_application.html", {"client":client, "account_no":account_no})
    else:
        form = ClientLoanAccountForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(id=client_id)
            account_no = request.POST.get("account_no")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            loan_amount = request.POST.get("loan_amount")
            loan_repayment_period = request.POST.get("loan_repayment_period")
            loan_repayment_every = request.POST.get("loan_repayment_every")
            annual_interest_rate = request.POST.get("annual_interest_rate")
            loanpurpose_description = request.POST.get("loanpurpose_description")
            loanaccount = LoanAccount.objects.create(account_no=account_no, client=client, status="Applied", created_by=created_by, loan_amount=loan_amount, loan_repayment_period=loan_repayment_period, loan_repayment_every=loan_repayment_every, annual_interest_rate=annual_interest_rate, loanpurpose_description=loanpurpose_description)
            interest_charged = ((decimal.Decimal(loanaccount.loan_amount) *(decimal.Decimal(loanaccount.annual_interest_rate) / 12)) / 100)
            loanaccount.interest_charged = (decimal.Decimal(interest_charged) * decimal.Decimal(loanaccount.loan_repayment_period))
            loanamount= (decimal.Decimal(loanaccount.loan_amount)  + decimal.Decimal(loanaccount.interest_charged))
            loan_repayment_amount = (decimal.Decimal(loanamount)) / (decimal.Decimal(loanaccount.loan_repayment_period))
            loanaccount.loan_repayment_amount = (decimal.Decimal(loan_repayment_amount) * decimal.Decimal(loanaccount.loan_repayment_every))
            loanaccount.total_loan_balance = ((decimal.Decimal(loanaccount.loan_amount)) + (decimal.Decimal(loanaccount.interest_charged)))
            loanaccount.save()
            data = {"error":False, "client_id":client.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_loan_account(request,client_id):
    client = Client.objects.get(id=client_id)
    loanaccount = LoanAccount.objects.get(client = client)
    total = (decimal.Decimal(loanaccount.total_loan_amount_repaid) + decimal.Decimal(loanaccount.total_interest_repaid))
    loanamount_withInterest = ((decimal.Decimal(loanaccount.loan_amount)) + (decimal.Decimal(loanaccount.interest_charged)))
    return render(request, "client_loan_account.html", {"client":client, "loanaccount":loanaccount, "loanamount_withInterest":loanamount_withInterest, "total":total})


@login_required
def approve_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Approved"
            loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))

        elif loan_account.client:
            loan_account.status = "Approved"
            loan_account.save()
            data = {"error":False, "client_id":loan_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def reject_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Rejected"
            loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))

        elif loan_account.client:
            loan_account.status = "Rejected"
            loan_account.save()
            data = {"error":False, "client_id":loan_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def close_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Closed"
            loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))

        elif loan_account.client:
            loan_account.status = "Closed"
            loan_account.save()
            data = {"error":False, "client_id":loan_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def withdraw_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Withdrawn"
            loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
            
        elif loan_account.client:
            loan_account.status = "Withdrawn"
            loan_account.save()
            data = {"error":False, "client_id":loan_account.client.id}
            return HttpResponse(json.dumps(data))


@login_required
def client_loan_transaction(request,loanaccount_id,client_id):
    if request.method == "POST":
        client = Client.objects.get(id=client_id)
        loanaccount = LoanAccount.objects.get(client=client)
        if loanaccount.status == "Approved":
            if loanaccount.total_loan_balance != 0:
                latest_client_loan_transaction = LoanTransactions.objects.filter(loan_account_id=loanaccount.id).order_by('-id')[0]
                d = datetime.datetime.now()
                if int(latest_client_loan_transaction.transaction_date.strftime('%m')) + 1 == d.month :
                    staff = User.objects.get(username=request.user)
                    transaction_amount = request.POST.get("transaction_amount")
                    if loanaccount.client:
                        transaction_amount = request.POST.get("transaction_amount")
                        if decimal.Decimal(transaction_amount) == decimal.Decimal(loanaccount.loan_repayment_amount):
                            loantransaction = LoanTransactions.objects.create(transaction_amount=transaction_amount, staff=staff,loan_account=loanaccount)
                            interest_charged = ((decimal.Decimal(loanaccount.loan_amount) *(decimal.Decimal(loanaccount.annual_interest_rate) / 12)) / 100)
                            total_interest_repaid = (decimal.Decimal(interest_charged) * decimal.Decimal(loanaccount.loan_repayment_every))
                            loan_repayment_amount = ((decimal.Decimal(loanaccount.loan_amount)) / (decimal.Decimal(loanaccount.loan_repayment_period)))
                            total_loan_amount_repaid = (decimal.Decimal(loan_repayment_amount) * decimal.Decimal(loanaccount.loan_repayment_every))
                            loanaccount.total_loan_amount_repaid += decimal.Decimal(total_loan_amount_repaid)
                            loanaccount.total_interest_repaid += decimal.Decimal(total_interest_repaid)
                            total = (decimal.Decimal(loanaccount.total_loan_amount_repaid) + decimal.Decimal(loanaccount.total_interest_repaid))
                            loanaccount.total_loan_balance = (decimal.Decimal(loanaccount.total_loan_balance) - decimal.Decimal(transaction_amount))
                            loanaccount.save()
                            data = {"error":False, "client_id":client_id}
                            return HttpResponse(json.dumps(data))
                        else:
                            data = {"error":True, "message":"Deposit Amount should be equal to Loan Repayment Amount ", "client_id":client_id}
                            return HttpResponse(json.dumps(data))
                    else:
                        return HttpResponse(" Select Client profile ")
                else:
                    data = {"error":True,"message_balance":"Next Transaction should be done Next month", "client_id":client_id}
                    return HttpResponse(json.dumps(data)) 
            else:
                data = {"error":True,"message_balance":"Loan has been completed", "client_id":client_id}
                return HttpResponse(json.dumps(data))       
        else:
            data = {"error":True,"message_pending":"Loan Account is under pending for approval", "client_id":client_id}
            return HttpResponse(json.dumps(data))


@login_required
def listofclient_loan_deposits(request, loanaccount_id):
    loanaccount = LoanAccount.objects.get(id=loanaccount_id)
    loantransactions_list = LoanTransactions.objects.filter(loan_account=loanaccount_id)
    return render(request, "view_clientloan_deposits.html", {"loanaccount":loanaccount, "loantransactions_list":loantransactions_list, "loanaccount_client":loanaccount.client})


@login_required
def listofclient_savings_deposits(request,savingsaccount_id):
    savingsaccount = SavingsAccount.objects.get(id=savingsaccount_id)
    savingstransactions_list = SavingsTransactions.objects.filter(savings_account=savingsaccount_id, transaction_type = "Deposit")
    return render(request, "listof_clientsavingsdeposits.html", {"savingsaccount":savingsaccount, "savingstransactions_list":savingstransactions_list, "savingsaccount_client":savingsaccount.client})


@login_required
def listofclient_savings_withdrawals(request,savingsaccount_id):
    savingsaccount = SavingsAccount.objects.get(id=savingsaccount_id)
    savingstransactions_list = SavingsTransactions.objects.filter(savings_account=savingsaccount_id, transaction_type = "Withdraw")
    return render(request, "listof_clientsavingswithdrawals.html", {"savingsaccount":savingsaccount, "savingstransactions_list":savingstransactions_list})    


@login_required
def group_loan_account(request, group_id):
    group = Group.objects.get(id=group_id)
    loan_account = LoanAccount.objects.get(group=group)
    return render(request, "group_loan_account.html", {"group":group, "loan_account":loan_account})


@login_required
def group_loan_transactions(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.status == "Approved":
            if loan_account.loan_issued_date :
                if decimal.Decimal(loan_account.total_loan_balance) :
                    latest_group_loan_transaction = LoanTransactions.objects.filter(loan_account_id=loan_account.id).order_by('-id')[0]
                    d = datetime.datetime.now()
                    if int(latest_group_loan_transaction.transaction_date.strftime('%m')) + 1 == d.month :
                        staff = User.objects.get(username=request.user)
                        transaction_amount = request.POST.get("transaction_amount")
                        if loan_account.group:
                            if decimal.Decimal(transaction_amount) == decimal.Decimal(loan_account.loan_repayment_amount) :
                                loan_transaction = LoanTransactions.objects.create(loan_account=loan_account, transaction_amount=transaction_amount, staff=staff)
                                interest_paid = decimal.Decimal(int(loan_account.loan_repayment_every) * (decimal.Decimal(loan_account.interest_charged) / decimal.Decimal(loan_account.loan_repayment_period)))
                                loan_amount_paid = decimal.Decimal(transaction_amount) - decimal.Decimal(interest_paid)
                                loan_account.total_loan_amount_repaid += decimal.Decimal(loan_amount_paid)
                                loan_account.total_interest_repaid += decimal.Decimal(interest_paid)
                                loan_account.total_loan_paid = decimal.Decimal(decimal.Decimal(loan_account.total_loan_amount_repaid) + decimal.Decimal(loan_account.total_interest_repaid))
                                loan_account.total_loan_balance = decimal.Decimal(decimal.Decimal(loan_account.total_loan_balance) - decimal.Decimal(transaction_amount))
                                loan_account.save()
                                data = {"error":False, "group_id":loan_account.group.id}
                                return HttpResponse(json.dumps(data))
                            else:
                                data = {"error":True, "amount_message":"Loan Amount must be equal to the Repayment Amount"}
                                return HttpResponse(json.dumps(data))
                        else:
                            return HttpResponse("No Group")
                    else:
                        data = {"error":True, "message":"Loan Amount has been sucessfully deposited for this month. Next deposit is to be done next month", "group_id":loan_account.group.id}
                        return HttpResponse(json.dumps(data))
                else:
                    data = {"error":True, "message":"Loan has been cleared sucessfully.", "group_id":loan_account.group.id}
                    return HttpResponse(json.dumps(data))
            else:
                data = {"error":True, "message":"Loan has not yet issued.", "group_id":loan_account.group.id}
                return HttpResponse(json.dumps(data))
        elif loan_account.status == "Applied":
            data = {"error":True, "message":"This account is under pending for approval.", "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        elif loan_account.status == "Rejected":
            data = {"error":True, "message":"Account has been Rejected.", "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        elif loan_account.status == "Closed":
            data = {"error":True, "message":"Account has been Closed.", "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))


@login_required
def view_grouploan_deposits(request, loanaccount_id):
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    loan_transactions = loan_account.loantransactions_set.all()
    return render(request, "listof_grouploan_deposits.html", {"loan_account":loan_account, "loan_transactions":loan_transactions, "group":loan_account.group})


@login_required
def view_groupsavings_deposits(request, savingsaccount_id):
    savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
    savings_deposit_transactions = savings_account.savingstransactions_set.filter(transaction_type="Deposit")
    return render(request, "listof_groupsavings_deposits.html", {"savings_account":savings_account, "savings_deposit_transactions":savings_deposit_transactions, "group":savings_account.group})


@login_required
def view_groupsavings_withdrawals(request, savingsaccount_id):
    savings_account = SavingsAccount.objects.get(id=savingsaccount_id)
    savings_withdrawal_transactions = savings_account.savingstransactions_set.filter(transaction_type="Withdraw")
    return render(request, "listof_groupsavings_withdrawals.html", {"savings_account":savings_account, "savings_withdrawal_transactions":savings_withdrawal_transactions, "group":savings_account.group})


@login_required
def issue_group_loan(request, loanaccount_id):
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    loan_account.loan_issued_date = datetime.datetime.now()
    loan_account.loan_issued_by = request.user
    loan_account.save()
    group_id = str(loan_account.group.id)
    return HttpResponseRedirect('/grouploanaccount/'+group_id+'/')

from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import login, authenticate, logout
import json
from micro_admin.models import User, Branch, Group, Client, CLIENT_ROLES, GroupMeetings, SavingsAccount, LoanAccount, Receipts, RECEIPT_TYPES, FixedDeposits, PAYMENT_TYPES, Payments, RecurringDeposits
from micro_admin.forms import BranchForm, UserForm, EditbranchForm, GroupForm, ClientForm, AddMemberForm, EditclientForm, GroupSavingsAccountForm, GroupLoanAccountForm, ClientSavingsAccountForm, ClientLoanAccountForm, ReceiptForm, FixedDepositForm, PaymentForm, ReccuringDepositForm
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
            print form.errors
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
            savings_account = SavingsAccount.objects.create(account_no=account_no, group=group, created_by=created_by, status="Applied", opening_date=opening_date, min_required_balance=min_required_balance, annual_interest_rate=annual_interest_rate)
            data = {"error":False, "group_id":group.id}
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
def group_loan_application(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        count = LoanAccount.objects.all().count()
        account_no = "%d" % (count+1)
        return render(request, "group_loan_application.html", {"group":group, "account_no":account_no})
    else:
        group_loanaccount_form = GroupLoanAccountForm(request.POST)
        if group_loanaccount_form.is_valid():
            group = Group.objects.get(id=group_id)
            account_no = request.POST.get("account_no")
            interest_type = request.POST.get("interest_type")
            created_by = User.objects.get(username=request.POST.get("created_by"))
            loan_amount = request.POST.get("loan_amount")
            loan_repayment_period = request.POST.get("loan_repayment_period")
            loan_repayment_every = request.POST.get("loan_repayment_every")
            annual_interest_rate = request.POST.get("annual_interest_rate")
            loanpurpose_description = request.POST.get("loanpurpose_description")
            loan_account = LoanAccount.objects.create(account_no=account_no, interest_type=interest_type, group=group, created_by=created_by, status="Applied", loan_amount=loan_amount, loan_repayment_period=loan_repayment_period, loan_repayment_every=loan_repayment_every, annual_interest_rate=annual_interest_rate, loanpurpose_description=loanpurpose_description)

            interest_charged = decimal.Decimal(((decimal.Decimal(loan_account.loan_amount) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
            loan_account.interest_charged = decimal.Decimal((decimal.Decimal(interest_charged)) * int(loan_account.loan_repayment_period))
            loan_account.loan_repayment_amount = ((int(loan_account.loan_repayment_every) * (decimal.Decimal(loan_account.loan_amount))) / (decimal.Decimal(loan_account.loan_repayment_period))) + (int(loan_account.loan_repayment_every) * (decimal.Decimal(interest_charged)))
            loan_account.total_loan_balance = decimal.Decimal(decimal.Decimal(loan_account.loan_amount))
            loan_account.save()
            clients_list = group.clients.all()
            count = group.clients.all().count()
            for client in clients_list:
                last_loan_account = LoanAccount.objects.filter().order_by("-id")[0]
                client_account_no = int(last_loan_account.account_no)+1
                client_loan_amount = decimal.Decimal(decimal.Decimal(loan_amount)/decimal.Decimal(count))
                client_loan_account = LoanAccount.objects.create(account_no=client_account_no, interest_type=interest_type, client=client, created_by=created_by, status="Applied", loan_amount=client_loan_amount, loan_repayment_period=loan_repayment_period, loan_repayment_every=loan_repayment_every, annual_interest_rate=annual_interest_rate, loanpurpose_description=loanpurpose_description)
                interest_charged = decimal.Decimal(((decimal.Decimal(client_loan_account.loan_amount) *(decimal.Decimal(client_loan_account.annual_interest_rate) / 12)) / 100))
                client_loan_account.interest_charged = decimal.Decimal((decimal.Decimal(interest_charged)) * int(client_loan_account.loan_repayment_every))
                client_loan_account.loan_repayment_amount = decimal.Decimal(((int(client_loan_account.loan_repayment_every) * (decimal.Decimal(client_loan_account.loan_amount)) / (decimal.Decimal(client_loan_account.loan_repayment_period))) + (decimal.Decimal(client_loan_account.interest_charged))))
                client_loan_account.total_loan_balance = decimal.Decimal(decimal.Decimal(client_loan_account.loan_amount))
                client_loan_account.save()
            data = {"error":False, "loanaccount_id":loan_account.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":group_loanaccount_form.errors}
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
            interest_type = request.POST.get("interest_type")
            loanaccount = LoanAccount.objects.create(account_no=account_no, interest_type=interest_type, client=client, status="Applied", created_by=created_by, loan_amount=loan_amount, loan_repayment_period=loan_repayment_period, loan_repayment_every=loan_repayment_every, annual_interest_rate=annual_interest_rate, loanpurpose_description=loanpurpose_description)
            if loanaccount.interest_type == "Flat":
                interest_charged = decimal.Decimal(((decimal.Decimal(loanaccount.loan_amount) *(decimal.Decimal(loanaccount.annual_interest_rate) / 12)) / 100))
                loanaccount.interest_charged = decimal.Decimal((decimal.Decimal(interest_charged)) * int(loanaccount.loan_repayment_every))
                loanaccount.loan_repayment_amount = decimal.Decimal(((int(loanaccount.loan_repayment_every) * (decimal.Decimal(loanaccount.loan_amount)) / (decimal.Decimal(loanaccount.loan_repayment_period))) + (decimal.Decimal(loanaccount.interest_charged))))
                print loanaccount.loan_repayment_amount
                loanaccount.total_loan_balance = decimal.Decimal(decimal.Decimal(loanaccount.loan_amount))
                loanaccount.save()
                data = {"error":False, "client_id":client.id}
                return HttpResponse(json.dumps(data))
            elif loanaccount.interest_type == "Declining":
                interest_charged = decimal.Decimal(((decimal.Decimal(loanaccount.loan_amount) *(decimal.Decimal(loanaccount.annual_interest_rate) / 12)) / 100))
                loanaccount.interest_charged = decimal.Decimal(decimal.Decimal(interest_charged) * int(loanaccount.loan_repayment_every))
                loanaccount.loan_repayment_amount = decimal.Decimal(((int(loanaccount.loan_repayment_every) * (decimal.Decimal(loanaccount.loan_amount)) / (decimal.Decimal(loanaccount.loan_repayment_period))) + (decimal.Decimal(loanaccount.interest_charged))))
                loanaccount.total_loan_balance = (decimal.Decimal(loanaccount.loan_amount))
                loanaccount.save()
                data = {"error":False, "client_id":client.id}
                return HttpResponse(json.dumps(data))
        else:
            print form.errors
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_loan_account(request,loanaccount_id):
    loanaccount = LoanAccount.objects.get(id=loanaccount_id)
    return render(request, "client_loan_account.html", {"client":loanaccount.client, "loanaccount":loanaccount})


@login_required
def group_loan_account(request, loanaccount_id):
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    return render(request, "group_loan_account.html", {"group":loan_account.group, "loan_account":loan_account})


@login_required
def approve_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Approved"
            loan_account.approved_date = datetime.datetime.now()
            loan_account.save()
            group = Group.objects.get(id=loan_account.group.id)
            clients_list = group.clients.all()
            for client in clients_list:
                client_loan_account = LoanAccount.objects.get(client=client)
                client_loan_account.status = "Approved"
                client_loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True}
            return HttpResponse(json.dumps(data))


@login_required
def reject_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Rejected"
            loan_account.save()
            group = Group.objects.get(id=loan_account.group.id)
            clients_list = group.clients.all()
            for client in clients_list:
                client_loan_account = LoanAccount.objects.get(client=client)
                client_loan_account.status = "Rejected"
                client_loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True}
            return HttpResponse(json.dumps(data))

@login_required
def close_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Closed"
            loan_account.save()
            group = Group.objects.get(id=loan_account.group.id)
            clients_list = group.clients.all()
            for client in clients_list:
                client_loan_account = LoanAccount.objects.get(client=client)
                client_loan_account.status = "Closed"
                client_loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True}
            return HttpResponse(json.dumps(data))


@login_required
def withdraw_loan(request, loanaccount_id):
    if request.method == "POST":
        loan_account = LoanAccount.objects.get(id=loanaccount_id)
        if loan_account.group:
            loan_account.status = "Withdrawn"
            loan_account.save()
            group = Group.objects.get(id=loan_account.group.id)
            clients_list = group.clients.all()
            for client in clients_list:
                client_loan_account = LoanAccount.objects.get(client=client)
                client_loan_account.status = "Withdrawn"
                client_loan_account.save()
            data = {"error":False, "group_id":loan_account.group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True}
            return HttpResponse(json.dumps(data))


@login_required
def view_grouploan_deposits(request, group_id):
    group = Group.objects.get(id=group_id)
    loan_account = LoanAccount.objects.get(group=group)
    receipts_list = Receipts.objects.filter(group=group).exclude(demand_loanprinciple_amount_atinstant=0, demand_loaninterest_amount_atinstant=0)
    count = Receipts.objects.filter(group=group).exclude(demand_loanprinciple_amount_atinstant=0, demand_loaninterest_amount_atinstant=0).count()
    return render(request, "listof_grouploan_deposits.html", {"loan_account":loan_account, "receipts_list":receipts_list, "group":group, "count":count})


@login_required
def view_groupsavings_deposits(request, group_id):
    group = Group.objects.get(id=group_id)
    savings_account = SavingsAccount.objects.get(group=group)
    receipts_list = Receipts.objects.filter(group=group).exclude(savingsdeposit_thrift_amount=0)
    count = Receipts.objects.filter(group=group).exclude(savingsdeposit_thrift_amount=0).count()
    return render(request, "listof_groupsavings_deposits.html", {"savings_account":savings_account, "receipts_list":receipts_list, "group":group, "count":count})


@login_required
def view_groupsavings_withdrawals(request, group_id):
    group = Group.objects.get(id=group_id)
    savings_withdrawals_list = Payments.objects.filter(group=group, payment_type="SavingsWithdrawal")
    count = Payments.objects.filter(group=group, payment_type="SavingsWithdrawal").count()
    return render(request, "listof_groupsavings_withdrawals.html", {"count":count, "savings_withdrawals_list":savings_withdrawals_list, "group":group})


@login_required
def listofclient_loan_deposits(request, client_id):
    loanaccount = LoanAccount.objects.get(client=client_id)
    receipts_lists = Receipts.objects.filter(client=client_id).exclude(loanprinciple_amount=0, loaninterest_amount=0)
    return render(request, "view_clientloan_deposits.html", {"loanaccount":loanaccount, "receipts_lists":receipts_lists})


@login_required
def listofclient_savings_deposits(request,client_id):
    savingsaccount = SavingsAccount.objects.get(client=client_id)
    receipts_lists = Receipts.objects.filter(client=client_id).exclude(savingsdeposit_thrift_amount=0)
    return render(request, "listof_clientsavingsdeposits.html", {"savingsaccount":savingsaccount, "receipts_lists":receipts_lists})


@login_required
def listofclient_savings_withdrawals(request,client_id):
    client = Client.objects.get(id=client_id)
    savings_withdrawals_list = Payments.objects.filter(client=client, payment_type="SavingsWithdrawal")
    count = Payments.objects.filter(client=client, payment_type="SavingsWithdrawal").count()
    return render(request, "listof_clientsavingswithdrawals.html", {"count":count, "savings_withdrawals_list":savings_withdrawals_list, "client":client})


@login_required
def issue_loan(request, loanaccount_id):
    loan_account = LoanAccount.objects.get(id=loanaccount_id)
    if loan_account.group:
        loan_account.loan_issued_date = datetime.datetime.now()
        loan_account.loan_issued_by = request.user
        loan_account.save()
        group_id = str(loan_account.group.id)
        return HttpResponseRedirect('/grouploanaccount/'+group_id+'/')
    elif loan_account.client:
        loan_account.loan_issued_date = datetime.datetime.now()
        loan_account.loan_issued_by = request.user
        loan_account.save()
        client_id = str(loan_account.client.id)
        return HttpResponseRedirect('/clientloanaccount/'+client_id+'/')


@login_required
def view_client_transactions(request):
    clients_list = Client.objects.all()
    result_list = []
    for client in clients_list:
        savings_account = SavingsAccount.objects.get(client=client)
        savings_transactions_list = SavingsTransactions.objects.filter(savings_account=savings_account)
        for savings_transaction in savings_transactions_list:
            dict = {}
            dict['date'] = savings_transaction.transaction_date.strftime('%Y-%m-%d')
            dict['client_name'] = client.first_name
            dict['status'] = client.is_active
            dict['savings_account_no'] = savings_account.account_no
            dict['savings_account_status'] = savings_account.status
            if savings_transaction.transaction_type == "Deposit":
                dict['savings_deposit'] = savings_transaction.transaction_amount
                dict['savings_withdrawal'] = 0
            if savings_transaction.transaction_type == "Withdraw":
                dict['savings_withdrawal'] = savings_transaction.transaction_amount
                dict['savings_deposit'] = 0
            dict['savings_balance'] = savings_transaction.savings_balance_atinstant
            result_list.append(dict)

        loan_accounts_list = LoanAccount.objects.filter(client=client)
        for loan_account in loan_accounts_list:
            loan_transactions_list = LoanTransactions.objects.filter(loan_account=loan_account)
            for loan_transaction in loan_transactions_list:
                dict = {}
                dict['date'] = loan_transaction.transaction_date.strftime('%Y-%m-%d')
                dict['client_name'] = client.first_name
                dict['loan_account_no'] = loan_account.account_no
                dict['status'] = client.is_active
                dict['loan_account_status'] = loan_account.status
                dict['loan_amount'] = loan_account.loan_amount
                dict['interest_rate'] = loan_account.annual_interest_rate
                dict['principle_loanamount_repaid'] = loan_transaction.principle_loanamount_repaid_atinstant
                dict['interest_repaid'] = loan_transaction.interest_repaid_atinstant
                dict['principle_loan_balance'] = loan_transaction.principle_loan_balance_atinstant
                result_list.append(dict)
    result_list.sort(key=lambda item:item['date'], reverse=True)
    print result_list
    return render(request,"listof_client_transactions.html",{"result_list":result_list})


@login_required
def view_group_transactions(request):
    groups_list = Group.objects.all()
    result_list = []
    for group in groups_list:
        savings_account = SavingsAccount.objects.get(group=group)
        savings_transactions_list = SavingsTransactions.objects.filter(savings_account=savings_account)
        loan_accounts_list = LoanAccount.objects.filter(group=group)
        for loan_account in loan_accounts_list:
            loan_transactions_list = LoanTransactions.objects.filter(loan_account=loan_account)
            for savings_transaction in savings_transactions_list:
                dict = {}
                same_savings_trns_list = SavingsTransactions.objects.values('date').distinct()
                for distinct_date in same_savings_trns_list:
                    sav_trn = SavingsTransactions.objects.filter(date=distinct_date).order_by('-id')[0]
                    #print sav_trn.savings_balance_atinstant
                for loan_transaction in loan_transactions_list:
                    if str(savings_transaction.transaction_date.strftime('%Y-%m-%d')) == str(loan_transaction.transaction_date.strftime('%Y-%m-%d')) :
                        dict['date'] = savings_transaction.transaction_date.strftime('%Y-%m-%d')
                        dict['group_name'] = group.name
                        dict['group_status'] = group.is_active
                        dict['savings_account_no'] = savings_account.account_no
                        dict['savings_account_status'] = savings_account.status
                        if savings_transaction.transaction_type == "Deposit" :
                            dict['savings_deposit'] = savings_transaction.transaction_amount
                            dict['savings_withdrawal'] = 0
                        if savings_transaction.transaction_type == "Withdraw":
                            dict['savings_deposit'] = 0
                            dict['savings_withdrawal'] = savings_transaction.transaction_amount
                        dict['savings_balance'] = savings_transaction.savings_balance_atinstant
                        dict['loan_account_no'] = loan_account.account_no
                        dict['loan_account_status'] = loan_account.status
                        dict['loan_amount'] = loan_account.loan_amount
                        dict['interest_rate'] = loan_account.annual_interest_rate
                        dict['principle_loanamount_repaid'] = loan_transaction.principle_loanamount_repaid_atinstant
                        dict['interest_repaid'] = loan_transaction.interest_repaid_atinstant
                        dict['principle_loan_balance'] = loan_transaction.principle_loan_balance_atinstant
                        result_list.append(dict)
                    else:
                        continue
    return render(request, "listof_group_transactions.html", {"result_list":result_list})


@login_required
def receipts_deposit(request):
    if request.method == "GET":
        branches = Branch.objects.all()
        return render(request, "receiptsform.html", {"branches":branches})
    elif request.method == "POST":
        receipt_form = ReceiptForm(request.POST)
        if receipt_form.is_valid():
            datestring_format = datetime.datetime.strptime(request.POST.get("date"),"%m/%d/%Y").strftime("%Y-%m-%d")
            dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            date = dateconvert
            branch = Branch.objects.get(id=request.POST.get("branch"))
            receipt_number = request.POST.get("receipt_number")
            name = request.POST.get("name")
            account_number = request.POST.get("account_number")
            staff = request.user
            try:
                client = Client.objects.get(first_name__iexact=name, account_number=account_number)
                print client.id
                if request.POST.get("sharecapital_amount"):
                    client.sharecapital_amount += decimal.Decimal(request.POST.get("sharecapital_amount"))
                if request.POST.get("entrancefee_amount"):
                    client.entrancefee_amount += decimal.Decimal(request.POST.get("entrancefee_amount"))
                if request.POST.get("membershipfee_amount"):
                    client.membershipfee_amount += decimal.Decimal(request.POST.get("membershipfee_amount"))
                if request.POST.get("bookfee_amount"):
                    client.bookfee_amount += decimal.Decimal(request.POST.get("bookfee_amount"))
                if request.POST.get("loanprocessingfee_amount"):
                    print "fee"
                    try:
                        loan_account = LoanAccount.objects.filter(client=client).exclude(status="Closed")[0]
                        print "loan"
                        loan_account.loanprocessingfee_amount = decimal.Decimal(request.POST.get("loanprocessingfee_amount"))
                        print loan_account.loanprocessingfee_amount
                        try:
                            client_group = client.group_set.get()
                            group_loan_account = LoanAccount.objects.filter(group=client_group).exclude(status="Closed")[0]
                            group_loan_account.loanprocessingfee_amount += decimal.Decimal(request.POST.get("loanprocessingfee_amount"))
                        except:
                            data = {"error":True, "message1":"Member has not been assigned to any group."}
                            return HttpResponse(json.dumps(data))
                    except:
                        data = {"error":True, "message1":"Member does not have any loan to pay the loan processing fee amount."}
                        return HttpResponse(json.dumps(data))
                if request.POST.get("savingsdeposit_thrift_amount"):
                    try:
                        savings_account = SavingsAccount.objects.get(client=client)
                        savings_account.savings_balance += decimal.Decimal(request.POST.get("savingsdeposit_thrift_amount"))
                        savings_account.total_deposits += decimal.Decimal(request.POST.get("savingsdeposit_thrift_amount"))

                        try:
                            client_group = client.group_set.get()
                            group_savings_account = SavingsAccount.objects.get(group=client_group)
                            group_savings_account.savings_balance += decimal.Decimal(request.POST.get("savingsdeposit_thrift_amount"))
                            group_savings_account.total_deposits += decimal.Decimal(request.POST.get("savingsdeposit_thrift_amount"))
                        except:
                            pass
                    except:
                        data = {"error":True, "message1":"Member does not have savings account."}
                        return HttpResponse(json.dumps(data))
                if request.POST.get("recurringdeposit_amount"):
                    try:
                        savings_account = SavingsAccount.objects.get(client=client)
                        savings_account.recurringdeposit_amount += decimal.Decimal(request.POST.get("recurringdeposit_amount"))
                    except:
                        data = {"error":True, "message1":"Member does not have savings account."}
                        return HttpResponse(json.dumps(data))
                if request.POST.get("insurance_amount"):
                    client.insurance_amount += decimal.Decimal(request.POST.get("insurance_amount"))

                try:
                    loan_account = LoanAccount.objects.filter(client=client).exclude(status="Closed")[0]
                    if loan_account.status == "Approved" :
                        if decimal.Decimal(loan_account.total_loan_balance) or decimal.Decimal(loan_account.interest_charged) or decimal.Decimal(loan_account.loan_repayment_amount):
                            var_demand_loanprinciple_amount_atinstant = decimal.Decimal(decimal.Decimal(loan_account.loan_repayment_amount) - decimal.Decimal(loan_account.interest_charged))
                            print var_demand_loanprinciple_amount_atinstant
                            var_demand_loaninterest_amount_atinstant = decimal.Decimal(loan_account.interest_charged)
                        else:
                            var_demand_loanprinciple_amount_atinstant = 0
                            var_demand_loaninterest_amount_atinstant = 0
                            var_principle_loan_balance_atinstant = 0
                except:
                    pass

                if decimal.Decimal(request.POST.get("loaninterest_amount")) != int(0) :
                    try:
                        loan_account = LoanAccount.objects.filter(client=client).exclude(status="Closed")[0]
                    except:
                        print "first"
                        data = {"error":True, "message1":"Member does not have any loan."}
                        return HttpResponse(json.dumps(data))
                else:
                    pass
                print "2"
                if request.POST.get("loanprinciple_amount") or decimal.Decimal(request.POST.get("loaninterest_amount")) != int(0) :
                    try:
                        loan_account = LoanAccount.objects.filter(client=client).exclude(status="Closed")[0]
                        client_group = client.group_set.get()
                        group_loan_account = LoanAccount.objects.filter(group=client_group).exclude(status="Closed")[0]
                        if loan_account.status == "Approved":
                            #if loan_account.loan_issued_date :
                                if decimal.Decimal(loan_account.total_loan_balance) or decimal.Decimal(loan_account.interest_charged):
                                    if loan_account.client:
                                        if decimal.Decimal(request.POST.get("loaninterest_amount")) > decimal.Decimal(loan_account.interest_charged) :
                                            data = {"error":True, "message1":"Entered interest amount is greater than interest charged."}
                                            return HttpResponse(json.dumps(data))
                                        else:
                                            loan_account.total_loan_amount_repaid += decimal.Decimal(request.POST.get("loanprinciple_amount"))
                                            loan_account.total_interest_repaid += decimal.Decimal(request.POST.get("loaninterest_amount"))
                                            loan_account.total_loan_paid = decimal.Decimal(decimal.Decimal(loan_account.total_loan_amount_repaid) + decimal.Decimal(loan_account.total_interest_repaid))
                                            loan_account.total_loan_balance -= decimal.Decimal(request.POST.get("loanprinciple_amount"))
                                            loan_account.no_of_repayments_completed += loan_account.loan_repayment_every
                                            loan_account.save()

                                            group_loan_account.total_loan_amount_repaid += decimal.Decimal(request.POST.get("loanprinciple_amount"))
                                            group_loan_account.total_interest_repaid += decimal.Decimal(request.POST.get("loaninterest_amount"))
                                            group_loan_account.total_loan_paid = decimal.Decimal(decimal.Decimal(group_loan_account.total_loan_amount_repaid) + decimal.Decimal(group_loan_account.total_interest_repaid))
                                            group_loan_account.total_loan_balance -= decimal.Decimal(request.POST.get("loanprinciple_amount"))
                                            group_loan_account.save()

                                            if decimal.Decimal(loan_account.total_loan_amount_repaid) == decimal.Decimal(loan_account.loan_amount) and decimal.Decimal(loan_account.total_loan_balance) == decimal.Decimal(0):
                                                if decimal.Decimal(request.POST.get("loaninterest_amount")) == decimal.Decimal(loan_account.interest_charged) :
                                                    if decimal.Decimal(request.POST.get("loanprinciple_amount")) == decimal.Decimal(decimal.Decimal(loan_account.loan_repayment_amount) - decimal.Decimal(loan_account.interest_charged)) :
                                                        loan_account.loan_repayment_amount = 0
                                                        loan_account.interest_charged = 0
                                                elif decimal.Decimal(request.POST.get("loaninterest_amount")) < decimal.Decimal(loan_account.interest_charged) :
                                                    balance_interest = decimal.Decimal(loan_account.interest_charged) - decimal.Decimal(request.POST.get("loaninterest_amount"))
                                                    loan_account.interest_charged = decimal.Decimal(balance_interest)
                                                    loan_account.loan_repayment_amount = decimal.Decimal(balance_interest)

                                            elif decimal.Decimal(loan_account.total_loan_amount_repaid) < decimal.Decimal(loan_account.loan_amount) and decimal.Decimal(loan_account.total_loan_balance) :
                                                if int(loan_account.no_of_repayments_completed) >= int(loan_account.loan_repayment_period) :
                                                    if decimal.Decimal(request.POST.get("loaninterest_amount")) == decimal.Decimal(loan_account.interest_charged) :
                                                        if loan_account.interest_type == "Flat" :
                                                            loan_account.interest_charged = decimal.Decimal(decimal.Decimal((decimal.Decimal(loan_account.loan_amount) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                        elif loan_account.interest_type == "Declining":
                                                            loan_account.interest_charged = decimal.Decimal(decimal.Decimal((decimal.Decimal(loan_account.total_loan_balance) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                    elif decimal.Decimal(request.POST.get("loaninterest_amount")) < decimal.Decimal(loan_account.interest_charged) :
                                                        balance_interest = decimal.Decimal(loan_account.interest_charged) - decimal.Decimal(request.POST.get("loaninterest_amount"))
                                                        if loan_account.interest_type == "Flat" :
                                                            interest_charged = decimal.Decimal(decimal.Decimal((decimal.Decimal(loan_account.loan_amount) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                        elif loan_account.interest_type == "Declining":
                                                            interest_charged = decimal.Decimal(decimal.Decimal((decimal.Decimal(loan_account.total_loan_balance) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                        loan_account.interest_charged = decimal.Decimal(balance_interest + interest_charged)

                                                    if decimal.Decimal(request.POST.get("loanprinciple_amount")) == decimal.Decimal(decimal.Decimal(loan_account.loan_repayment_amount) - decimal.Decimal(loan_account.interest_charged)) :
                                                        loan_account.loan_repayment_amount = decimal.Decimal(decimal.Decimal(loan_account.total_loan_balance) + decimal.Decimal(loan_account.interest_charged))
                                                    elif decimal.Decimal(request.POST.get("loanprinciple_amount")) < decimal.Decimal(decimal.Decimal(loan_account.loan_repayment_amount) - decimal.Decimal(loan_account.interest_charged)) :
                                                        balance_principle = decimal.Decimal(decimal.Decimal(decimal.Decimal(loan_account.loan_repayment_amount) - decimal.Decimal(loan_account.interest_charged)) - decimal.Decimal(request.POST.get("loanprinciple_amount")))
                                                        loan_account.loan_repayment_amount = decimal.Decimal(decimal.Decimal(loan_account.total_loan_balance) + decimal.Decimal(loan_account.interest_charged) + decimal.Decimal(balance_principle))

                                                elif int(loan_account.no_of_repayments_completed) < int(loan_account.loan_repayment_period) :
                                                    principle_repayable = decimal.Decimal(decimal.Decimal(loan_account.loan_amount) / decimal.Decimal(loan_account.loan_repayment_period))
                                                    if loan_account.interest_type == "Flat" :
                                                        if decimal.Decimal(request.POST.get("loaninterest_amount")) == decimal.Decimal(loan_account.interest_charged) :
                                                            loan_account.interest_charged = decimal.Decimal(int(loan_account.loan_repayment_every) * decimal.Decimal((decimal.Decimal(loan_account.loan_amount) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                        elif decimal.Decimal(request.POST.get("loaninterest_amount")) < decimal.Decimal(loan_account.interest_charged) :
                                                            balance_interest = decimal.Decimal(loan_account.interest_charged) - decimal.Decimal(request.POST.get("loaninterest_amount"))
                                                            interest_charged = decimal.Decimal(int(loan_account.loan_repayment_every) * decimal.Decimal((decimal.Decimal(loan_account.loan_amount) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                            loan_account.interest_charged = decimal.Decimal(balance_interest + interest_charged)
                                                    elif loan_account.interest_type == "Declining":
                                                        if decimal.Decimal(request.POST.get("loaninterest_amount")) == decimal.Decimal(loan_account.interest_charged) :
                                                            loan_account.interest_charged = decimal.Decimal(int(loan_account.loan_repayment_every) * decimal.Decimal((decimal.Decimal(loan_account.total_loan_balance) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                        elif decimal.Decimal(request.POST.get("loaninterest_amount")) < decimal.Decimal(loan_account.interest_charged) :
                                                            balance_interest = decimal.Decimal(loan_account.interest_charged) - decimal.Decimal(request.POST.get("loaninterest_amount"))
                                                            interest_charged = decimal.Decimal(int(loan_account.loan_repayment_every) * decimal.Decimal((decimal.Decimal(loan_account.total_loan_balance) * (decimal.Decimal(loan_account.annual_interest_rate) / 12)) / 100))
                                                            loan_account.interest_charged = decimal.Decimal(balance_interest + interest_charged)

                                                    if decimal.Decimal(request.POST.get("loanprinciple_amount")) == decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable))) :
                                                        if decimal.Decimal(loan_account.total_loan_balance) < decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable))) :
                                                            loan_account.loan_repayment_amount = decimal.Decimal(decimal.Decimal(loan_account.total_loan_balance) + decimal.Decimal(loan_account.interest_charged))
                                                        else:
                                                            loan_account.loan_repayment_amount = decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable)) + decimal.Decimal(loan_account.interest_charged))
                                                    elif decimal.Decimal(request.POST.get("loanprinciple_amount")) < decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable))) :
                                                        balance_principle = decimal.Decimal(decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable))) - decimal.Decimal(request.POST.get("loanprinciple_amount")))
                                                        if decimal.Decimal(loan_account.total_loan_balance) < decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable))) :
                                                            loan_account.loan_repayment_amount = decimal.Decimal(decimal.Decimal(loan_account.total_loan_balance) + decimal.Decimal(loan_account.interest_charged) + decimal.Decimal(balance_principle))
                                                        else:
                                                            loan_account.loan_repayment_amount = decimal.Decimal((int(loan_account.loan_repayment_every) * decimal.Decimal(principle_repayable)) + decimal.Decimal(loan_account.interest_charged) + decimal.Decimal(balance_principle))
                                    else:
                                        return HttpResponse("No Client")
                                else:
                                    data = {"error":True, "message1":"Loan has been cleared sucessfully."}
                                    return HttpResponse(json.dumps(data))
                            # else:
                            #     data = {"error":True, "message1":"Loan has not yet issued."}
                            #     return HttpResponse(json.dumps(data))
                        elif loan_account.status == "Applied":
                            data = {"error":True, "message1":"This loan is under pending for approval."}
                            return HttpResponse(json.dumps(data))
                        elif loan_account.status == "Rejected":
                            data = {"error":True, "message1":"Loan has been Rejected."}
                            return HttpResponse(json.dumps(data))
                        elif loan_account.status == "Closed":
                            data = {"error":True, "message1":"Loan has been Closed."}
                            return HttpResponse(json.dumps(data))
                    except:
                        data = {"error":True, "message1":"Member does not have any Loan."}
                        return HttpResponse(json.dumps(data))


                if request.POST.get("sharecapital_amount") or request.POST.get("entrancefee_amount") or request.POST.get("membershipfee_amount") or request.POST.get("bookfee_amount") or request.POST.get("loanprocessingfee_amount") or request.POST.get("savingsdeposit_thrift_amount") or request.POST.get("fixeddeposit_amount") or request.POST.get("recurringdeposit_amount") or request.POST.get("loanprinciple_amount") or request.POST.get("insurance_amount") or decimal.Decimal(request.POST.get("loaninterest_amount")) != 0 :
                    try:
                        client_group = client.group_set.get()
                        receipt = Receipts.objects.create(date=date, branch=branch, receipt_number=receipt_number, client=client, group=client_group, name=name, account_number=account_number, staff=staff)
                    except:
                        receipt = Receipts.objects.create(date=date, branch=branch, receipt_number=receipt_number, client=client, name=name, account_number=account_number, staff=staff)
                    if request.POST.get("sharecapital_amount"):
                        receipt.sharecapital_amount = decimal.Decimal(request.POST.get("sharecapital_amount"))
                    if request.POST.get("entrancefee_amount"):
                        receipt.entrancefee_amount = decimal.Decimal(request.POST.get("entrancefee_amount"))
                    if request.POST.get("membershipfee_amount"):
                        receipt.membershipfee_amount = decimal.Decimal(request.POST.get("membershipfee_amount"))
                    if request.POST.get("bookfee_amount"):
                        receipt.bookfee_amount = decimal.Decimal(request.POST.get("bookfee_amount"))
                    if request.POST.get("loanprocessingfee_amount"):
                        receipt.loanprocessingfee_amount = decimal.Decimal(request.POST.get("loanprocessingfee_amount"))
                    if request.POST.get("savingsdeposit_thrift_amount"):
                        receipt.savingsdeposit_thrift_amount = decimal.Decimal(request.POST.get("savingsdeposit_thrift_amount"))
                        receipt.savings_balance_atinstant = decimal.Decimal(savings_account.savings_balance)
                    if request.POST.get("fixeddeposit_amount"):
                        receipt.fixeddeposit_amount = decimal.Decimal(request.POST.get("fixeddeposit_amount"))
                    if request.POST.get("recurringdeposit_amount"):
                        receipt.recurringdeposit_amount = decimal.Decimal(request.POST.get("recurringdeposit_amount"))
                    if request.POST.get("insurance_amount"):
                        receipt.insurance_amount = decimal.Decimal(request.POST.get("insurance_amount"))
                    if request.POST.get("loanprinciple_amount"):
                        receipt.loanprinciple_amount = decimal.Decimal(request.POST.get("loanprinciple_amount"))
                    if request.POST.get("loaninterest_amount"):
                        receipt.loaninterest_amount = decimal.Decimal(request.POST.get("loaninterest_amount"))

                    try:
                        if var_demand_loanprinciple_amount_atinstant:
                            receipt.demand_loanprinciple_amount_atinstant = decimal.Decimal(var_demand_loanprinciple_amount_atinstant)
                            print var_demand_loanprinciple_amount_atinstant
                        if var_demand_loaninterest_amount_atinstant:
                            receipt.demand_loaninterest_amount_atinstant = decimal.Decimal(var_demand_loaninterest_amount_atinstant)
                    except:
                        pass

                    try:
                        receipt.principle_loan_balance_atinstant = decimal.Decimal(loan_account.total_loan_balance)
                    except:
                        pass

                    receipt.save()
                    client.save()
                    try:
                        savings_account.save()
                    except:
                        pass
                    try:
                        loan_account.save()
                    except:
                        pass
                    try:
                        group_savings_account.save()
                    except:
                        pass

                    data = {"error":False}
                    return HttpResponse(json.dumps(data))
                else:
                    data = {"error":True, "message1":"Empty Receipt can't be generated."}
                    return HttpResponse(json.dumps(data))
            except:
                data = {"error":True, "message1":"No Client exists with this name and account number."}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":receipt_form.errors}
            return HttpResponse(json.dumps(data))


def receipts_list(request):
    receipt_list = Receipts.objects.all().order_by("-id")
    return render(request, "listof_receipts.html", {"receipt_list":receipt_list})


def ledger_account(request, client_id):
    client = Client.objects.get(id=client_id)
    receipts_list = Receipts.objects.filter(client=client_id).exclude(demand_loanprinciple_amount_atinstant=0, demand_loaninterest_amount_atinstant=0)
    return render(request, "client_ledger_account.html", {"receipts_list":receipts_list, "client":client})


def general_ledger(request):
    query_set = Receipts.objects.all()
    query_set.query.group_by = ["date"]
    grouped_receipts_list = []
    for i in query_set:
        grouped_receipts_list.append(i)
    list = []
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
        dict = {}
        dict["date"] = objreceipt.date
        for receipt in receipts_list:
            sum_sharecapital_amount += decimal.Decimal(receipt.sharecapital_amount)
            sum_entrancefee_amount += decimal.Decimal(receipt.entrancefee_amount)
            sum_membershipfee_amount += decimal.Decimal(receipt.membershipfee_amount)
            sum_bookfee_amount += decimal.Decimal(receipt.bookfee_amount)
            sum_loanprocessingfee_amount += decimal.Decimal(receipt.loanprocessingfee_amount)
            sum_savingsdeposit_thrift_amount += decimal.Decimal(receipt.savingsdeposit_thrift_amount)
            sum_fixeddeposit_amount += decimal.Decimal(receipt.fixeddeposit_amount)
            sum_recurringdeposit_amount += decimal.Decimal(receipt.recurringdeposit_amount)
            sum_loanprinciple_amount += decimal.Decimal(receipt.loanprinciple_amount)
            sum_loaninterest_amount += decimal.Decimal(receipt.loaninterest_amount)
            sum_insurance_amount = decimal.Decimal(receipt.insurance_amount)

        dict["sum_sharecapital_amount"] = decimal.Decimal(sum_sharecapital_amount)
        dict["sum_entrancefee_amount"] = decimal.Decimal(sum_entrancefee_amount)
        dict["sum_membershipfee_amount"] = decimal.Decimal(sum_membershipfee_amount)
        dict["sum_bookfee_amount"] = decimal.Decimal(sum_bookfee_amount)
        dict["sum_loanprocessingfee_amount"] = decimal.Decimal(sum_loanprocessingfee_amount)
        dict["sum_savingsdeposit_thrift_amount"] = decimal.Decimal(sum_savingsdeposit_thrift_amount)
        dict["sum_fixeddeposit_amount"] = decimal.Decimal(sum_fixeddeposit_amount)
        dict["sum_recurringdeposit_amount"] = decimal.Decimal(sum_recurringdeposit_amount)
        dict["sum_loanprinciple_amount"] = decimal.Decimal(sum_loanprinciple_amount)
        dict["sum_loaninterest_amount"] = decimal.Decimal(sum_loaninterest_amount)
        dict["sum_insurance_amount"] = decimal.Decimal(sum_insurance_amount)
        dict["total_sum"] = decimal.Decimal(sum_sharecapital_amount + sum_entrancefee_amount + sum_membershipfee_amount + sum_bookfee_amount + sum_loanprocessingfee_amount + sum_savingsdeposit_thrift_amount + sum_fixeddeposit_amount + sum_recurringdeposit_amount + sum_loanprinciple_amount + sum_loaninterest_amount + sum_insurance_amount)
        list.append(dict)
    return render(request, "generalledger.html", {"list":list})


@login_required
def fixed_deposits(request):
    if request.method == "GET":
        return render(request,"fixed_deposit_application.html")
    else:
        form = FixedDepositForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(first_name__iexact=request.POST.get("client_name"), account_number=request.POST.get("client_account_no"))
            savings_account = SavingsAccount.objects.get(client=client)
            fixed_deposit_amount = request.POST.get("fixed_deposit_amount")
            fixed_deposit_interest_rate = request.POST.get("fixed_deposit_interest_rate")
            fixed_deposit_period = request.POST.get("fixed_deposit_period")
            nominee_firstname = request.POST.get("nominee_firstname")
            nominee_lastname = request.POST.get("nominee_lastname")
            nominee_gender = request.POST.get("nominee_gender")
            nominee_occupation = request.POST.get("nominee_occupation")
            datestring_format = datetime.datetime.strptime(request.POST.get("deposited_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            deposited_date = dateconvert
            nominee_datestring_format = datetime.datetime.strptime(request.POST.get("nominee_date_of_birth"),'%m/%d/%Y').strftime('%Y-%m-%d')
            nominee_dateconvert = datetime.datetime.strptime(nominee_datestring_format, "%Y-%m-%d")
            nominee_date_of_birth = nominee_dateconvert
            relationship_with_nominee = request.POST.get("relationship_with_nominee")
            fixed_deposit = FixedDeposits.objects.create(deposited_date=deposited_date, client=client, nominee_occupation=nominee_occupation, nominee_date_of_birth=nominee_date_of_birth, nominee_lastname=nominee_lastname, savings_account=savings_account, nominee_gender=nominee_gender, fixed_deposit_amount=fixed_deposit_amount, fixed_deposit_interest_rate=fixed_deposit_interest_rate, fixed_deposit_period=fixed_deposit_period, nominee_firstname=nominee_firstname, relationship_with_nominee=relationship_with_nominee)
            interest_charged = decimal.Decimal(((decimal.Decimal(fixed_deposit.fixed_deposit_amount) *(decimal.Decimal(fixed_deposit.fixed_deposit_interest_rate) / 12)) / 100))
            fixed_deposit_interest_charged = decimal.Decimal(decimal.Decimal(interest_charged) * decimal.Decimal(fixed_deposit.fixed_deposit_period))
            fixed_deposit.maturity_amount = decimal.Decimal(decimal.Decimal(fixed_deposit.fixed_deposit_amount) + decimal.Decimal(fixed_deposit_interest_charged))
            fixed_deposit.fixed_deposit_interest = decimal.Decimal(decimal.Decimal(fixed_deposit.maturity_amount) - decimal.Decimal(fixed_deposit.fixed_deposit_amount))
            fixed_deposit.save()
            data = {"error":False, "fixed_deposit_id":fixed_deposit.id}
            return HttpResponse(json.dumps(data))
        else:
            print form.errors
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def client_fixed_deposits_profile(request,fixed_deposit_id):
    fixed_deposit = FixedDeposits.objects.get(id=fixed_deposit_id)
    return render(request, "client_fixed_deposits_profile.html", {"fixed_deposit":fixed_deposit})


@login_required
def view_client_fixed_deposits(request):
    fixed_deposit_list = FixedDeposits.objects.all().order_by("-id")
    return render(request, "view_client_fixed_deposits.html", {"fixed_deposit_list":fixed_deposit_list})


@login_required
def view_particular_client_fixed_deposits(request,client_id):
    fixed_deposit_list = FixedDeposits.objects.filter(client=client_id).order_by("-id")
    return render(request, "view_client_fixed_deposits.html", {"fixed_deposit_list":fixed_deposit_list})


@login_required
def client_recurring_deposits_profile(request, recurring_deposit_id):
    recurring_deposit = RecurringDeposits.objects.get(id=recurring_deposit_id)
    return render(request, "client_recurring_deposits_profile.html", {"recurring_deposit":recurring_deposit})


@login_required
def view_client_recurring_deposits(request):
    recurring_deposit_list = RecurringDeposits.objects.all().order_by("-id")
    return render(request, "view_client_recurring_deposits.html", {"recurring_deposit_list":recurring_deposit_list})


@login_required
def view_particular_client_recurring_deposits(request, client_id):
    client = Client.objects.get(id=client_id)
    recurring_deposit_list = RecurringDeposits.objects.filter(client=client_id)
    return render(request, "view_particular_client_recurring_deposits.html", {"client":client, "recurring_deposit_list":recurring_deposit_list})


@login_required
def view_day_book(request):
    current_date = datetime.datetime.now().date()
    current_date1 = datetime.datetime.now().date()
    query_set = Receipts.objects.filter(date=current_date)

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

    for group_id in grouped_receipts_list:
        if group_id:
            receipts_list = Receipts.objects.filter(group=group_id, date=current_date)
            thrift_deposit_sum = 0
            loanprinciple_amount_sum = 0
            loaninterest_amount_sum = 0
            entrancefee_amount_sum = 0
            membershipfee_amount_sum = 0
            bookfee_amount_sum = 0
            loanprocessingfee_amount_sum = 0
            insurance_amount_sum = 0

            for receipt in receipts_list:
                thrift_deposit_sum += decimal.Decimal(receipt.savingsdeposit_thrift_amount)
                loanprinciple_amount_sum += decimal.Decimal(receipt.loanprinciple_amount)
                loaninterest_amount_sum += decimal.Decimal(receipt.loaninterest_amount)
                entrancefee_amount_sum += decimal.Decimal(receipt.entrancefee_amount)
                membershipfee_amount_sum += decimal.Decimal(receipt.membershipfee_amount)
                bookfee_amount_sum += decimal.Decimal(receipt.bookfee_amount)
                loanprocessingfee_amount_sum += decimal.Decimal(receipt.loanprocessingfee_amount)
                insurance_amount_sum += decimal.Decimal(receipt.insurance_amount)

            group = Group.objects.get(id=group_id)
            dict = {}
            dict["group_name"] = group.name
            dict["thrift_deposit_sum"] = thrift_deposit_sum
            dict["account_number"] = group.account_number
            thrift_deposit_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["loanprinciple_amount_sum"] = loanprinciple_amount_sum
            dict["account_number"] = group.account_number
            loanprinciple_amount_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["loaninterest_amount_sum"] = loaninterest_amount_sum
            dict["account_number"] = group.account_number
            loaninterest_amount_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["entrancefee_amount_sum"] = entrancefee_amount_sum
            dict["account_number"] = group.account_number
            entrancefee_amount_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["membershipfee_amount_sum"] = membershipfee_amount_sum
            dict["account_number"] = group.account_number
            membershipfee_amount_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["bookfee_amount_sum"] = bookfee_amount_sum
            dict["account_number"] = group.account_number
            bookfee_amount_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["loanprocessingfee_amount_sum"] = loanprocessingfee_amount_sum
            dict["account_number"] = group.account_number
            loanprocessingfee_amount_sum_list.append(dict)
            dict = {}
            dict["group_name"] = group.name
            dict["insurance_amount_sum"] = insurance_amount_sum
            dict["account_number"] = group.account_number
            insurance_amount_sum_list.append(dict)
        else:
            receipts_list = Receipts.objects.filter(date=current_date, group=0)
            thrift_deposit_sum = 0
            loanprinciple_amount_sum = 0
            loaninterest_amount_sum = 0
            entrancefee_amount_sum = 0
            membershipfee_amount_sum = 0
            bookfee_amount_sum = 0
            loanprocessingfee_amount_sum = 0
            insurance_amount_sum = 0

            for receipt in receipts_list:
                thrift_deposit_sum = decimal.Decimal(receipt.savingsdeposit_thrift_amount)
                loanprinciple_amount_sum = decimal.Decimal(receipt.loanprinciple_amount)
                loaninterest_amount_sum = decimal.Decimal(receipt.loaninterest_amount)
                entrancefee_amount_sum = decimal.Decimal(receipt.entrancefee_amount)
                membershipfee_amount_sum = decimal.Decimal(receipt.membershipfee_amount)
                bookfee_amount_sum = decimal.Decimal(receipt.bookfee_amount)
                loanprocessingfee_amount_sum = decimal.Decimal(receipt.loanprocessingfee_amount)
                insurance_amount_sum = decimal.Decimal(receipt.insurance_amount)

                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["thrift_deposit_sum"] = thrift_deposit_sum
                dict["account_number"] = receipt.client.account_number
                thrift_deposit_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["loanprinciple_amount_sum"] = loanprinciple_amount_sum
                dict["account_number"] = receipt.client.account_number
                loanprinciple_amount_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["loaninterest_amount_sum"] = loaninterest_amount_sum
                dict["account_number"] = receipt.client.account_number
                loaninterest_amount_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["entrancefee_amount_sum"] = entrancefee_amount_sum
                dict["account_number"] = receipt.client.account_number
                entrancefee_amount_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["membershipfee_amount_sum"] = membershipfee_amount_sum
                dict["account_number"] = receipt.client.account_number
                membershipfee_amount_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["bookfee_amount_sum"] = bookfee_amount_sum
                dict["account_number"] = receipt.client.account_number
                bookfee_amount_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["loanprocessingfee_amount_sum"] = loanprocessingfee_amount_sum
                dict["account_number"] = receipt.client.account_number
                loanprocessingfee_amount_sum_list.append(dict)
                dict = {}
                dict["group_name"] = receipt.client.first_name
                dict["insurance_amount_sum"] = insurance_amount_sum
                dict["account_number"] = receipt.client.account_number
                insurance_amount_sum_list.append(dict)

    dict = {}
    total_thrift_deposit_sum = 0
    for dictionary in thrift_deposit_sum_list:
        total_thrift_deposit_sum += dictionary["thrift_deposit_sum"]
    dict["total_thrift_deposit_sum"] = total_thrift_deposit_sum
    total_loanprinciple_amount_sum = 0
    for dictionary in loanprinciple_amount_sum_list:
        total_loanprinciple_amount_sum += dictionary["loanprinciple_amount_sum"]
    dict["total_loanprinciple_amount_sum"] = total_loanprinciple_amount_sum
    total_loaninterest_amount_sum = 0
    for dictionary in loaninterest_amount_sum_list:
        total_loaninterest_amount_sum += dictionary["loaninterest_amount_sum"]
    dict["total_loaninterest_amount_sum"] = total_loaninterest_amount_sum
    total_entrancefee_amount_sum = 0
    for dictionary in entrancefee_amount_sum_list:
        total_entrancefee_amount_sum += dictionary["entrancefee_amount_sum"]
    dict["total_entrancefee_amount_sum"] = total_entrancefee_amount_sum
    total_membershipfee_amount_sum = 0
    for dictionary in membershipfee_amount_sum_list:
        total_membershipfee_amount_sum += dictionary["membershipfee_amount_sum"]
    dict["total_membershipfee_amount_sum"] = total_membershipfee_amount_sum
    total_bookfee_amount_sum = 0
    for dictionary in bookfee_amount_sum_list:
        total_bookfee_amount_sum += dictionary["bookfee_amount_sum"]
    dict["total_bookfee_amount_sum"] = total_bookfee_amount_sum
    total_loanprocessingfee_amount_sum = 0
    for dictionary in loanprocessingfee_amount_sum_list:
        total_loanprocessingfee_amount_sum += dictionary["loanprocessingfee_amount_sum"]
    dict["total_loanprocessingfee_amount_sum"] = total_loanprocessingfee_amount_sum
    total_insurance_amount_sum = 0
    for dictionary in insurance_amount_sum_list:
        total_insurance_amount_sum += dictionary["insurance_amount_sum"]
    dict["total_insurance_amount_sum"] = total_insurance_amount_sum
    total = total_thrift_deposit_sum + total_loanprinciple_amount_sum + total_loaninterest_amount_sum + total_entrancefee_amount_sum + total_membershipfee_amount_sum + total_bookfee_amount_sum + total_loanprocessingfee_amount_sum + total_insurance_amount_sum

    payments_list = Payments.objects.filter(date=current_date1)
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
    print travellingallowance_list
    print loans_list
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
        travellingallowance_sum += decimal.Decimal(payment.total_amount)
    dict_payments["travellingallowance_sum"] = travellingallowance_sum
    for payment in loans_list:
        loans_sum += decimal.Decimal(payment.total_amount)
    dict_payments["loans_sum"] = loans_sum
    print loans_list
    for payment in paymentofsalary_list:
        paymentofsalary_sum += decimal.Decimal(payment.total_amount)
    dict_payments["paymentofsalary_sum"] = paymentofsalary_sum
    for payment in printingcharges_list:
        printingcharges_sum += decimal.Decimal(payment.total_amount)
    dict_payments["printingcharges_sum"] = printingcharges_sum
    for payment in stationarycharges_list:
        stationarycharges_sum += decimal.Decimal(payment.total_amount)
    dict_payments["stationarycharges_sum"] = stationarycharges_sum
    for payment in othercharges_list:
        othercharges_sum += decimal.Decimal(payment.total_amount)
    dict_payments["othercharges_sum"] = othercharges_sum
    for payment in savingswithdrawal_list:
        savingswithdrawal_sum += decimal.Decimal(payment.total_amount)
    dict_payments["savingswithdrawal_sum"] = savingswithdrawal_sum
    for payment in fixedwithdrawal_list:
        fixedwithdrawal_sum += decimal.Decimal(payment.total_amount)
    dict_payments["fixedwithdrawal_sum"] = fixedwithdrawal_sum
    for payment in recurringwithdrawal_list:
        recurringwithdrawal_sum += decimal.Decimal(payment.total_amount)
    dict_payments["recurringwithdrawal_sum"] = recurringwithdrawal_sum
    total_payments = travellingallowance_sum + loans_sum + paymentofsalary_sum + printingcharges_sum + stationarycharges_sum + othercharges_sum + savingswithdrawal_sum + fixedwithdrawal_sum + recurringwithdrawal_sum 
    return render(request,"day_book.html", {"receipts_list":receipts_list, "total_payments":total_payments, "travellingallowance_list":travellingallowance_list, "loans_list":loans_list, "paymentofsalary_list":paymentofsalary_list, "printingcharges_list":printingcharges_list,"stationarycharges_list":stationarycharges_list,"othercharges_list":othercharges_list,"savingswithdrawal_list":savingswithdrawal_list, "recurringwithdrawal_list":recurringwithdrawal_list, "fixedwithdrawal_list":fixedwithdrawal_list, "total":total, "dict_payments":dict_payments, "dict":dict, "current_date":current_date, "grouped_receipts_list":grouped_receipts_list, "thrift_deposit_sum_list":thrift_deposit_sum_list, "loanprinciple_amount_sum_list":loanprinciple_amount_sum_list, "loaninterest_amount_sum_list":loaninterest_amount_sum_list, "entrancefee_amount_sum_list":entrancefee_amount_sum_list, "membershipfee_amount_sum_list":membershipfee_amount_sum_list, "bookfee_amount_sum_list":bookfee_amount_sum_list, "loanprocessingfee_amount_sum_list":loanprocessingfee_amount_sum_list, "insurance_amount_sum_list":insurance_amount_sum_list})


@login_required
def recurring_deposits(request):
    if request.method == "GET":
        return render(request,"recurring_deposit_application.html")
    else:
        form = ReccuringDepositForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(first_name__iexact=request.POST.get("client_name"), account_number=request.POST.get("client_account_no"))
            savings_account = SavingsAccount.objects.get(client=client)
            recurring_deposit_amount = request.POST.get("recurring_deposit_amount")
            reccuring_deposit_number = request.POST.get("reccuring_deposit_number")
            recurring_deposit_interest_rate = request.POST.get("recurring_deposit_interest_rate")
            recurring_deposit_period = request.POST.get("recurring_deposit_period")
            nominee_firstname = request.POST.get("nominee_firstname")
            nominee_lastname = request.POST.get("nominee_lastname")
            nominee_gender = request.POST.get("nominee_gender")
            nominee_occupation = request.POST.get("nominee_occupation")
            datestring_format = datetime.datetime.strptime(request.POST.get("deposited_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            deposited_date = dateconvert
            nominee_datestring_format = datetime.datetime.strptime(request.POST.get("nominee_date_of_birth"),'%m/%d/%Y').strftime('%Y-%m-%d')
            nominee_dateconvert = datetime.datetime.strptime(nominee_datestring_format, "%Y-%m-%d")
            nominee_date_of_birth = nominee_dateconvert
            relationship_with_nominee = request.POST.get("relationship_with_nominee")
            recurring_deposit = RecurringDeposits.objects.create(reccuring_deposit_number=reccuring_deposit_number, status="Opened", deposited_date=deposited_date, client=client, nominee_occupation=nominee_occupation, nominee_date_of_birth=nominee_date_of_birth, nominee_lastname=nominee_lastname, savings_account=savings_account, nominee_gender=nominee_gender, recurring_deposit_amount=recurring_deposit_amount, recurring_deposit_interest_rate=recurring_deposit_interest_rate, recurring_deposit_period=recurring_deposit_period, nominee_firstname=nominee_firstname, relationship_with_nominee=relationship_with_nominee)
            data = {"error":False, "recurring_deposit_id":recurring_deposit.id}
            return HttpResponse(json.dumps(data))
        else:
            print form.errors
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


@login_required
def payments_list(request):
   payments_list = Payments.objects.all().order_by("-id")
   return render(request,"list_of_payments.html", {"payments_list":payments_list})


@login_required
def pay_slip(request):
    if request.method == "GET":
        branches = Branch.objects.all()
        voucher_types = []
        for voucher_type in PAYMENT_TYPES:
            voucher_types.append(voucher_type[0])
        return render(request, "paymentform.html", {"branches":branches, "voucher_types":voucher_types})
    elif request.method == "POST":
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            datestring_format = datetime.datetime.strptime(request.POST.get("date"),"%m/%d/%Y").strftime("%Y-%m-%d")
            dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            date = dateconvert
            branch = Branch.objects.get(id=request.POST.get("branch"))
            voucher_number = request.POST.get("voucher_number")
            payment_type = request.POST.get("payment_type")
            amount = request.POST.get("amount")
            total_amount = request.POST.get("total_amount")
            totalamount_in_words = request.POST.get("totalamount_in_words")

            if decimal.Decimal(request.POST.get("amount")) != 0 and decimal.Decimal(request.POST.get("total_amount")) != 0 :

                if request.POST.get("payment_type") == "TravellingAllowance" or request.POST.get("payment_type") == "Paymentofsalary" :
                    if not request.POST.get("staff_username"):
                        data = {"error":True, "message1":"Please enter Employee Username"}
                        return HttpResponse(json.dumps(data))
                    elif request.POST.get("staff_username"):
                        try:
                            staff = User.objects.get(username__iexact=request.POST.get("staff_username"))
                            if not request.POST.get("interest"):
                                print "first"
                                if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(request.POST.get("amount")) :
                                    print "1"
                                    payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, payment_type=payment_type, staff=staff, amount=amount, total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                                    data = {"error":False}
                                    return HttpResponse(json.dumps(data))
                                else:
                                    data = {"error":True, "message1":"Entered total amount is not equal to amount."}
                                    return HttpResponse(json.dumps(data))
                            else:
                                data = {"error":True, "message1":"Interest must be empty for TA and Payment of salary Voucher."}
                                return HttpResponse(json.dumps(data))
                        except:
                            data = {"error":True, "message1":"Entered Employee Username is incorrect"}
                            return HttpResponse(json.dumps(data))

                elif request.POST.get("payment_type") == "PrintingCharges" or request.POST.get("payment_type") == "StationaryCharges" or request.POST.get("payment_type") == "OtherCharges" :
                    if not request.POST.get("interest"):
                        if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(request.POST.get("amount")) :
                            payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, payment_type=payment_type, amount=amount, total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                            data = {"error":False}
                            return HttpResponse(json.dumps(data))
                        else:
                            data = {"error":True, "message1":"Entered total amount is not equal to amount."}
                            return HttpResponse(json.dumps(data))
                    else:
                        data = {"error":True, "message1":"Interest must be empty for Charges Voucher."}
                        return HttpResponse(json.dumps(data))

                elif request.POST.get("payment_type") == "SavingsWithdrawal" :
                    if not request.POST.get("client_name"):
                        data = {"error":True, "message1":"Please enter the Member First Name"}
                        return HttpResponse(json.dumps(data))
                    elif request.POST.get("client_name"):
                        if not request.POST.get("client_account_number"):
                            data = {"error":True, "message1":"Please enter the Member Account number"}
                            return HttpResponse(json.dumps(data))
                        try:
                            client = Client.objects.get(first_name__iexact=request.POST.get("client_name"), account_number=request.POST.get("client_account_number"))
                            try:
                                savings_account = SavingsAccount.objects.get(client=client)
                                if decimal.Decimal(savings_account.savings_balance) >= decimal.Decimal(request.POST.get("amount")) :
                                    try:
                                        client_group = client.group_set.get()
                                        try:
                                            group_savings_account = SavingsAccount.objects.get(group=client_group)
                                            if decimal.Decimal(group_savings_account.savings_balance) >= decimal.Decimal(request.POST.get("amount")) :
                                                if request.POST.get("group_name"):
                                                    if request.POST.get("group_name").lower() == client_group.name.lower() :
                                                        if request.POST.get("group_account_number"):
                                                            if request.POST.get("group_account_number") == client_group.account_number :
                                                                if not request.POST.get("interest"):
                                                                    if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(request.POST.get("amount")) :
                                                                        payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, client=client, group=client_group, payment_type=payment_type, amount=amount, total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                                                                        savings_account.savings_balance -= decimal.Decimal(request.POST.get("amount"))
                                                                        savings_account.total_withdrawals += decimal.Decimal(request.POST.get("amount"))
                                                                        savings_account.save()

                                                                        group_savings_account.savings_balance -= decimal.Decimal(request.POST.get("amount"))
                                                                        group_savings_account.total_withdrawals += decimal.Decimal(request.POST.get("amount"))
                                                                        group_savings_account.save()
                                                                        data = {"error":False}
                                                                        return HttpResponse(json.dumps(data))
                                                                    else:
                                                                        data = {"error":True, "message1":"Entered total amount is not equal to amount."}
                                                                        return HttpResponse(json.dumps(data))

                                                                elif request.POST.get("interest"):
                                                                    if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(decimal.Decimal(request.POST.get("amount")) + decimal.Decimal(request.POST.get("interest"))) :
                                                                        payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, client=client, group=client_group, payment_type=payment_type, amount=amount, interest=request.POST.get("interest"), total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                                                                        savings_account.savings_balance -= decimal.Decimal(request.POST.get("amount"))
                                                                        savings_account.total_withdrawals += decimal.Decimal(request.POST.get("amount"))
                                                                        savings_account.save()

                                                                        group_savings_account.savings_balance -= decimal.Decimal(request.POST.get("amount"))
                                                                        group_savings_account.total_withdrawals += decimal.Decimal(request.POST.get("amount"))
                                                                        group_savings_account.save()
                                                                        data = {"error":False}
                                                                        return HttpResponse(json.dumps(data))
                                                                    else:
                                                                        data = {"error":True, "message1":"Entered total amount is incorrect."}
                                                                        return HttpResponse(json.dumps(data))
                                                            else:
                                                                data = {"error":True, "message1":"Entered Group A/C Number is incorrect."}
                                                                return HttpResponse(json.dumps(data))
                                                        else:
                                                            data = {"error":True, "message1":"Please enter the Group A/C Number."}
                                                            return HttpResponse(json.dumps(data))
                                                    else:
                                                        data = {"error":True, "message1":"Member does not belong to the entered Group Name."}
                                                        return HttpResponse(json.dumps(data))
                                                else:
                                                    data = {"error":True, "message1":"Please enter the Group name of the Member."}
                                                    return HttpResponse(json.dumps(data))
                                            elif decimal.Decimal(group_savings_account.savings_balance) < decimal.Decimal(request.POST.get("amount")) :
                                                data = {"error":True, "message1":"Group Savings A/C does not have sufficient balance."}
                                                return HttpResponse(json.dumps(data))
                                        except:
                                            data = {"error":True, "message1":"The Group which the Member belongs to does not have Savings Account."}
                                            return HttpResponse(json.dumps(data))
                                    except:
                                        if request.POST.get("group_name") or request.POST.get("group_account_number") :
                                            data = {"error":True, "message1":"Member does not assigned to any Group. Please clear Group details"}
                                            return HttpResponse(json.dumps(data))
                                        else:
                                            if not request.POST.get("interest"):
                                                if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(request.POST.get("amount")) :
                                                    payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, client=client, payment_type=payment_type, amount=amount, total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                                                    savings_account.savings_balance -= decimal.Decimal(request.POST.get("amount"))
                                                    savings_account.total_withdrawals += decimal.Decimal(request.POST.get("amount"))
                                                    savings_account.save()

                                                    data = {"error":False}
                                                    return HttpResponse(json.dumps(data))
                                                else:
                                                    data = {"error":True, "message1":"Entered total amount is not equal to amount."}
                                                    return HttpResponse(json.dumps(data))

                                            elif request.POST.get("interest"):
                                                if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(decimal.Decimal(request.POST.get("amount")) + decimal.Decimal(request.POST.get("interest"))) :
                                                    payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, client=client, payment_type=payment_type, amount=amount, interest=request.POST.get("interest"), total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                                                    savings_account.savings_balance -= decimal.Decimal(request.POST.get("amount"))
                                                    savings_account.total_withdrawals += decimal.Decimal(request.POST.get("amount"))
                                                    savings_account.save()

                                                    data = {"error":False}
                                                    return HttpResponse(json.dumps(data))
                                                else:
                                                    data = {"error":True, "message1":"Entered total amount is incorrect."}
                                                    return HttpResponse(json.dumps(data))

                                elif decimal.Decimal(savings_account.savings_balance) < decimal.Decimal(request.POST.get("amount")) :
                                    data = {"error":True, "message1":"Member Savings Account does not have sufficient balance."}
                                    return HttpResponse(json.dumps(data))
                            except:
                                data = {"error":True, "message1":"Member does not have Savings Account."}
                                return HttpResponse(json.dumps(data))
                        except:
                            data = {"error":True, "message1":"Member does not exists with this First Name and A/C Number. Please enter correct details."}
                            return HttpResponse(json.dumps(data))
                elif request.POST.get("payment_type") == "Loans" :
                    if request.POST.get("interest"):
                        data = {"error":True, "message1":"Interest amount must be empty while issuing Loans."}
                        return HttpResponse(json.dumps(data))
                    if request.POST.get("client_name") or request.POST.get("client_account_number"):
                        data = {"error":True, "message1":"Client details must be empty while issuing Loans."}
                        return HttpResponse(json.dumps(data))
                    if not request.POST.get("group_name") :
                        data = {"error":True, "message1":"Please enter Group Name."}
                        return HttpResponse(json.dumps(data))
                    elif request.POST.get("group_name") :
                        if not request.POST.get("group_account_number") :
                            data = {"error":True, "message1":"Please enter Group A/C Number."}
                            return HttpResponse(json.dumps(data))
                        elif request.POST.get("group_account_number") :
                            try:
                                group = Group.objects.get(name__iexact=request.POST.get("group_name"), account_number=request.POST.get("group_account_number"))
                                try:
                                    loan_account = LoanAccount.objects.filter(group=group).exclude(status="Closed")[0]
                                    if decimal.Decimal(request.POST.get("total_amount")) == decimal.Decimal(request.POST.get("amount")) :
                                        try:
                                            if decimal.Decimal(loan_account.loan_amount) == decimal.Decimal(request.POST.get("total_amount")) :
                                                try:
                                                    clients_list = group.clients.all()
                                                    payment = Payments.objects.create(date=date, branch=branch, voucher_number=voucher_number, group=group, payment_type=payment_type, amount=amount, total_amount=total_amount, totalamount_in_words=totalamount_in_words)
                                                    loan_account.loan_issued_date = datetime.datetime.now().date()
                                                    loan_account.loan_issued_by = request.user
                                                    for client in clients_list:
                                                        client_loan_account = LoanAccount.objects.filter(client=client).exclude(status="Closed")[0]
                                                        client_loan_account.loan_issued_date = datetime.datetime.now().date()
                                                        client_loan_account.loan_issued_by = request.user
                                                        client_loan_account.save()
                                                    loan_account.save()
                                                    data = {"error":False}
                                                    return HttpResponse(json.dumps(data))
                                                except:
                                                    data = {"error":True, "message1":"Group does not contain members inorder to issue Loan."}
                                                    return HttpResponse(json.dumps(data))
                                        except:
                                            data = {"error":True, "message1":"Amount is less than applied loan amount."}
                                            return HttpResponse(json.dumps(data))
                                    else:
                                        data = {"error":True, "message1":"Entered total amount is not equal to amount."}
                                        return HttpResponse(json.dumps(data))
                                except:
                                    data = {"error":True, "message1":"Group has not been applied for the Loan. Please create loan account inorder to issue Loan."}
                                    return HttpResponse(json.dumps(data))
                            except:
                                data = {"error":True, "message1":"Group does not exists with this Name and A/C Number. Please enter correct details."}
                                return HttpResponse(json.dumps(data))
            else:
                data = {"error":True, "message1":"Voucher can't be generated with amount/total amount zero"}
                return HttpResponse(json.dumps(data))

        else:
            print payment_form.errors
            data = {"error":True, "message":payment_form.errors}
            return HttpResponse(json.dumps(data))


def view_group_loanslist(request, group_id):
    group = Group.objects.get(id=group_id)
    loan_accounts_list = LoanAccount.objects.filter(group=group)
    loan_accounts_count = LoanAccount.objects.filter(group=group).count()
    return render(request, "listof_grouploan_accounts.html", {"group":group, "loan_accounts_list":loan_accounts_list, "loan_accounts_count":loan_accounts_count})


def view_client_loanslist(request, client_id):
    client = Client.objects.get(id=client_id)
    loan_accounts_list = LoanAccount.objects.filter(client=client)
    loan_accounts_count = LoanAccount.objects.filter(client=client).count()
    return render(request, "listof_clientloan_accounts.html", {"client":client, "loan_accounts_list":loan_accounts_list, "loan_accounts_count":loan_accounts_count})
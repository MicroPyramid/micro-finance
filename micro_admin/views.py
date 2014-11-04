from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import login, authenticate, logout
import json
from micro_admin.models import User, Branch, Group, Client
from micro_admin.forms import BranchForm, UserForm, EditbranchForm, GroupForm, ClientForm, AddMemberForm
import datetime

def index(request):
    data = {}
    data.update(csrf(request))
    return render_to_response("login.html",data)


def user_login(request):
    if request.method == "POST":
        user_name = request.POST.get("username")
        user_password = request.POST.get("password")
        user = authenticate(username=user_name, password=user_password)
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


def user_logout(request):
    if not request.user.is_authenticated():
        return HttpResponse("")
    logout(request)
    return HttpResponseRedirect("/")


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


def edit_branch(request, branch_id):
    if request.method == "GET":
        branch = Branch.objects.get(id=branch_id)
        return render(request, "editbranchdetails.html", {"branch":branch})
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
            return HttpResponse("Branch Details Updated Successfully")
        else:
            return HttpResponse("Invalid Data")


def branch_profile(request,branch_id):
    branch = Branch.objects.get(id=branch_id)
    return render(request,"branchprofile.html", {"branch":branch})


def view_branch(request):
    branch_list = Branch.objects.all()
    return render(request,"viewbranch.html",{"branch_list":branch_list })


def delete_branch(request,branch_id):
    branch = Branch.objects.get(id=branch_id)
    branch.delete()
    return HttpResponse("Deleted Branch Profile")


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
            account_type = request.POST.get("account_type")
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
            client = Client.objects.create(branch=branch, first_name=first_name, last_name=last_name, email=email, account_type=account_type, account_number=account_number, blood_group=blood_group, gender=gender, client_role=client_role, occupation=occupation, annual_income=annual_income, country=country, state=state, district=district, city=city, area=area, mobile=mobile, pincode=pincode, date_of_birth=date_of_birth, joined_date=joined_date)
            data = {"error":False, "message":"Client Created Successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":form.errors}
            return HttpResponse(json.dumps(data))


def client_profile(request):
    return HttpResponse("client created Successfully")


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


def user_profile(request, user_id):
    selecteduser = User.objects.get(id=user_id)
    return render(request, "userprofile.html", {"selecteduser":selecteduser})


def users_list (request):
    list_of_users = User.objects.filter(is_admin=0)
    return render(request,"listofusers.html", {"list_of_users":list_of_users})


def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    list_of_users = User.objects.filter(is_admin=0)
    return render(request, "listofusers.html", {"list_of_users":list_of_users})


def create_group(request):
    if request.method == "GET":
        data = {}
        branches = Branch.objects.all()
        return render(request, "creategroup.html", {"data":data, "branches":branches})
    else:
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            name = request.POST.get("name")
            account_type = request.POST.get("account_type")
            account_number = request.POST.get("account_number")
            datestring_format = datetime.datetime.strptime(request.POST.get("activation_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
            dateconvert=datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
            activation_date = dateconvert
            branch = Branch.objects.get(id=request.POST.get("branch"))
            group = Group.objects.create(name=name, account_type=account_type, account_number=account_number, activation_date=activation_date, branch=branch)
            data = {"error":False, "group_id":group.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error":True, "message":group_form.errors}
            return HttpResponse(json.dumps(data))


def edit_group(request, group_id):
    if request.method == "GET":
        group = Group.objects.get(id=group_id)
        return render(request, "editgroup.html", {"group":group, "group_id":group.id})


def group_profile(request, group_id):
    group = Group.objects.get(id=group_id)
    clients_list = group.clients.all()
    clients_count = group.clients.all().count()
    return render(request, "groupprofile.html", {"group":group, "clients_list":clients_list, "clients_count":clients_count})


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


def viewmembers_under_group(request, group_id):
    group = Group.objects.get(id=group_id)
    clients_list = group.clients.all()
    clients_count = group.clients.all().count()
    return render(request, "viewmembers.html", {"group":group, "clients_list":clients_list, "clients_count":clients_count})


def groups_list(request):
    groups_list = Group.objects.all()
    return render(request, "listofgroups.html", {"groups_list":groups_list})


def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if group.staff and group.clients.all().count():
        return HttpResponse("This group can't be deleted")
    else:
        if not group.staff and not group.clients.all().count():
            print group.clients.all().count()
            group.delete()
            return HttpResponse("Group deleted suceefully")


def removemembers_from_group(request, group_id, client_id):
    group = Group.objects.get(id=group_id)
    client = Client.objects.get(id=client_id)
    group.clients.remove(client)
    group.save()
    clients_list = group.clients.all()
    clients_count = group.clients.all().count()
    return render(request, "groupprofile.html", {"group":group, "clients_list":clients_list, "clients_count":clients_count})
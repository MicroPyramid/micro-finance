from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import login, authenticate, logout
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from micro_admin.models import User, Branch
from micro_admin.forms import BranchForm, UserForm, EditbranchForm
import datetime

def index(request):
    data = {}
    data.update(csrf(request))
    return render_to_response('login.html',data)


def user_login(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        user_password = request.POST.get('password')
        user = authenticate(username=user_name, password=user_password)
        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                data = {'error':False,'message':"Loggedin Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                data = {'error':True, 'message':"User is not active."}
                return HttpResponse(json.dumps(data))
        else:
            data = {'error':True, 'message':"Username and Password were incorrect."}
            return HttpResponse(json.dumps(data))
    else:
        if request.user.is_authenticated():
            username = request.user
            user = User.objects.get(username=username)
            return render(request, 'index.html', {'user': user})


def user_logout(request):
    if not request.user.is_authenticated():
        return HttpResponse('')
    logout(request)
    return HttpResponseRedirect('/')


def create_branch(request):
    if request.method == 'GET':
        data = {}
        return render(request, 'createbranch.html', {'data':data})
    else:
        form = BranchForm(request.POST)
        if form.is_valid():
            name = request.POST.get("name")
            datestring_format = datetime.datetime.strptime(request.POST.get("opening_date"),'%m/%d/%Y').strftime('%Y-%m-%d')
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
            data = {'error':False, 'message':"Created Sucessfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {'error':True, 'message':form.errors}
            return HttpResponse(json.dumps(data))


def edit_branch(request, branch_id):
    if request.method == "GET":
        branch = Branch.objects.get(id=branch_id)
        return render(request, 'editbranchdetails.html', {'branch':branch})
    else:
        form = EditbranchForm(request.POST)
        if form.is_valid():
            branch = Branch.objects.get(id=branch_id)
            branch.country = request.POST.get('country')
            branch.state = request.POST.get('state')
            branch.district = request.POST.get('district')
            branch.city = request.POST.get('city')
            branch.area = request.POST.get('area')
            branch.phone_number = request.POST.get('phone_number')
            branch.pincode = request.POST.get('pincode')
            branch.save()
            return HttpResponse("Branch Details Updated Successfully")
        else:
            print form.errors
            return HttpResponse('Invalid Data')


def branch_profile(request):
    return HttpResponse("Branch Created Successfully")


def create_user(request):
    if request.method == 'GET':
        data = {}
        branches = Branch.objects.all()
        return render(request, 'createuser.html', {'data':data, 'branches':branches})
    else:
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user_name = request.POST.get('username')
            user_password = request.POST.get('password')
            email = request.POST.get('email')
            user = User.objects.create_user(username=user_name, email=email, password=user_password, branch=Branch.objects.get(id=request.POST.get('branch')))
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.gender = request.POST.get('gender')
            user.user_roles = request.POST.get('user_roles')
            user.country = request.POST.get('country')
            user.state = request.POST.get('state')
            user.district = request.POST.get('district')
            user.city = request.POST.get('city')
            user.area = request.POST.get('area')
            user.pincode = request.POST.get('pincode')
            date_of_birth1 = request.POST.get("date_of_birth")
            mobile1 = request.POST.get('mobile')
            if mobile1:
                user.mobile = mobile1
            if date_of_birth1:
                datestring_format = datetime.datetime.strptime(request.POST.get("date_of_birth"),'%m/%d/%Y').strftime('%Y-%m-%d')
                dateconvert = datetime.datetime.strptime(datestring_format, "%Y-%m-%d")
                user.date_of_birth = dateconvert
            user.save()
            data = {'error':False, 'user_id':user.id}
            return HttpResponse(json.dumps(data))
        else:
            data = {'error':True, 'message':user_form.errors}
            return HttpResponse(json.dumps(data))


def edit_user(request, user_id):
    if request.method == 'GET':
        user = User.objects.get(id=user_id)
        return render(request, 'edituser.html', {'user':user, 'user_id':user.id})
    else:
        user = User.objects.get(id=user_id)
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.country = request.POST.get('country')
        user.state = request.POST.get('state')
        user.district = request.POST.get('district')
        user.city = request.POST.get('city')
        user.area = request.POST.get('area')
        user.pincode = request.POST.get('pincode')
        mobile1 = request.POST.get('mobile')
        if mobile1:
            user.mobile = mobile1
        user.save()
        data = {'error':False, 'user_id':user.id}
        return HttpResponse(json.dumps(data))


def user_profile(request, user_id):
    return HttpResponse("User created sucessfully")

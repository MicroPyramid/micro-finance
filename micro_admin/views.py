from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from micro_admin.models import User


def index(request):
    data = {}
    return render_to_response('login.html',{'data':data})


@csrf_exempt
def user_login(request):
    if request.method=="POST":
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
            return render_to_response('index.html', {'user': user})      


def create_branch(request):
    if request.method == 'GET':
        return render(request, 'branchcreate.html')
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
            return render_to_response("branch_profile.html", {'branch':branch})
        else:
            return HttpResponse("Invalid Data")

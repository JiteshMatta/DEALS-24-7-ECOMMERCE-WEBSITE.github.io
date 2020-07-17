from django.shortcuts import render, redirect
from .models import Product,Contact, Orders, OrderUpdate, User123
from math import ceil
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from PayTm import Checksum
from django.contrib.auth.decorators import login_required
import json

from django.views.decorators.csrf import csrf_exempt
MERCHANT_KEY = 'type  your merchant key'

# Create your views here.
@login_required(login_url='login')
def index(request):
    allProds=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod,range(1,nSlides),nSlides])
    params={'allProds':allProds}
    return render(request,'QuickShop/index.html',params)

def searchMatch(query,item):
    if query in item.product_name or query in item.desc or query in item.category:
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!=0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds,"msg":""}
    if len(allProds)==0 or len(query)<3:
        params={"msg":"Please Enter Correct Data"}
    return render(request, 'QuickShop/search.html', params)













def about(request):
    return render(request,'QuickShop/about.html')
def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
        print(name)
    return render(request,'QuickShop/contact.html',{'thank': thank})
@login_required(login_url='login')
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    # response = json.dumps([updates, order[0].items_json], default=str)
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json},
                                          default=str)

                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'QuickShop/tracker.html')


def productview(request,myid):
    product = Product.objects.filter(id=myid)
    print(product)
    params={'product':product[0]}
    return render(request,'QuickShop/prodview.html',params)
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone,amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id,update_desc="The Order has been placed")
        update.save()
        thank = True
        id = order.order_id
        #return render(request, 'QuickShop/checkout.html', {'thank': thank, 'id': id})

        param_dict = {

            'MID': 'type your merchant id',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/QuickShop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'QuickShop/paytm.html', {'param_dict': param_dict})

    return render(request, 'QuickShop/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'QuickShop/paymentstatus.html', {'response': response_dict})




def signIn(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        cpassword = request.POST.get('cpassword', '')
        if(password==cpassword):
            if(User123.objects.filter(email=email).exists()):
                print("Email Taken ")
            else:
                user123 = User123(name=name, email=email, phone=phone, password=password)
                user123.save()
        return redirect('/QuickShop')
    else:
        return render(request,'QuickShop/signIn.html')

def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request,'Account was created for '+ user)
            return redirect('login')
    context = {'form':form}
    return render(request,'QuickShop/register.html',context)

def logIn(request):
    if(request.method=='POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.info(request,'Username OR Password Incorrect')
            return render(request, 'QuickShop/login.html')
    return render(request,'QuickShop/login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request,'QuickShop/home.html')
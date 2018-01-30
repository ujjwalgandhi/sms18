from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, Http404 ,HttpResponseForbidden
from .models import UserProfile, GameSwitch, Stock, StockPurchased
from django.shortcuts import redirect, render_to_response
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib import auth
from django.db import IntegrityError
from django.contrib.auth.models import User
import json
from .forms import TransactionForm
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

def index(request):#just a render view
    return render(request, 'main/index.html' )

def game(request):#just a render view
    return render(request, 'main/gamepage.html' )

def leaderboard(request):#just a render view
    return render(request, 'main/leaderboard.html')

def buy(request, id):#just a render view
    return render(request, 'main/buy.html')

def sell(request, id):#just a render view
    return render(request, 'main/sell.html')

def profile(request):#just a render view
    return render(request, 'main/profile.html')

def register(request):#just a render view
    if request.method == 'POST':
        data = request.POST
        try:
            obj = User.objects.get(username=data['username'])
            return redirect('form')
        except User.DoesNotExist:
            user = User.objects.create_user(data['username'], data['email'], data['password'])
            user.save()
            userProf = UserProfile.objects.create(user=user, name=data['username'], balance=100)
            userProf.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/game')



def createProfile(request):
    try:
        userProf = UserProfile.objects.get(user=request.user)
    except:
        userProf = UserProfile.objects.create(user=request.user, name=request.user.username, balance=100)
    return redirect('/game')



@csrf_exempt
def BuyStocks(request, id):
    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")
    current_user = UserProfile.objects.get(user = request.user)
    if request.method == 'POST':
        data = request.POST
        stock_info = Stock.objects.get(id=id)
        current_user.balance -= int(data['units'])*stock_info.stock_price
        current_user.save()

        try:
            current_stock = StockPurchased.objects.get(owner_id=current_user.id, stockid=stock_info)
        except:
            current_stock = StockPurchased.objects.create(owner_id=current_user.id, stockid=stock_info)

        current_stock.number_of_stocks += int(data['units'])
        current_stock.save()
        return redirect('/game')



@csrf_exempt
def SellStocks(request, id):
    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")
    current_user = UserProfile.objects.get(user = request.user)
    if request.method == 'POST':
        data = request.POST
        stock_info = Stock.objects.get(id=id)
        current_user.balance += int(data['units'])*stock_info.stock_price
        current_user.save()
        current_stock = StockPurchased.objects.get(owner=current_user.id, stockid=stock_info)
        current_stock.number_of_stocks -= int(data['units'])
        if current_stock.number_of_stocks is 0:
            current_stock.delete()
        else:
            current_stock.save()
        return redirect('/game')



def UserPrimaryDetails(request): #this view will give you all info of the user! Check out the fields.

    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")
    current_user = UserProfile.objects.get(user = request.user)
    resp={
        'username': current_user.name ,
        'email-id': current_user.mail_id ,
        'user_balance': current_user.balance ,
    }
    return HttpResponse(json.dumps(resp), content_type = "application/json")
    #I havent renderred any template. This view is only for pinging and sending data



def UserStockDetails(request):
    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")
    current_user = UserProfile.objects.get(user = request.user)
    UserStocks = StockPurchased.objects.filter(owner=current_user)
    StocksData = []
    for this_stock in UserStocks:
        current_stock = Stock.objects.get(id=this_stock.stockid.id)
        stock_data = {
        "name" : current_stock.product_name,
        "num" : this_stock.number_of_stocks,
        "price" : current_stock.stock_price,
        }
        #this will send the name of the stock along with the number of units the user is currently owning
        StocksData.append(stock_data)

    return HttpResponse(json.dumps(StocksData), content_type = "application/json")



def StocksPrimaryData(request):

    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")
    All_stocks = Stock.objects.all()
    StocksData = []

    for this_stock in All_stocks:
        stock_data = {
            "id" : this_stock.id,
            "name" : this_stock.product_name,
            "price" : this_stock.stock_price,
        }
        StocksData.append(stock_data)

    return HttpResponse(json.dumps(StocksData), content_type = "application/json")



def StockData(request, id):

    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")

    this_stock = Stock.objects.get(id = id)
    num = 0
    try:
        current_stock = StockPurchased.objects.get(owner=UserProfile.objects.get(user = request.user), stockid=this_stock)
        num = current_stock.number_of_stocks
    except:
        pass
    stock_data = {
        "name" : this_stock.product_name,
        "price" : this_stock.stock_price,
        "num" : num
    }

    return HttpResponse(json.dumps(stock_data), content_type = "application/json")



def LBdata(request):
    if not request.user.is_authenticated():
        resp={
            'error':'The user is not registered yet.'
        }
        return HttpResponse(json.dumps(resp), content_type = "application/json")

    for this_user in UserProfile.objects.all():
        this_user.net_worth=0
        for this_stock in StockPurchased.objects.filter(owner=this_user):
            this_user.net_worth+=this_stock.number_of_stocks * (this_stock.stockid).stock_price
        this_user.net_worth+=this_user.balance
        this_user.save()
    up = UserProfile.objects.order_by('-net_worth')
    x = 20
    n = len(up)
    up = up[:abs(x-n)]
    d=[]
    for i in up:
        if i.net_worth>0:
            d.append({
                'name':i.name,
                'net_worth':i.net_worth
                })
    return HttpResponse(json.dumps(d), content_type = "application/json")


from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .forms import  CreateUserForm
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
def store(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer = customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
            print('CART:', cart)

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

        for i in cart:
            #We use try block to prevent items in cart that may have been removed from causing error
            try:	
                if(cart[i]['quantity']>0): #items with negative quantity = lot of freebies  
                    cartItems += cart[i]['quantity']

                    product = Product.objects.get(id=i)
                    total = (product.price * cart[i]['quantity'])

                    order['get_cart_total'] += total
                    order['get_cart_items'] += cart[i]['quantity']

                    item = {
                    'id':product.id,
                    'product':{'id':product.id,'name':product.name, 'price':product.price, 
                    'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
                    'digital':product.digital,'get_total':total,
                    }
                    items.append(item)

                    if product.digital == False:
                        order['shipping'] = True
            except:
                pass
                

    context = {'products':products , 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    # items = OrderItem.objects.all()
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer = customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
            print('CART:', cart)

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

        for i in cart:
            #We use try block to prevent items in cart that may have been removed from causing error
            try:	
                if(cart[i]['quantity']>0): #items with negative quantity = lot of freebies  
                    cartItems += cart[i]['quantity']

                    product = Product.objects.get(id=i)
                    total = (product.price * cart[i]['quantity'])

                    order['get_cart_total'] += total
                    order['get_cart_items'] += cart[i]['quantity']

                    item = {
                    'id':product.id,
                    'product':{'id':product.id,'name':product.name, 'price':product.price, 
                    'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
                    'digital':product.digital,'get_total':total,
                    }
                    items.append(item)

                    if product.digital == False:
                        order['shipping'] = True
            except:
                pass
                

    context = {'items':items, 'order':order , 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer = customer , complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
            print('CART:', cart)

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

        for i in cart:
            #We use try block to prevent items in cart that may have been removed from causing error
            try:	
                if(cart[i]['quantity']>0): #items with negative quantity = lot of freebies  
                    cartItems += cart[i]['quantity']

                    product = Product.objects.get(id=i)
                    total = (product.price * cart[i]['quantity'])

                    order['get_cart_total'] += total
                    order['get_cart_items'] += cart[i]['quantity']

                    item = {
                    'id':product.id,
                    'product':{'id':product.id,'name':product.name, 'price':product.price, 
                    'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
                    'digital':product.digital,'get_total':total,
                    }
                    items.append(item)

                    if product.digital == False:
                        order['shipping'] = True
            except:
                pass
                
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)
    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order,created = Order.objects.get_or_create(customer = customer,complete=False)
    orderItem,created = OrderItem.objects.get_or_create(product= product, order = order)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('item was added ', safe=False)


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    print(data)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )
    else:
        customer, order = guestOrder(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )
    return JsonResponse('Payment submitted..', safe=False)        


def registerPage(request):
    form = CreateUserForm(request.POST)
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            Customer.objects.create(
                user = user,
                name = user.username,
            )
            messages.success(request, 'account was created for ' + username)
            return redirect('login')
    context = {'form':form}
    return render(request, 'store/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password')
    
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
                messages.info(request,'Username or password is incrorrect')
    context = {}
    return render(request, 'store/login.html', context)
def logoutUser(request):
	logout(request)
	return redirect('store')


from rest_framework.response import Response
from rest_framework.views import APIView
from .models import  MoringaMerch
from .serializer import MerchSerializer
from rest_framework import status
class MerchList(APIView):
    def get(self, request, format=None):
        all_merch = MoringaMerch.objects.all()
        serializers = MerchSerializer(all_merch, many=True)
        return Response(serializers.data)
    def post(self, request, format=None):
        serializers = MerchSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
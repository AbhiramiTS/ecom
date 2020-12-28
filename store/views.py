from django.shortcuts import render, redirect 
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from .productFilter import ProductNameFilter
from .forms import CreateUserForm

def registerPage(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			user_object = User.objects.get(username=username)
			Customer.objects.create(user=user_object, name=username)

			messages.success(request, 'Account was created for ' + username)

			return redirect('login')
		

	context = {'form':form}
	return render(request, 'store/register.html', context)

def loginPage(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('store')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'store/login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('store')


def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	current_user = request.user
	products = Product.objects.filter(product_type1='Men')
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def allProducts(request, pk_test):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	# ELECTRONICS:
	if pk_test == '40':
		products = Product.objects.filter(product_type1='Electronics').filter(product_type2='Mobiles')
	if pk_test == '41':
		products = Product.objects.filter(product_type1='Electronics').filter(product_type2='Laptops')

	# MEN:
	if pk_test == '00':
		products = Product.objects.filter(product_type1='Men')
	if pk_test == '01':
		products = Product.objects.filter(product_type1='Men').filter(product_type2='Watches')
	if pk_test == '02':
		products = Product.objects.filter(product_type1='Men').filter(product_type2='Shoes').filter(product_type2='Bags')

	# WOMEN:
	if pk_test == '10':
		products = Product.objects.filter(product_type1='Women')
	if pk_test == '11':
		products = Product.objects.filter(product_type1='Women').filter(product_type2='Handbags')
	if pk_test == '12':
		products = Product.objects.filter(product_type1='Women').filter(product_type2='Watches')

	# KIDS:
	if pk_test == '20':
		products = Product.objects.filter(product_type1='Kids').filter(product_type2='Boys')
	if pk_test == '21':
		products = Product.objects.filter(product_type1='Kids').filter(product_type2='Girls')

	# HOME & LIVING:
	if pk_test == '30':
		products = Product.objects.filter(product_type1='Home').filter(product_type2='Bedsheets')
	if pk_test == '31':
		products = Product.objects.filter(product_type1='Home').filter(product_type2='Decor')

	# DIGITAL PRODUCTS
	if pk_test == '50':
		products = Product.objects.filter(product_type1='digital')
	
	first_product = products.first()
	if first_product is not None:
		tag1 = f"{first_product.product_type1}"
		if first_product.product_type2 is not None:
			tag2 = tag1 + f" >> {first_product.product_type2}"
			if first_product.product_type3 is not None:
				tag3 = tag2 + f" >> {first_product.product_type3}"
			else:
				tag3 = tag2 + ""
		else:
			tag2 = tag1 + ""
			tag3 = tag2
	else:
		tag3 = ""
		
	tag = tag3

	myFilter = ProductNameFilter(request.GET, queryset=products)
	products = myFilter.qs 

	context = {'products':products, 'cartItems':cartItems, 'pk_test':pk_test, 'myFilter':myFilter, 'tag':tag}
	return render(request, 'store/all_products.html', context)

def offers(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	mobiles = Product.objects.filter(product_type1='Electronics').filter(product_type2='Mobiles')
	men = Product.objects.filter(product_type1='Men')
	watches = Product.objects.filter(product_type1='Kids').filter(product_type2='Watches')

	context = {'mobiles':mobiles, 'men':men, 'watches':watches, 'cartItems':cartItems}
	return render(request, 'store/offers.html', context)



def itemView(request, pk_test):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.filter(id=pk_test)
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/item_view.html', context)

# The Search Button
@csrf_exempt
def products(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	
	if request.method == 'POST':
		value = request.POST.get("username")
		products = Product.objects.filter(Q(product_type1=value) | Q(name__icontains=value) | Q(product_type2=value) | Q(product_type3=value))
		first_product = products.first()

		if first_product is not None:
			tag1 = f"{first_product.product_type1}"
			if first_product.product_type2 is not None:
				tag2 = tag1 + f" >> {first_product.product_type2}"
				if first_product.product_type3 is not None:
					tag3 = tag2 + f" >> {first_product.product_type3}"
				else:
					tag3 = tag2 + ""
			else:
				tag2 = tag1 + ""
				tag3 = tag2
		else:
			tag3 = ""

		tag = tag3

		context = {'products':products,'tag':tag, 'cartItems':cartItems}	
		return render(request, 'store/all_products.html', context)


	products = Product.objects.all()
	context = {'products':products}
	return render(request, 'store/men.html', context)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
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
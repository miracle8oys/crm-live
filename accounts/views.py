from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .form import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

# Create your views here.


@unauthenticated_user
def registerPage(request):
    """
    Register form
    """
    form = CreateUserForm()

    if request.POST:
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    """
    Login form
    """
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Usrname or Password is incorrect')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    """
    User Profile Data
    """
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
    }
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    """
    Accounts Setting Page
    """
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.POST:
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {
        'form': form,
    }
    return render(request, 'accounts/account_settings.html', context)


def logoutUser(request):
    """
    Logout view
    """
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    """
    Home Page
    """
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {
        'orders': orders,
        'customers': customers,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
        'total_customers': total_customers,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    """
    Product List Page
    """
    products = Product.objects.all()
    context = {
        'products': products,

    }
    return render(request, 'accounts/products.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, id_customer):
    """
    Customer List Page
    """
    customer = Customer.objects.get(id=id_customer)
    orders = customer.order_set.all()
    total_orders = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'myFilter': myFilter,
    }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
def create_order(request, id_customer):
    """
    Create Order Form
    """
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=3)
    customer = Customer.objects.get(id=id_customer)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    #form = OrderForm(initial={'customer': customer})

    if request.POST:
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {
        'formset': formset,
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
def update_order(request, id_order):
    """
    Update Order Form
    """
    order = Order.objects.get(id=id_order)
    form = OrderForm(instance=order)

    if request.POST:
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {
        'form': form,
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
def delete_order(request, id_order):
    """
    Delete Order
    """
    order = Order.objects.get(id=id_order)
    order.delete()
    return redirect('/')

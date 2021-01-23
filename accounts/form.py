from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Customer


class OrderForm(ModelForm):
    """
    Form to Create Models
    """
    class Meta:
        model = Order
        fields = '__all__'


class CreateUserForm(UserCreationForm):
    """
    Form to Create User
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomerForm(ModelForm):
    """
    Customer Setting Form
    """
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']

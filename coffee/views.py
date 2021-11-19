from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib import messages
from coffee.models import Category,Order,OrderItem,Product,Cart,CartItem
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
import stripe
# Create your views here.
def index(request):
    return render(request,'signin.html')

def order(request,category_slug=None):
    products=None
    category_page=None
    if category_slug!=None:
        category_page=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.all().filter(category=category_page,available=True)
    else:
        products=Product.objects.all().filter(available=True)

    return render(request,'order.html',{'products':products,'category':category_page})

def signup(request):
    return render(request,'signup.html')

def addForm(request):
    username=request.POST['username']
    email=request.POST['email']
    no=request.POST['no']
    password=request.POST['password']
    con_password=request.POST['con_password']
    if password==con_password:
        if User.objects.filter(username=username).exists():
            messages.info(request,'username นี้มีคนใช้แล้ว')
            return redirect('signUp')
        elif User.objects.filter(email=email).exists():
            messages.info(request,'email นี้มีคนใช้แล้ว')
            return redirect('signUp')
        else:
            user = User.objects.create_user(
            username=name,
            password=password,
            last_name=no,
            email=emails
            )
            user.save()
            return redirect('order')
    else:
        messages.info(request,'password ไม่ตรง')
        return redirect('signUp')

    return render(request,'signin.html')

def login(request):
    name=request.POST['username']
    password=request.POST['password']
    #check username password
    user = auth.authenticate(username=name,password=password)
    if user is not None:
        auth.login(request,user)
        return redirect('order')
    else:
        messages.info(request,'ไม่พบข้อมูล')
        return redirect('login')

def logout(request):
    auth.logout(request)
    return redirect('home')

def product(request):
    return render(request,'order.html')

def productPage(request,category_slug,product_slug):
    try:
        product=Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    return render(request,'orderdetails.html',{'product':product})

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def addCart(request,product_id):
    if request.method == "GET":
        sugar=request.GET.get('SugarLevel')
        product=Product.objects.get(id=product_id)
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))
            cart.save()
        
        try:
            #same order
            cart_item=CartItem.objects.get(product=product,cart=cart,sugar=sugar)
            cart_item.quantity+=1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item=CartItem.objects.create(
                product=product,
                sugar=sugar,
                cart=cart,
                quantity=1
            )
            cart_item.save()
        return redirect('order')

def cartdetail(request):
    total=0
    counter=0
    cart_items=None
    try:
        #pull cart
        cart=Cart.objects.get(cart_id=_cart_id(request))
        #pull info product in cart
        cart_items=CartItem.objects.filter(cart=cart,active=True)
        for item in cart_items:
            total+=(item.product.price * item.quantity)
            counter+=item.quantity
    except Exception as e:
        pass

    stripe.api_key=settings.SECRET_KEY
    stripe_total=int(total*100)
    description="Payment online"
    data_key=settings.PUBLIC_KEY

    if request.method=="POST":
        try :
            token=request.POST['stripeToken']
            email=request.POST['stripeEmail']
            name=request.POST['stripeShippingName']
            address=request.POST['stripeShippingAddressLine1']
            city=request.POST['stripeShippingAddressCity']
            postcode=request.POST['stripeShippingAddressZip']
            
            customer=stripe.Customer.create(
                email=email,
                source=token
            )
            charge=stripe.Charge.create(
                amount=stripe_total,
                currency='thb',
                description=description,
                customer=customer.id
            )
            #save order
            order=Order.objects.create(
                name=name,
                address=address,
                city=city,
                postcode=postcode,
                total=total,
                email=email,
                token=token
            )
            order.save()

            #save OderItem
            for item in cart_items:
                order_item=OrderItem.objects.create(
                    product=item.product.name,
                    quantity=item.quantity,
                    sugar=item.sugar,
                    price=item.product.price,
                    order=order
                )
                order_item.save()

                #delete stock
                product=Product.objects.get(id=item.product.id)
                product.save()
                item.delete()
            return redirect('thankyou')

        except stripe.error.CardError as e:
            return False,e

    return render(request,'cartdetails.html',
    dict(cart_items=cart_items,total=total,counter=counter,
    data_key=data_key,
    stripe_total=stripe_total,
    description=description
    ))

def removeCart(request,id):
    CartItem.objects.filter(id=id).delete()
    return redirect('cartdetail')

def thankyou(request):
    return render(request,'thankyou.html')

def orderHistory(request):
    if request.user.is_authenticated:
        email=str(request.user.email)
        orders=Order.objects.filter(email=email)
    return render(request,'orderhistory.html',{'orders':orders})

def viewOrder(request,order_id):
    if request.user.is_authenticated:
        email=str(request.user.email)
        order=Order.objects.get(email=email,id=order_id)
        orderitem=OrderItem.objects.filter(order=order)
    return render(request,'orderhisdetail.html',{'order':order,'order_items':orderitem})

def search(request):
    products=Product.objects.filter(name__icontains=request.GET['title'])
    return render(request,'order.html',{'products':products})
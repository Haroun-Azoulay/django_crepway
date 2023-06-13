from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, Cart, Order
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views import generic
import stripe
from decimal import Decimal
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.db import transaction
from datetime import datetime
from django.utils import timezone
import requests
import base64
import os
from dotenv import load_dotenv


load_dotenv()

# Create your views here.

def index(request):
    products = Product.objects.all()


    context = {
        'products': products,
    }

    return render(request, 'store/index.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={"product": product})

def add_to_cart(request, slug):
    user = request.user #get user
    product = get_object_or_404(Product, slug=slug) #recover product if exists we pass slug
    cart, _ = Cart.objects.get_or_create(user = user) #if product exists we recup cart if no cart create
    order, created = Order.objects.get_or_create(user=user, ordered=False, product=product) # found db associate
    
    if not product.stock:
        return redirect(reverse("product", kwargs={"slug": slug}) + "?error=product_unavailable")

    
    else:

        if created: # if product created
            cart.orders.add(order)
            cart.save()
        
        else: # if already exists 
            order.quantity += 1
            order.save()

        return redirect(reverse("product", kwargs={"slug":slug}))


@login_required(login_url='login')
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        orders = cart.orders.all()
        if orders:
            total_price = sum(order.product.price * order.quantity for order in orders)
        else:
            total_price = 0  # Set total price to 0 if cart is empty

    except Cart.DoesNotExist:
        cart = None
        orders = []
        total_price = 0

    context = {
        'cart': cart,
        'orders': orders,
        'total_price': total_price,
    }

    return render(request, 'store/cart.html', context=context)


def delete_cart(request):
    if cart := request.user.cart:
        cart.delete()

    return redirect('index')

        
def menu(request):
    products = Product.objects.all()
    return render(request, 'store/menu.html', context={"products": products})

@login_required(login_url='login')
def payment(request):
    cart = Cart.objects.get(user=request.user)
    orders = cart.orders.all()


    from django.utils import timezone

def payment(request):
    cart = Cart.objects.get(user=request.user)
    orders = cart.orders.all()
   

    
    return render(request, 'store/payment.html', context={'orders': orders})



stripe.api_key = settings.STRIPE_SECRET_KEY
def checkout(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    city = request.POST.get('city')
    address = request.POST.get('address')
    address_info = request.POST.get('address_info')
    request_info = request.POST.get('request_info')

    # Get cart and associated orders

    cart = Cart.objects.get(user=request.user)
    orders = cart.orders.all()

    # Calculate the total price of the basket taking into account the quantities
    total_price = sum(order.product.price * order.quantity for order in orders)

    # Create a Stripe Checkout payment session
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': int(total_price * 100),
                    'product_data': {
                        'name': 'Total du panier',
                    },
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_confirm')) + '?success=true',
        cancel_url=request.build_absolute_uri(reverse('cart')),
    )

    if checkout_session.id:
        request.session['checkout_address_info'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'city': city,
            'address': address,
            'address_info': address_info,
            'request_info': request_info,
        }
        
        return redirect(checkout_session.url)
    else:
        # Handle payment session creation error
        messages.error(request, 'Une erreur s\'est produite lors de la création de la session de paiement.')
        return redirect(checkout_session.url, code=303)


def payment_confirm(request):
    if request.GET.get('success'):
        # Get cart and associated orders
        cart = Cart.objects.get(user=request.user)
        orders = cart.orders.all()

        # Calculate the total price of the basket taking into account the quantities
        total_price = sum(order.product.price * order.quantity for order in orders)

        # Retrieve address information from session
        address_info = request.session.get('checkout_address_info', {})

        # Mark orders as "ordered=true" and record order date
        with transaction.atomic():
            for order in orders:
                order.ordered = True
                order.ordered_date = timezone.now()
                order.save()

        cart.orders.clear()
        cart.delete()

        # Construct the email message using the retrieved address information
        product_details = [
            f"- {order.product.name}: Quantité {order.quantity}, Prix unitaire {order.product.price}, Prix total { order.total_price }€"
            for order in orders
        ]
        products_message = '\n'.join(product_details) + '\n'

        email_subject_order = f'Nouvelle commande reçue {address_info.get("first_name", "")} {address_info.get("last_name", "")}'
        email_message_order = f'Une nouvelle commande a été passée.\n\nDétails de la commande:\n{products_message}\n\nRenseignements d\'adresse:\nPrénom: {address_info.get("first_name", "")}\nNom: {address_info.get("last_name", "")}\nE-mail: {address_info.get("email", "")}\nTéléphone: {address_info.get("phone", "")}\nVille: {address_info.get("city", "")}\nAdresse: {address_info.get("address", "")}\nAutre information sur l\'adresse: {address_info.get("address_info", "")}\n\nDemandes particulières: {address_info.get("request_info", "")}\n\nPrix total du panier : {total_price} €.'

        # Send confirmation email
        send_mail(email_subject_order, email_message_order, settings.DEFAULT_FROM_EMAIL, ['noreply.creepway93@gmail.com'])

         # Build the message of the receipt email to the customer
        email_subject_customer = f'Reçu de commande - {address_info.get("first_name", "")} {address_info.get("last_name", "")}'
        
        # Build the content of the email for the customer
        email_body_customer = f'''
        Cher(e) {address_info.get("first_name", "")} {address_info.get("last_name", "")},
        
        Merci d'avoir passé une commande. Voici le récapitulatif de votre commande :

        Détails de la commande :
        {products_message}

        Renseignements d'adresse :
        Prénom: {address_info.get("first_name", "")}
        Nom: {address_info.get("last_name", "")}
        E-mail: {address_info.get("email", "")}
        Téléphone: {address_info.get("phone", "")}
        Ville: {address_info.get("city", "")}
        Adresse: {address_info.get("address", "")}
        Autre information sur l'adresse: {address_info.get("address_info", "")}

        Prix total du panier : {total_price} €.

        Merci de votre commande !
        '''

        # Create the Email Message object for the email to the customer
        email_message_customer = EmailMessage(
            subject=email_subject_customer,
            body=email_body_customer,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[address_info.get("email", "")]
        )

        # Send email to customer
        email_message_customer.send()

        # Print order details
        text_to_print = f"{email_subject_order}\n\n{email_message_order}"
        print_commande(text_to_print)

        
        success_message = 'Le paiement a été confirmé. Merci de votre commande.'
        return render(request, 'store/payment_confirm.html', {'success_message': success_message})

    return render(request, 'store/payment_confirm.html')

def print_commande(text_to_print):
    api_key = os.environ.get("API_KEY")
    printnode_url = os.environ.get("PRINTNODE_URL")

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.b64encode(api_key.encode("utf-8")).decode("utf-8")
    }

    printer_id = YOUR_ID

    
    encoded_text = base64.b64encode(text_to_print.encode("utf-8")).decode("utf-8")

    data = {
        "printerId": printer_id,
        "title": "Titre de l'impression",
        "contentType": "raw_base64",
        "content": encoded_text
    }

    response = requests.post(printnode_url, json=data, headers=headers)

    if response.status_code == 200:
        print("Impression lancée avec succès.")
    else:
        print("Échec de l'impression.")
        print(response.text)

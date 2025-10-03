import json

from rest_framework import status

# API
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperuser
from .serializers import *

from django.db.models import Count, Sum
from django.views.generic import DetailView
from vi_address.models import City, District, Ward
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from datetime import timezone
from django.contrib.auth import logout, authenticate, login
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from home.models import *
from django.conf import settings
from datetime import datetime, date

# VNPAY import
from home.forms import PaymentForm
from .vnpay import vnpay
from datetime import datetime as dt
from django.utils import timezone

# Google map
import googlemaps
from datetime import datetime
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim

# Create your views here.
CITIES = City.objects.all().order_by("name")
DISTRICTS = District.objects.all().order_by("name")
WARDS = Ward.objects.all().order_by("name")


def get_best_selling_item():
    current_date = timezone.now()
    seven_days_ago = current_date - timezone.timedelta(days=7)
    recent_orders = Payment.objects.filter(
        order_placed_at__range=[seven_days_ago, current_date], paid=True
    )
    item_sales = {}
    for order in recent_orders:
        line_items = order.items.all()
        for line_item in line_items:
            item_id = line_item.item.id
            item_sales[item_id] = item_sales.get(item_id, 0) + line_item.quantity
    best_selling_item_id = max(item_sales, key=item_sales.get)
    best_selling_item = Item.objects.get(id=best_selling_item_id)
    return best_selling_item


def home(request):
    best_selling_item = get_best_selling_item()
    categories_list = []
    for choice in CATEGORY_CHOICES:
        category = {
            "key": choice[0],
            "value": choice[1],
        }
        categories_list.append(category)
    context = {"categories": categories_list, 'best_selling_item': best_selling_item}
    return render(request, "home/main.html", context)


def menu(request):
    categories_list = []
    for choice in CATEGORY_CHOICES:
        category = {
            "key": choice[0],
            "value": choice[1],
        }
        categories_list.append(category)
    context = {"categories": categories_list}
    return render(request, "home/menu.html", context)


def about(request):
    return render(request, "home/about.html")


def book_table(request):
    return render(request, "home/book-table.html")


# lấy item dựa trên category hoặc query
def get_items(request, category=None, query=None):
    if category:
        items = Item.objects.filter(category=category).order_by("slug")
    elif query:
        items = Item.objects.filter(title__icontains=query)
    else:
        items = Item.objects.all().order_by("slug")

    data = []

    for obj in items:
        item = {
            "title": obj.title,
            "price": obj.price,
            "description": obj.description,
            "image": obj.image.url,
            "slug": obj.slug,
            "category": obj.category,
            "get_absolute_url": obj.get_absolute_url(),
            "get_final_price": obj.get_final_price(),
            "discount": obj.discount,
        }
        data.append(item)

    paginator = Paginator(data, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    items = list(page)

    return JsonResponse(
        {
            "items": items,
            "has_next": page.has_next(),
            "has_previous": page.has_previous(),
            "page_number": page_number,
            "num_pages": paginator.num_pages,
        }
    )


# lấy item khi vào trang web
def load_items_data_view(request):
    try:
        address_payment_request(request)
        return get_items(request)
    except:
        return get_items(request)


# lấy item khi chọn category
def categories(request):
    category = request.GET.get("category")
    if category == "All":
        category = None
    return get_items(request, category=category)


# lấy item khi search
def search_item(request):
    query = request.GET.get("query")
    return get_items(request, query=query)


# Đăng xuất
def logoutPage(request):
    logout(request)
    return redirect("/")


# Đăng nhập hoặc đăng ký
def register_login(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        if "signin-btn" in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "Account does not exist!")
                return redirect("home:login")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )

                # Move guest cart to user cart
                device = request.COOKIES.get("device")
                guest, created = Guest.objects.get_or_create(device=device)

                # Get guest cart and user cart
                guest_cart = Cart.objects.get_or_create(guest=guest, ordered=False)
                guest_cart = guest_cart[0]
                user_cart = Cart.objects.get_or_create(user=user, ordered=False)
                user_cart = user_cart[0]

                # Move items from guest cart to user cart
                for item in guest_cart.items.all():
                    # Create ordering Item like adding to cart
                    order_item, created = LineItem.objects.get_or_create(
                        item=item.item,
                        title=item.title,
                        user=user,
                        ordered=False,
                        slug=item.slug,
                        price_each=item.item.get_final_price(),
                        img=item.img,
                    )

                    if user_cart.items.filter(item__slug=item.slug).exists():
                        order_item.quantity += item.quantity
                        order_item.save()
                    else:
                        order_item.quantity += item.quantity - 1
                        order_item.save()
                        user_cart.items.add(order_item)

                # Delete guest_cart and guest
                guest_cart.delete()
                guest.delete()

                user_cart.save()
                return redirect("home:home")
            else:
                messages.error(request, "Invalid account or password!")
                return redirect("home:login")

        elif "signup-btn" in request.POST:
            username = request.POST.get("username_signup")
            password = request.POST.get("password_signup")
            email = request.POST.get("email_signup")
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect("home:login")
            else:
                try:
                    user = User.objects.get(username=username)
                    messages.error(request, "Account already exists!")
                    return redirect("home:login")
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        username=username, email=email, password=password
                    )
                    userprofile = UserProfile.objects.get_or_create(user=user)
                    cart = Cart.objects.get_or_create(user=user, ordered=False)
                    default_address = Address.objects.create(user=user, is_default=True)

                    # Move guest cart to user cart
                    device = request.COOKIES.get("device")
                    guest, created = Guest.objects.get_or_create(device=device)

                    # Get guest cart and user cart
                    guest_cart = Cart.objects.get_or_create(guest=guest, ordered=False)
                    guest_cart = guest_cart[0]
                    user_cart = Cart.objects.get_or_create(user=user, ordered=False)
                    user_cart = user_cart[0]

                    # Move items from guest cart to user cart
                    for item in guest_cart.items.all():
                        item.user = user
                        item.guest = None
                        item.save()
                        user_cart.items.add(item)
                        user_cart.save()

                    # Delete guest_cart and guest
                    guest_cart.delete()
                    guest.delete()

                    user.save()
                    messages.success(request, "Registration successful!")
                    login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    return redirect("home:home")
    context = {"page": page}
    return render(request, "home/login.html", context)


def add_to_cart(request):
    if request.user.is_authenticated:
        # Handle user logins but not logged in
        user = get_user(request)

        slug = request.POST.get("slug")
        quantity = request.POST.get("quantity")
        item = get_object_or_404(Item, slug=slug)

        # Create ordering Item
        order_item, created = LineItem.objects.get_or_create(
            item=item,
            title=item.title,
            user=user,
            ordered=False,
            slug=item.slug,
            price_each=item.get_final_price(),
            img=item.image.url,
        )

        # Create and Update cart
        cart_qs = Cart.objects.filter(user=user, ordered=False)
        if cart_qs.exists():
            # Each user has only one cart, so get the first one
            cart = cart_qs.first()

            # Check if the order item is in the cart
            if cart.items.filter(item__slug=item.slug).exists():
                order_item.quantity += int(quantity)
                order_item.save()
            else:
                cart.items.add(order_item)
                order_item.quantity += int(quantity) - int(1)
                order_item.save()
        else:
            ordered_date = timezone.now()
            cart = Cart.objects.create(user=request.user)
            cart.items.add(order_item)
            cart.save()

        # Count items in cart
        cart_item_count = cart.items.count()
        return JsonResponse(
            {
                "message": "Thêm sản phầm vào giỏ hàng thành công",
                "cart_item_count": cart_item_count,
            }
        )
    else:
        # return JsonResponse(
        #     {"error": "Vui lòng đăng nhập để thêm sản phẩm!"}, status=403
        # )
        device = request.COOKIES.get("device")
        guest, created = Guest.objects.get_or_create(device=device)

        slug = request.POST.get("slug")
        item = get_object_or_404(Item, slug=slug)

        # Create ordering Item
        order_item, created = LineItem.objects.get_or_create(
            item=item,
            title=item.title,
            guest=guest,
            ordered=False,
            slug=item.slug,
            price_each=item.get_final_price(),
            img=item.image.url,
        )

        # Create and Update cart
        cart_qs = Cart.objects.filter(guest=guest, ordered=False)
        if cart_qs.exists():
            # Each user has only one cart, so get the first one
            print("cart exist")
            cart = cart_qs.last()
            print(cart)

            # Check if the order item is in the cart
            if cart.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
            else:
                cart.items.add(order_item)
        else:
            ordered_date = timezone.now()
            cart = Cart.objects.create(guest=guest)
            cart.items.add(order_item)
            cart.save()

        # Count items in cart
        cart_item_count = cart.items.count()
        return JsonResponse(
            {
                "message": "Thêm sản phầm vào giỏ hàng thành công",
                "cart_item_count": cart_item_count,
            }
        )


def get_user(request):
    try:
        user = request.user
        return user
    except User.DoesNotExist:
        return redirect("home:login")


class summary_cartView(View):
    template = "home/cart_summary.html"
    login_url = "/login/"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            address_payment_request(self.request)
            order, created = Cart.objects.get_or_create(user=self.request.user)

            line_items_to_add = LineItem.objects.filter(
                user=self.request.user, ordered=False
            )
            order.items.add(*line_items_to_add)
            optional_addresses = Address.objects.filter(
                user=self.request.user, is_default=False
            )

            default_address, create = Address.objects.get_or_create(
                user=self.request.user, is_default=True
            )
            order.save()
            if default_address.city == "":
                is_blank = True
                context = {
                    "object": order,
                    "optional_addresses": optional_addresses,
                    "cities": CITIES,
                    "districts": DISTRICTS,
                    "wards": WARDS,
                    "is_blank": is_blank,
                }
                return render(self.request, "home/cart_summary.html", context)
            else:
                is_blank = False
                city_id = CITIES.filter(name=default_address.city).first().id
                district_id = DISTRICTS.filter(name=default_address.district).first().id
                context = {
                    "object": order,
                    "default_address": default_address,
                    "optional_addresses": optional_addresses,
                    "cities": CITIES,
                    "districts": DISTRICTS,
                    "wards": WARDS,
                    "city_id": city_id,
                    "district_id": district_id,
                    "is_blank": is_blank,
                }
                return render(self.request, "home/cart_summary.html", context)
        else:
            device = self.request.COOKIES.get("device")
            guest, created = Guest.objects.get_or_create(device=device)
            order, created = Cart.objects.get_or_create(guest=guest)
            line_items_to_add = LineItem.objects.filter(guest=guest, ordered=False)
            order.items.add(*line_items_to_add)
            order.save()
            is_blank = True
            cart_item_count = order.items.count()
            print(cart_item_count)
            context = {
                "object": order,
                # "optional_addresses": optional_addresses,
                "cities": CITIES,
                "districts": DISTRICTS,
                "wards": WARDS,
                "is_blank": is_blank,
                "cart_item_count": cart_item_count,
            }

            return render(self.request, "home/cart_summary.html", context)


# View bills of user
class billingView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, *args, **kwargs):
        address_payment_request(self.request)
        template = "home/billing.html"
        order, created = Cart.objects.get_or_create(user=self.request.user)
        bill_list = Payment.objects.filter(user=self.request.user)

        # default_address = Address.objects.get(user=self.request.user, is_default=True)
        # optional_addresses = Address.objects.filter(
        #     user=self.request.user, is_default=False
        # )

        context = {
            "object": bill_list,
            # "optional_addresses": optional_addresses,
            # "default_address": default_address,
        }
        # reload order summary
        # reload_order_summary(self.request)

        return render(self.request, template, context)


# Change quantity of item in cart
def update_item(request):
    slug = request.POST.get("slug")
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_item, created = LineItem.objects.get_or_create(
            item=item,
            title=item.title,
            user=request.user,
            ordered=False,
            slug=item.slug,
            price_each=item.get_final_price(),
            img=item.image.url,
        )
        order_qs = Cart.objects.filter(user=request.user, ordered=False)

    else:
        device = request.COOKIES.get("device")
        guest, created = Guest.objects.get_or_create(device=device)
        item = get_object_or_404(Item, slug=slug)
        order_item, created = LineItem.objects.get_or_create(
            item=item,
            title=item.title,
            guest=guest,
            ordered=False,
            slug=item.slug,
            price_each=item.get_final_price(),
            img=item.image.url,
        )
        order_qs = Cart.objects.filter(guest=guest, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if request.POST.get("action") == "plus":
            order_item.quantity = order_item.quantity + 1
        else:
            order_item.quantity = order_item.quantity - 1

        order_item.save()

        if order_item.quantity <= 0:
            order_item.delete()
            order.items.remove(order_item)
            order.save()

        cart_sum = int(order.items.count())
        total_price = Cart.get_total(order)
        price = int(order_item.quantity * order_item.item.get_final_price())

        return JsonResponse(
            {
                "quantity": order_item.quantity,
                "id": order_item.item.id,
                "price": price,
                "sum": cart_sum,
                "totalPrice": total_price,
            },
            safe=False,
        )
    else:
        order_item.delete()

    order = order_qs[0]
    price = float(order_item.quantity * order_item.item.price)
    total_price = Cart.get_total(order)

    return JsonResponse(
        {
            "quantity": order_item.quantity,
            "id": order_item.item.id,
            "price": price,
            "totalPrice": total_price,
        },
        safe=False,
    )


# Xóa khỏi giỏ hàng
def remove_from_cart(request):
    slug = request.POST.get("slug")
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_qs = Cart.objects.filter(user=request.user, ordered=False)
        order_item, created = LineItem.objects.get_or_create(
            item=item,
            title=item.title,
            user=request.user,
            ordered=False,
            slug=item.slug,
            price_each=item.get_final_price(),
            img=item.image.url,
        )
    else:
        # Handle guest
        device = request.COOKIES.get("device")
        guest, created = Guest.objects.get_or_create(device=device)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Cart.objects.filter(guest=guest, ordered=False)
        order_item, created = LineItem.objects.get_or_create(
            item=item,
            title=item.title,
            guest=guest,
            ordered=False,
            slug=item.slug,
            price_each=item.get_final_price(),
            img=item.image.url,
        )

    order_item.quantity = 0
    order_item.save()
    order_item.delete()

    if order_qs.exists():
        order = order_qs[0]
        total_price = 0
        if order.items.filter(item__slug=item.slug).exists():
            order.items.remove(order_item)
            order.save()
        cart_sum = order.items.count()

        total_price = Cart.get_total(order)

        return JsonResponse(
            {
                "message": "Item removed from cart successfully",
                "id": item.id,
                "slug": slug,
                "quantity": order_item.quantity,
                "sum": cart_sum,
                "totalPrice": total_price,
            },
            safe=False,
        )
    return JsonResponse({"message": "something wrong if go here"}, safe=False)


# Bill checkout
class checkout_bill(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if self.request.method == "POST":
            if self.request.user.is_authenticated:
                user = self.request.user
                cart_qs = Cart.objects.filter(user=user, ordered=False)

                try:
                    # Get address before checkout
                    address = Address.objects.get(user=user, is_default=True)
                    payment_id = self.request.POST.get("order_item_id")
                    payment = Payment.objects.get(user=user, id=payment_id)

                    # order.items.add(*payment.items.all())
                    for item in payment.items.all():
                        # Create ordering Item like adding to cart
                        order_item, created = LineItem.objects.get_or_create(
                            item=item.item,
                            title=item.title,
                            user=user,
                            ordered=False,
                            slug=item.slug,
                            price_each=item.item.get_final_price(),
                            img=item.img,
                        )

                        # Create and Update cart
                        if cart_qs.exists:
                            # Each user has only one cart, so get the first one
                            cart = cart_qs.first()

                            # Check if the order item is in the cart
                            if cart.items.filter(item__slug=item.slug).exists():
                                order_item.quantity += item.quantity
                                order_item.save()
                            else:
                                order_item.quantity = item.quantity
                                order_item.save()
                                cart.items.add(order_item)
                        else:
                            ordered_date = timezone.now()
                            cart = Cart.objects.create(
                                user=request.user, ordered_date=ordered_date
                            )
                            order_item.quantity = item.quantity
                            order_item.save()
                            cart.items.add(order_item)
                            cart.save()

                    # Delete payment after click pay
                    payment.delete()

                    # Redirect to cart summary
                    cart_url = reverse("home:cart-summary")
                    return redirect(cart_url)
                except Address.DoesNotExist:
                    return redirect("home:user_profile")
            else:
                return redirect("home:login")

        else:
            return HttpResponse("Invalid request method")


# Original checkout
class checkout(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            address = request.POST.get("address")
            ward = request.POST.get("ward")
            district = request.POST.get("district")
            city = request.POST.get("city")

            try:
                cart_instance = Cart.objects.get(user=request.user)
                cart_instance.temp_address = f"{address}, {ward}, {district}, {city}"
                cart_instance.save()

                # Order handle
                order, created = Cart.objects.get_or_create(user=self.request.user)
                line_items_to_add = LineItem.objects.filter(
                    user=self.request.user, ordered=False
                )
                order.items.add(*line_items_to_add)
                default_address = Address.objects.get(
                    user=self.request.user, is_default=True
                )
                optional_addresses = Address.objects.filter(
                    user=self.request.user, is_default=False
                )

                # # Google maps

                gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                from_address = (
                    "Nam Ky Khoi Nghia Street, Hoa Phu Ward, Thu Dau Mot, Binh Duong"
                )
                to_address = f"{address} Street {ward} Ward {district} {city}"
                now = datetime.now()

                # Use geopy to get latitude and longitude
                geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
                to_address_coordinates = geolocator.geocode(to_address)

                print(to_address_coordinates.latitude)

                # Calculate distance and time
                calculate = gmaps.distance_matrix(
                    from_address, to_address, mode="driving", departure_time=now
                )

                delivery_info = f'About {calculate["rows"][0]["elements"][0]["distance"]["text"]} - Estimated delivery time {calculate["rows"][0]["elements"][0]["duration"]["text"]}'

                # Passing context
                context = {
                    "object": order,
                    "optional_addresses": optional_addresses,
                    "default_address": default_address,
                    "delivery_info": delivery_info,
                    "des_coordinates_lat": to_address_coordinates.latitude,
                    "des_coordinates_lng": to_address_coordinates.longitude,
                }

                template = "home/checkout.html"
                return render(request, template, context)
            except Cart.DoesNotExist:
                return HttpResponse("Cart instance not found.")
        else:
            return HttpResponse("Invalid request method")


# Get payment information
def get_payment_info(request):
    order_id = request.POST.get("data_id")
    if request.user.is_authenticated:
        try:
            # Try to get payment object
            payment = Payment.objects.get(user=request.user, id=order_id)

            # Get payment info
            id = payment.id
            total_price = int(payment.total)
            items = list(payment.items.values())
            order_status = payment.status

            # Return data
            return JsonResponse(
                {
                    "id": id,
                    "total_price": total_price,
                    "items": items,
                    "status": order_status,
                },
                safe=False,
            )
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment does not exist"}, status=404)
    else:
        return JsonResponse({"error": "User is not authenticated"}, status=403)


def alter_payment(request):
    if request.user.is_authenticated:
        try:
            data = json.loads(request.POST.get("data"))

            # Get id and action
            id = data.get("id")
            action = data.get("action")
            group = data.get("group")
            payment = get_object_or_404(Payment, user=request.user, id=id, paid=False)

            if action == "cancel":
                payment.delete()
                print("cancel")
                return JsonResponse(
                    {"id": id, "action": "cancel", "message": "Payment canceled"},
                    safe=False,
                )

            if action == "confirm":
                print("confirm")

            if group == "edit":
                item_id = data.get("item_id")
                if action == "delete-item":
                    blank = False
                    payment.items.remove(item_id)
                    total = payment.get_total_final_price()
                    payment.total = total
                    payment.save()
                    if total == 0:
                        blank = True
                        payment.delete()
                    print(total)
                    return JsonResponse(
                        {
                            "id": id,
                            "item_id": item_id,
                            "total": total,
                            "is_blank": blank,
                            "action": "delete-item",
                            "message": "Delete item successfully",
                        },
                        safe=False,
                    )
                if action == "plus" and not payment.paid:
                    item = LineItem.objects.get(user=request.user, id=item_id)
                    item.quantity = item.quantity + 1
                    item.save()
                    total = payment.get_total_final_price()
                    payment.total = total

                    payment.save()

                    print(total)
                    return JsonResponse(
                        {
                            "id": id,
                            "item_id": item_id,
                            "total": total,
                            "quantity": item.quantity,
                            "action": "plus",
                            "message": "Plus item successfully",
                        },
                        safe=False,
                    )
                if action == "minus" and not payment.paid:
                    blank = False
                    item = LineItem.objects.get(user=request.user, id=item_id)

                    item.quantity = item.quantity - 1
                    item.save()

                    if item.quantity == 0:
                        item.delete()
                        payment.items.remove(item_id)
                        payment.save()

                    total = payment.get_total_final_price()
                    payment.total = total

                    payment.save()

                    if total == 0:
                        payment.delete()
                        blank = True
                    return JsonResponse(
                        {
                            "id": id,
                            "item_id": item_id,
                            "total": total,
                            "is_blank": blank,
                            "quantity": item.quantity,
                            "action": "minus",
                            "message": "Minus item successfully",
                        },
                        safe=False,
                    )

            # Return data
            return JsonResponse({"message": "Success"}, safe=False)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment does not exist"}, status=404)

    else:
        return JsonResponse({"error": "User is not authenticated"}, status=403)


# Lấy hồ sơ người dùng
def get_profile_user(request):
    user = User.objects.get(username=request.user.username)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    date_of_birth = user.userprofile.date_of_birth
    formatted_date = date_of_birth.strftime("%Y-%m-%d")
    optional_addresses = Address.objects.filter(user=request.user, is_default=False)

    default_address, created = Address.objects.get_or_create(
        user=request.user, is_default=True
    )
    if default_address.city == "":
        is_blank = True
        context = {
            "optional_addresses": optional_addresses,
            "user": user,
            "date_of_birth": formatted_date,
            "cities": CITIES,
            "districts": DISTRICTS,
            "wards": WARDS,
            "is_blank": is_blank,
        }
        return render(request, "home/profile_user.html", context)
    else:
        is_blank = False
        city_id = CITIES.filter(name=default_address.city).first().id
        district_id = DISTRICTS.filter(name=default_address.district).first().id
        context = {
            "default_address": default_address,
            "optional_addresses": optional_addresses,
            "user": user,
            "date_of_birth": formatted_date,
            "cities": CITIES,
            "districts": DISTRICTS,
            "wards": WARDS,
            "city_id": city_id,
            "district_id": district_id,
            "is_blank": is_blank,
        }
        return render(request, "home/profile_user.html", context)


# Đổi mật khẩu
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        user = request.user

        if user.check_password(current_password):
            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return JsonResponse({"success": "Thay đổi mật khẩu thành công"})
        else:
            return JsonResponse({"error": "Mật khẩu cũ không đúng"})


# Lấy địa chỉ mặc định của user
def get_default_address(request):
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user, is_default=True)
            return JsonResponse(
                {
                    "street": address.street,
                    "ward": address.ward,
                    "district": address.district,
                    "city": address.city,
                },
                safe=False,
            )
        except Address.DoesNotExist:
            return JsonResponse(
                {
                    "message": "User do not have a default address",
                },
                safe=False,
            )
    else:
        return JsonResponse(
            {
                "message": "User is not authenticated",
            },
            safe=False,
        )


# Thay đổi địa chỉ mặc định
def change_default_address(request):
    if request.method == "POST":
        user = request.user
        street = request.POST.get("street")
        ward = request.POST.get("ward")
        district = request.POST.get("district")
        city = request.POST.get("city")

        default_address = Address.objects.get(user=user, is_default=True)
        default_address.street = street
        default_address.ward = ward
        default_address.district = district
        default_address.city = city
        default_address.save()
    return JsonResponse({"message": "changed default address"})


# Thay đổi hồ sơ người dùng
def change_profile_user(request):
    if request.method == "POST":
        current_user = request.user
        current_username = request.user.username

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        date_of_birth = request.POST.get("date_of_birth")

        user = User.objects.get(username=current_username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.userprofile.phone_number = phone_number
        user.userprofile.date_of_birth = date_of_birth
        user.save()
        user.userprofile.save()

        street = request.POST.get("street")
        ward = request.POST.get("ward")
        district = request.POST.get("district")
        city = request.POST.get("city")
        action = request.POST.get("action")
        optional_id = request.POST.get("optional_id")

        optional_addresses = Address.objects.filter(is_default=False, user=request.user)
        if action == "default":
            default_address = Address.objects.get(is_default=True, user=current_user)
            default_address.street = street
            default_address.ward = ward
            default_address.district = district
            default_address.city = city
            default_address.save()
        elif action == "optional":
            optional_address = Address.objects.get(
                is_default=False, user=current_user, id=optional_id
            )
            optional_address.street = street
            optional_address.ward = ward
            optional_address.district = district
            optional_address.city = city
            optional_address.save()
        else:
            if optional_addresses.count() >= 2:
                return JsonResponse({"error": "Tối đa 2 địa chỉ tùy chọn!"}, status=403)
            else:
                new_optional_address = Address(
                    user=current_user,
                    street=street,
                    ward=ward,
                    district=district,
                    city=city,
                    is_default=False,
                )
                new_optional_address.save()
        optional_data = []
        for optional_address in optional_addresses:
            optional_address = {
                "street": optional_address.street,
                "ward": optional_address.ward,
                "district": optional_address.district,
                "city": optional_address.city,
                "id": optional_address.id,
            }
            optional_data.append(optional_address)

        default_address = Address.objects.get(is_default=True, user=request.user)
        default_data = []
        data = {
            "street": default_address.street,
            "ward": default_address.ward,
            "district": default_address.district,
            "city": default_address.city,
            "id": default_address.id,
        }
        default_data.append(data)
        return JsonResponse(
            {
                "message": "changed profile",
                "optional_data": optional_data,
                "default_data": default_data,
            }
        )


# Xóa địa chỉ tùy chọn
def delete_optional_address(request):
    if request.method == "POST":
        current_user = request.user
        optional_id = request.POST.get("optional_id")
        optional_address = Address.objects.get(
            is_default=False, user=current_user, id=optional_id
        )
        optional_address.delete()

    optional_addresses = Address.objects.filter(is_default=False, user=request.user)
    data = []
    for optional_address in optional_addresses:
        optional_address = {
            "street": optional_address.street,
            "ward": optional_address.ward,
            "district": optional_address.district,
            "city": optional_address.city,
            "id": optional_address.id,
        }
        data.append(optional_address)
    return JsonResponse({"message": "changed profile", "data": data})


def get_districts(request):
    city_id = request.GET.get("city_id")
    if city_id:
        return get_location_infor(city_id)
    else:
        return JsonResponse({"error": "Invalid city_id"})


def get_wards(request):
    district_id = request.GET.get("district_id")
    if district_id:
        return get_location_infor(district_id)
    else:
        return JsonResponse({"error": "Invalid district_id"})


def get_location_infor(location_id):
    districts = DISTRICTS.filter(parent_code_id=location_id)
    items = []
    for district in districts:
        item = {
            "name": district.name,
            "id": district.id,
            "name_with_type": district.name_with_type,
        }
        items.append(item)
    return JsonResponse({"items": items})


# VNPay
# email towh.th182@gmail.com
# pass Ajax123@123

# Payment function


# Payment URL
def payment(request):
    template_name = "order-summary/"
    if request.method == "POST":
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            # order_type = form.cleaned_data['order_type']
            order_type = "other"
            order_id = form.cleaned_data["order_id"]
            amount = form.cleaned_data["amount"]
            # amount = 10000
            order_desc = form.cleaned_data["order_desc"]
            # bank_code = form.cleaned_data["bank_code"]
            bank_code = ""
            language = form.cleaned_data["language"]
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData["vnp_Version"] = "2.1.0"
            vnp.requestData["vnp_Command"] = "pay"
            vnp.requestData["vnp_TmnCode"] = settings.VNPAY_TMN_CODE
            vnp.requestData["vnp_Amount"] = amount * 100
            vnp.requestData["vnp_CurrCode"] = "VND"
            vnp.requestData["vnp_TxnRef"] = order_id
            vnp.requestData["vnp_OrderInfo"] = order_desc
            vnp.requestData["vnp_OrderType"] = order_type
            # Check language, default: vn
            if language and language != "":
                vnp.requestData["vnp_Locale"] = language
            else:
                vnp.requestData["vnp_Locale"] = "vn"
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData["vnp_BankCode"] = bank_code

            vnp.requestData["vnp_CreateDate"] = dt.now().strftime("%Y%m%d%H%M%S")
            vnp.requestData["vnp_IpAddr"] = ipaddr
            vnp.requestData["vnp_ReturnUrl"] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(
                settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY
            )
            print(vnpay_payment_url)

            # create logic condition to create placed_order
            try:
                user = User.objects.get(username=request.user.username)
                cart = Cart.objects.get(user=request.user)
                address = Address.objects.get(user=request.user, is_default=True)
            except User.DoesNotExist:
                return redirect("home:login")
            except Cart.DoesNotExist:
                return redirect("home:home")
            except Address.DoesNotExist:
                return redirect("home:user_profile")

            if cart.items.count() > 0:
                address = ""
                if cart.temp_address != "None, None, None, None":
                    address = cart.temp_address
                else:
                    address = Address.objects.get(user=user, is_default=True)

                placed_order = PlacedOrder(
                    user=user,
                    total_price=amount,
                    placed_order_at=timezone.now(),
                    address=str(address),
                )
                placed_order.save()
                placed_order.items.set(
                    LineItem.objects.filter(user=user, ordered=False)
                )
                placed_order.save()
                for item in placed_order.items.all():
                    item.ordered = True
                    item.save()

            else:
                # return reverse(template_name)
                return render(
                    request, "home/cart_summary.html", {"title": "Thanh toán"}
                )

            # wipe cart to prevent duplicate create placed_order with status 'waiting'
            cart.wipe_ordered_items()
            cart.save()

            # Redirect to VNPAY
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")

            return render(request, "home/cart_summary.html", {"title": "Thanh toán"})
    else:
        return render(request, "base.html", {"title": "Thanh toán"})


# IPN URL
def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData["vnp_TxnRef"]
        amount = inputData["vnp_Amount"]
        order_desc = inputData["vnp_OrderInfo"]
        vnp_TransactionNo = inputData["vnp_TransactionNo"]
        vnp_ResponseCode = inputData["vnp_ResponseCode"]
        vnp_TmnCode = inputData["vnp_TmnCode"]
        vnp_PayDate = inputData["vnp_PayDate"]
        vnp_BankCode = inputData["vnp_BankCode"]
        vnp_CardType = inputData["vnp_CardType"]
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalAmount = True

            # Check user exist or not
            try:
                user = User.objects.get(username=request.user.username)
            except User.DoesNotExist:
                return redirect("home:login")

            if totalAmount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == "00":
                        # placed_order model
                        placed_order = PlacedOrder.objects.get(
                            user=request.user,
                            status="waiting",
                        )
                        placed_order.status = "paid"
                        placed_order.save()

                        # payment model
                        payment = placed_order.placed_order()
                        payment.confirm_payment()
                        payment.save()

                        # cart model
                        cart = Cart.objects.get(user=request.user)
                        cart.wipe_ordered_items()
                        cart.save()

                        # delete placed_order
                        placed_order.delete()

                        print("Payment Successfully")

                    else:
                        address_payment_request(request)
                        print("Payment Error.")
                    # Return VNPAY: Merchant update success
                    result = JsonResponse(
                        {"RspCode": "00", "Message": "Confirm Success"}
                    )
                    return result
                else:
                    # Already Update
                    result = JsonResponse(
                        {"RspCode": "02", "Message": "Order Already Update"}
                    )
            else:
                # invalid amount
                result = JsonResponse({"RspCode": "04", "Message": "invalid amount"})
        else:
            # Invalid Signature
            result = JsonResponse({"RspCode": "97", "Message": "Invalid Signature"})
    else:
        result = JsonResponse({"RspCode": "99", "Message": "Invalid request"})

    # address_payment_request after all
    address_payment_request(request)

    return result


# ReturnURL
def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData["vnp_TxnRef"]
        amount = int(inputData["vnp_Amount"]) / 100
        order_desc = inputData["vnp_OrderInfo"]
        vnp_TransactionNo = inputData["vnp_TransactionNo"]
        vnp_ResponseCode = inputData["vnp_ResponseCode"]
        vnp_TmnCode = inputData["vnp_TmnCode"]
        vnp_PayDate = inputData["vnp_PayDate"]
        vnp_BankCode = inputData["vnp_BankCode"]
        vnp_CardType = inputData["vnp_CardType"]
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                payment_ipn(request)
                return render(
                    request,
                    "home/payment_return.html",
                    {
                        "title": "Payment Result",
                        "result": "Successful",
                        "order_id": order_id,
                        "amount": amount,
                        "order_desc": order_desc,
                        "vnp_TransactionNo": vnp_TransactionNo,
                        "vnp_ResponseCode": vnp_ResponseCode,
                    },
                )
            else:
                payment_ipn(request)
                return render(
                    request,
                    "home/payment_return.html",
                    {
                        "title": "Payment Result",
                        "result": "Fail",
                        "order_id": order_id,
                        "amount": amount,
                        "order_desc": order_desc,
                        "vnp_TransactionNo": vnp_TransactionNo,
                        "vnp_ResponseCode": vnp_ResponseCode,
                    },
                )
        else:
            payment_ipn(request)
            return render(
                request,
                "home/payment_return.html",
                {
                    "title": "Payment Result",
                    "result": "Fail",
                    "order_id": order_id,
                    "amount": amount,
                    "order_desc": order_desc,
                    "vnp_TransactionNo": vnp_TransactionNo,
                    "vnp_ResponseCode": vnp_ResponseCode,
                    "msg": "Sai checksum",
                },
            )
    else:
        payment_ipn(request)
        return render(
            request,
            "home/payment_return.html",
            {"title": "Payment Result", "result": ""},
        )


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# reload order summary to prevent duplicate create placed_order with status 'waiting'
def reload_order_summary(request):
    try:
        username = request.user.username
        user = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        return redirect("home:login")
    try:
        address_payment_request(request)

    except PlacedOrder.DoesNotExist:
        print("no order waiting")
        pass


# address payment request
def address_payment_request(request):
    # placed_order model
    placed_orders = PlacedOrder.objects.filter(user=request.user, status="waiting")

    for placed_order in placed_orders:
        placed_order.status = "pending"
        placed_order.save()

    # payment model
    for placed_order in placed_orders:
        payment = placed_order.placed_order()
        payment.save()

    # delete placed_order
    for placed_order in placed_orders:
        placed_order.delete()

    # bill model
    bills = PlacedOrder.objects.filter(user=request.user, status="temp")

    # delete placed_order
    for bill in bills:
        bills.delete()

    # delete zero cost payment
    payments = Payment.objects.filter(user=request.user, total=0)
    for payment in payments:
        payment.delete()


######## END PAYMENT ########


def sort_cart(request):
    if request.method == "GET":
        sort = request.GET.get("sort")

        # Sort list cart
        cart = Cart.objects.get(user=request.user)
        items = cart.items.filter(user=request.user, ordered=False)
        sorted_items = sorted(items, key=lambda x: x.get_final_price())

        for item in sorted_items:
            print(item.get_final_price())

        # Apply sort condition
        if sort == "true":  # ascending
            cart.items.clear()
            for item in sorted_items:
                cart.items.add(item)
        else:  # descending
            cart.items.clear()
            for item in reversed(sorted_items):
                cart.items.add(item)

        for item in cart.items.all():
            print(item.get_final_price())

        cart.save()
        print("ok")
    return JsonResponse({"message": "sorted cart"})


class ItemDetailView(DetailView):
    model = Item
    template_name = "home/detail.html"


def get_chart_data():
    category_counts = Item.objects.values("category").annotate(total=Count("category"))
    payment_counts = Payment.objects.values("status").annotate(total=Count("status"))

    paid_orders = Payment.objects.filter(paid=True)
    revenue_data = paid_orders.values("order_placed_at__date").annotate(
        total_revenue=Sum("total")
    )

    labels = []
    revenue_values = []

    for entry in revenue_data:
        labels.append(entry["order_placed_at__date"].strftime("%Y-%m-%d"))
        revenue_values.append(entry["total_revenue"])

    total_today_payments = Payment.objects.filter(
        order_placed_at__date=date.today()
    ).aggregate(Sum("total"))["total__sum"]
    today_payments = Payment.objects.filter(order_placed_at__date=date.today()).count()
    context = {
        "category_counts": category_counts,
        "payment_counts": payment_counts,
        "labels": labels,
        "revenue_values": revenue_values,
        "total_today_payments": total_today_payments,
        "today_payments": today_payments,
    }
    return context


def dashboard(request):
    context = get_chart_data()
    return render(request, "home/dashboard.html", context)


def chart(request):
    context = get_chart_data()
    return render(request, "home/chart.html", context)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def api_items(request):
    list_items = Item.objects.all()
    serializer = ItemSerializer(list_items, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def api_get_item(request, slug):
    try:
        item = Item.objects.get(slug=slug)
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["DELETE"])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def api_delete_item(request, slug):
    try:
        item = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def api_add_item(request):
    if request.method == "POST":
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def api_update_item(request, slug):
    try:
        item = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = ItemSerializer(item, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSuperuser])
def auth(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def api_today_payments(request):
    today = date.today()
    today_payments = Payment.objects.filter(order_placed_at__date=today)
    serializer = PaymentSerializer(today_payments, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def api_get_order(request, id):
    try:
        order = Payment.objects.get(id=id)
        serializer = PaymentSerializer(order)
        return Response(serializer.data)
    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def api_customers(request):
    list_customers = User.objects.all()
    serializer = UserSerializer(list_customers, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def api_customer_detail(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=404)

    orders = Payment.objects.filter(user=user, status='paid')
    orders_serializer = PaymentSerializer(orders, many=True)
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum("total"))["total"] or 0

    user_serializer = UserSerializer(user)
    order_summary_serializer = OrderSummarySerializer(
        {
            "total_orders": total_orders,
            "total_spent": total_spent,
        }
    )

    response_data = {
        'user': user_serializer.data,
        'order_summary': order_summary_serializer.data,
    }
    return Response(response_data)

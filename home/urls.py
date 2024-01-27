from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import *

app_name = "home"

urlpatterns = [

    path("", home, name="home"),
    path("menu/", menu, name="menu"),
    path("about/", about, name="about"),
    path("book-table/", book_table, name="book-table"),
    path("logout/", logoutPage, name="logout"),
    path("login/", register_login, name="login"),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/chart/', chart, name='chart'),

    # url ajax
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    path("cart-summary/", summary_cartView.as_view(), name="cart-summary"),
    path("load-items-data-view/", load_items_data_view, name="load-items-data-view"),
    path("update-item/", update_item, name="update-item"),
    path("remove-from-cart/", remove_from_cart, name="remove-from-cart"),
    path("categories/", categories, name="categories"),
    path("search-item/", search_item, name="search-item"),
    path("cart-summary/sort-cart/", sort_cart, name="sort-cart"),
    path("filter-billing/", billingView.as_view(), name="filter-billing"),
    path("filter-billing/get-payment-info/", get_payment_info, name="get-payment-info"),
    path("filter-billing/alter-payment/", alter_payment, name="alter_payment"),
    path("get-default-address/", get_default_address, name="get-default-address"),
    path("change-default-address/", change_default_address, name="change-default-address"),
    path("change-profile-user/", change_profile_user, name="change-profile-user"),
    path("delete-optional-address/", delete_optional_address, name="delete-optional-address"),

    # profile user
    path("user/profile/", get_profile_user, name="get-profile-user"),
    # Change password
    path("change-password/", change_password, name="change-password"),
    # payment
    path("checkout/", checkout.as_view(), name="checkout"),
    path("checkout-bill/", checkout_bill.as_view(), name="checkout-bill"),
    # url payment
    path("payment/", payment, name="payment"),
    path("payment_return/", payment_return, name="payment_return"),
    # Reset Password
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="home/reset_password.html",
            success_url=reverse_lazy("home:password_reset_done"),
        ),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="home/reset_password_sent.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="home/password_reset_confirm.html",
            success_url=reverse_lazy("home:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="home/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # Get district
    path("get_districts/", get_districts, name="get_district"),
    path("get_wards/", get_wards, name="get_wards"),

    # API
    path("api/items/", api_items, name="items"),
    path('api/items/<slug:slug>/', api_get_item, name='get_item'),
    path('api/items/delete/<slug:slug>/', api_delete_item, name='delete_item'),
    path("api/add_item/", api_add_item, name="add_item"),
    path('api/update_item/<slug:slug>/', api_update_item, name='update_item'),
    path("auth/", auth, name="auth"),
    path("api/orders/", api_today_payments, name="today_payments"),
    path('api/orders/<int:id>/', api_get_order, name='get_order'),
    path("api/customers/", api_customers, name="customers"),
    path("api/customers/<int:user_id>", api_customer_detail, name="customer_detail"),

]

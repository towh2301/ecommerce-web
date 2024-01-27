from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User, AbstractUser

CATEGORY_CHOICES = (
    ("Burger", "Burger"),
    ("Pizza", "Pizza"),
    ("Pasta", "Pasta"),
    ("Fries", "Fries"),
)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    ward = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street}, {self.ward}, {self.district}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(id=self.id).update(
                is_default=False
            )
        super(Address, self).save(*args, **kwargs)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=10)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField()
    discount = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("home:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("home:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("home:remove-from-cart", kwargs={"slug": self.slug})

    def get_final_price(self):
        return int(self.price - self.price * (self.discount / 100))


class LineItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey("Guest", on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    slug = models.SlugField(null=True, blank=True)
    price_each = models.FloatField(null=True, blank=True)
    img = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return int(self.quantity * self.item.price)

    def get_total_discount_item_price(self):
        return int(self.quantity * self.item.get_final_price())

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        return self.get_total_item_price() - self.get_amount_saved()
    
    def get_name(self):
        return self.item.title


class PlacedOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(LineItem)
    status = models.CharField(max_length=255, default="waiting")
    total_price = models.IntegerField(null=True, blank=True)
    placed_order_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"

    # def placed_order(self):
    #     return self.items.count()

    def get_total_final_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def placed_order(self):
        payment = Payment.objects.create(
            user=self.user,
            order_id=self,
            total=self.get_total(),
            address=self.address,
        )
        payment.items.set(self.items.all())
        return payment


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.ForeignKey(PlacedOrder, on_delete=models.SET_NULL, null=True)
    paid = models.BooleanField(default=False)
    total = models.FloatField(null=True, blank=True)
    items = models.ManyToManyField(LineItem)
    address = models.CharField(max_length=255, null=True, blank=True)
    order_placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default="pending")

    def __str__(self) -> str:
        return super().__str__()

    def confirm_payment(self):
        self.paid = True
        self.status = "paid"

        items = LineItem.objects.filter(user=self.user, ordered=False)

        for item in items:
            item.ordered = True
            item.save()
        self.save()
        return self.status

    def get_payment_details(self):
        return self.order_id.items.all()
    
    def get_total_final_price(self):
        total_money = 0
        for item in self.items.all():
            total_money += item.get_final_price()
        return total_money


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey("Guest", on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(LineItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    temp_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username}"
        else:
            return f"{self.guest.device}"

    def get_products(self):
        return self.items.count()

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        # if self.coupon:
        #     total -= self.coupon.amount
        return total

    def get_total_final_price(self):
        total_money = self.get_total()
        return total_money

    def create_order(self):
        order = PlacedOrder.objects.create(user=self.user)
        for item in self.items.all():
            order.items.add(item)
        order.save()
        return order

    def wipe_ordered_items(self):
        self.items.all().update(ordered=True)
        self.items.clear()
        self.save()
        return self


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, blank=True, null=True, default="")
    date_of_birth = models.DateField(default="1900-01-01")

    def __str__(self):
        return f"Profile {self.user.username}"


class Guest(models.Model):
    device = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.device}"
    
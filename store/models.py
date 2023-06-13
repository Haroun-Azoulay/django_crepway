from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
import pytz



class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    price = models.FloatField(default=0.0)
    stock = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="products", blank=True, null=True)


    def __str__(self):
        return f"{self.name} ({self.stock})"

    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})
    


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)
    total_price = models.FloatField(default=0.0)

    @property
    def ordered_date_utc(self):
        if self.ordered_date:
            paris_tz = pytz.timezone('Europe/Paris')
            return timezone.localtime(self.ordered_date).astimezone(paris_tz)
        return None

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity  
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order)
    


    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        self.orders.all().delete()
        super().delete(*args, **kwargs)

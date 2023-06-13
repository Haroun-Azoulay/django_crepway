from django.contrib import admin
from django.urls import path
from store.views import index, product_detail, add_to_cart, cart, delete_cart, menu, payment, checkout, payment_confirm
from crepway import settings
from django.conf.urls.static import static
from accounts.views import signup, logout_user, login_user, password_reset, password_reset_done, password_reset_complete
from mail.views import mail
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
urlpatterns = [
    path('', index, name='index'),
    path("admin/", admin.site.urls),
    path("signup/", signup, name="signup"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("cart/", cart, name="cart"),
    path("payment/", payment, name="payment"),
    path("payment_confirm/", payment_confirm, name="payment_confirm"),
    path("menu/", menu, name="menu"),
    path("cart/delete/", delete_cart, name="delete-cart"),
    path("product/<str:slug>/", product_detail, name="product"),
    path("product/<str:slug>/add-to-cart/", add_to_cart, name="add-to-cart"),
    path("mail/", mail, name="mail"),
    path("checkout/", checkout, name="checkout"),
    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', password_reset_complete, name='password_reset_complete'),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEFAULT_FILE_STORAGE == 'storages.backends.dropbox.DropBoxStorage':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

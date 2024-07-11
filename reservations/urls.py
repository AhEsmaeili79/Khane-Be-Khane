from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    admin_panel,admin_houses_list,admin_users_list, admin_orders_list,admin_add_admin, house_list,admin_delete_user, admin_delete_house, admin_delete_order,toggle_house_status,toggle_user_status,
    home, signup, login_view,cancel_order, logout_view, host_reservations, user_info, host_houses, house_create,user_orders, HouseDetailView, HouseUpdateView, HouseDeleteView, order_house, search, host_requests
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user_info/', user_info, name='user_info'),
    path('houses/', house_list, name='house_list'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house_detail'),
    path('houses/new/', house_create, name='house_create'),
    path('houses/<int:pk>/edit/', HouseUpdateView.as_view(), name='house_update'),
    path('houses/<int:pk>/delete/', HouseDeleteView.as_view(), name='house_delete'),
    path('houses/<int:pk>/order/', order_house, name='order_house'),
    path('search/', search, name='search'),
    path('host-houses/', host_houses, name='host_houses'),
    path('management/host_requests/', host_requests, name='host_requests'),
    path('user/orders/', user_orders, name='user_orders'),
    path('cancel_order/<int:pk>/', cancel_order, name='cancel_order'),
    path('host_reservations/', host_reservations, name='host_reservations'),
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('management/users/', admin_users_list, name='admin_users_list'),
    path('management/houses/', admin_houses_list, name='admin_houses_list'),
    path('management/orders/', admin_orders_list, name='admin_orders_list'),
    path('management/add_admin/', admin_add_admin, name='admin_add_admin'),
    path('management/users/delete/<int:user_id>/', admin_delete_user, name='admin_delete_user'),
    path('management/houses/delete/<int:house_id>/', admin_delete_house, name='admin_delete_house'),
    path('management/orders/delete/<int:order_id>/', admin_delete_order, name='admin_delete_order'),
    path('management/users/toggle/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('management/houses/toggle/<int:house_id>/', toggle_house_status, name='toggle_house_status'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
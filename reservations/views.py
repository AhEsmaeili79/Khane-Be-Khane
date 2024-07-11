from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User, House, Order, Review
from .forms import SignUpForm, UserInfoForm, HouseForm, ReviewForm, OrderForm 

def home(request):
    houses = House.objects.all()
    return render(request, 'reservations/home.html', {'houses': houses})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 3  
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'ثبت نام با موفقیت انجام شد.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'reservations/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')

    return render(request, 'reservations/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def user_info(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserInfoForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'اطلاعات کاربری شما با موفقیت تغییر یافت.')
                return redirect('user_info')
        elif 'request_role_change' in request.POST:
            request.user.role_change_requested = True
            request.user.save()
            messages.success(request, 'درخواست میزبانی شما با موفقیت ارسال گردید.')
            return redirect('user_info')
    else:
        user_form = UserInfoForm(instance=request.user)
    
    return render(request, 'reservations/user_info.html', {
        'user_form': user_form,
    })


def house_list(request):
    houses = House.objects.all()

    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            houses = houses.filter(price_per_day__lte=price)

    if 'location' in request.GET:
        location = request.GET['location']
        if location:
            houses = houses.filter(city__icontains=location)

    sort_by = request.GET.get('sort_by', '-id') 
    if sort_by not in ['name', 'city', 'price_per_day', 'number_of_rooms', 'area']:
        sort_by = '-id'  

    houses = houses.order_by(sort_by)

    context = {
        'houses': houses,
    }
    return render(request, 'reservations/house_list.html', context)

class HouseDetailView(DetailView):
    model = House
    template_name = 'reservations/house_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        house = self.get_object()
        reviews = Review.objects.filter(house=house)
        context['reviews'] = reviews
        if self.request.user.is_authenticated:
            user_review = Review.objects.filter(house=house, user=self.request.user).first()
            context['form'] = ReviewForm(instance=user_review) if user_review else ReviewForm()
        else:
            context['form'] = None
        return context

    def post(self, request, *args, **kwargs):
        house = self.get_object()
        user_review = Review.objects.filter(house=house, user=request.user).first()
        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.house = house
            review.user = request.user
            review.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد.')
        else:
            messages.error(request, 'خطا در ثبت نظر.')
        return redirect('house_detail', pk=house.pk)

class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    template_name = 'reservations/house_form.html'
    success_url = reverse_lazy('house_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def house_create(request):
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.user = request.user
            house.save()
            return redirect('host_houses')
    else:
        form = HouseForm()
    return render(request, 'reservations/house_form.html', {'form': form})

class HouseUpdateView(LoginRequiredMixin, UpdateView):
    model = House
    form_class = HouseForm
    template_name = 'reservations/house_form.html'
    success_url = reverse_lazy('house_list')

    def get_queryset(self):
        return House.objects.filter(user=self.request.user)

class HouseDeleteView(LoginRequiredMixin, DeleteView):
    model = House
    template_name = 'reservations/house_confirm_delete.html'
    success_url = reverse_lazy('house_list')

    def get_queryset(self):
        return House.objects.filter(user=self.request.user)



@login_required
def order_house(request, pk):
    house = get_object_or_404(House, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.house = house
            
            existing_orders = Order.objects.filter(
                house=house,
                exit_date__gte=order.arrive_date,
                arrive_date__lte=order.exit_date
            )
            
            if existing_orders.exists():
                messages.error(request, 'در این تاریخ رزرو دیگری انجام شده است.')
                return redirect('house_detail', pk=pk)
            
            order.total_price = house.price_per_day * (order.exit_date - order.arrive_date).days
            order.save()
            messages.success(request, 'رزرو خانه با موفقیت انجام شد.')
            return redirect('house_detail', pk=pk)  
    else:
        form = OrderForm()
    return render(request, 'reservations/order_form.html', {'form': form, 'house': house})

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    houses = House.objects.all()
    if request.method == 'POST':
        order.delete()
        return redirect('user_orders')
    return render(request, 'reservations/confirm_cancel_order.html', {'order': order,'houses': houses})

def search(request):
    query = request.GET.get('q')
    if query:
        houses = House.objects.filter(name__icontains=query)
    else:
        houses = House.objects.all()
    return render(request, 'reservations/search_results.html', {'houses': houses, 'query': query})

@user_passes_test(lambda u: u.role == 1)  
def host_requests(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)
        if action == 'approve':
            user.role = 2
        user.role_change_requested = False
        user.save()
        return redirect('host_requests')

    users_requesting_role_change = User.objects.filter(role_change_requested=True)
    return render(request, 'reservations/host_requests.html', {'users': users_requesting_role_change})


def host_houses(request):
    if request.user.is_authenticated and request.user.role == 2:
        host_houses = House.objects.filter(user=request.user)
        return render(request, 'reservations/host_houses.html', {'host_houses': host_houses})
    else:
        return render(request, 'reservations/access_denied.html')  
    
@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'reservations/user_orders.html', {'orders': orders})


@login_required
def host_reservations(request):
    if request.user.role != 2: 
        return redirect('home')
    houses = House.objects.filter(user=request.user)
    reservations = Order.objects.filter(house__in=houses)
    return render(request, 'reservations/host_reservations.html', {'reservations': reservations})



@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('home')  

    return render(request, 'reservations/admin_panel.html')

@login_required
def admin_users_list(request):
    if not request.user.is_superuser:
        return redirect('home')  

    users = User.objects.all()
    return render(request, 'reservations/admin_users_list.html', {'users': users})

@login_required
def admin_houses_list(request):
    if not request.user.is_superuser:
        return redirect('home')  

    houses = House.objects.all()
    return render(request, 'reservations/admin_houses_list.html', {'houses': houses})

@login_required
def admin_add_house(request):
    if not request.user.is_superuser:
        return redirect('home')  

    # Handle adding house form submission
    return render(request, 'reservations/admin_add_house.html')

@login_required
def admin_orders_list(request):
    if not request.user.is_superuser:
        return redirect('home')  

    orders = Order.objects.all()
    return render(request, 'reservations/admin_orders_list.html', {'orders': orders})

@login_required
def admin_add_admin(request):
    if not request.user.is_superuser:
        return redirect('home')  

    if request.method == 'POST':
        new_admin_username = request.POST.get('new_admin_username')
        try:
            new_admin = User.objects.get(username=new_admin_username)
            new_admin.is_staff = True
            new_admin.save()
            messages.success(request, 'کاربر به عنوان مدیر افزوده شد.')
        except User.DoesNotExist:
            messages.error(request, 'کاربری با این نام کاربری وجود ندارد.')

    return redirect('admin_panel')

def admin_required(user):
    return user.is_authenticated and user.role == 1

@user_passes_test(admin_required)
def admin_users_list(request):
    users = User.objects.all()
    return render(request, 'reservations/admin_users_list.html', {'users': users})

@user_passes_test(admin_required)
def admin_houses_list(request):
    houses = House.objects.all()
    return render(request, 'reservations/admin_houses_list.html', {'houses': houses})

@user_passes_test(admin_required)
def admin_orders_list(request):
    orders = Order.objects.all()
    return render(request, 'reservations/admin_orders_list.html', {'orders': orders})

@user_passes_test(admin_required)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'کاربر با موفقیت حذف شد.')
    return redirect('admin_users_list')

@user_passes_test(admin_required)
def admin_delete_house(request, house_id):
    house = get_object_or_404(House, id=house_id)
    house.delete()
    messages.success(request, 'خانه با موفقیت حذف شد.')
    return redirect('admin_houses_list')

@user_passes_test(admin_required)
def admin_delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, 'سفارش با موفقیت حذف شد.')
    return redirect('admin_orders_list')

@user_passes_test(admin_required)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'کاربر {"فعال" if user.is_active else "غیرفعال"} شد.')
    return redirect('admin_users_list')

@user_passes_test(admin_required)
def toggle_house_status(request, house_id):
    house = get_object_or_404(House, pk=house_id)
    house.is_active = not house.is_active
    house.save()
    messages.success(request, f'خانه {"فعال" if house.is_active else "غیرفعال"} شد.')
    return redirect('admin_houses_list')
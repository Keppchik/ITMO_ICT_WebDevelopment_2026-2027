from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.views import View
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date, timedelta
from django.db.models import Q
from django.core.paginator import Paginator

from .forms import CustomUserCreationForm, ProfileUpdateForm, ReservationForm, ReviewForm
from .models import Hotel, RoomType, Reservation, Stay, Review

# Create your views here.
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

def homeView(request):
    hotels = Hotel.objects.all().order_by('name')

    query = request.GET.get('q', '').strip()
    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(address__icontains=query) |
            Q(description__icontains=query)
        )

    selected_city = request.GET.get('city', '').strip()
    if selected_city:
        hotels = hotels.filter(city__iexact=selected_city)

    selected_stars = request.GET.get('stars', '').strip()
    if selected_stars in ('1', '2', '3', '4', '5'):
        hotels = hotels.filter(stars=int(selected_stars))
    else:
        selected_stars = ''

    paginator = Paginator(hotels, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = []
    if query:
        params.append(f'q={query}')
    if selected_city:
        params.append(f'city={selected_city}')
    if selected_stars:
        params.append(f'stars={selected_stars}')
    query_string = ('&' + '&'.join(params)) if params else ''

    cities = Hotel.objects.values_list('city', flat=True).distinct().order_by('city')

    return render(request, 'homeView.html', {
        'page_obj': page_obj,
        'cities': cities,
        'selected_city': selected_city,
        'selected_stars': selected_stars,
        'query': query,
        'query_string': query_string,
    })


def searchView(request):
    query = request.GET.get('q', '')
    if query:
        return redirect(f'/?q={query}')
    return redirect('home')

def hotelDetailView(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    reviews = Review.objects.filter(stay__room__room_type__hotel=hotel).select_related('author', 'stay').order_by('-created_at')

    return render(request, 'hotelDetailView.html', { 'hotel': hotel, 'reviews': reviews, })

@login_required
def profileView(request):
    user = request.user
    return render(request, 'profileView.html', {'profile_user': user})

@login_required
def profileEditView(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные профиля обновлены.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profileEditView.html', {'form': form, 'user': user})

@login_required
def roomTypeBookView(request, room_type_id):
    room_type = get_object_or_404(RoomType, pk=room_type_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, room_type=room_type)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            busy_room_ids = Reservation.objects.filter(
                room__room_type=room_type,
                status__in=['pending', 'confirmed', 'checked_in'],
                date_from__lt=date_to,
                date_to__gt=date_from,
            ).values_list('room_id', flat=True)

            free_room = room_type.room_set.filter(
                is_available=True
            ).exclude(pk__in=busy_room_ids).first()

            if not free_room:
                form.add_error(None, 'На выбранные даты нет свободных номеров этого типа.')
            else:
                reservation = form.save(commit=False)
                reservation.guest = request.user
                reservation.room = free_room
                reservation.status = 'pending'
                reservation.save()
                messages.success(request, 'Бронирование создано и ожидает подтверждения.')
                return redirect('my_reservations')
    else:
        form = ReservationForm(room_type=room_type)

    return render(request, 'room_book.html', {
        'room_type': room_type,
        'hotel': room_type.hotel,
        'form': form,
    })


@login_required
def myReservationsView(request):
    reservations = Reservation.objects.filter(guest=request.user).select_related('room__room_type__hotel').order_by('-created_at')
    return render(request, 'my_reservations.html', {'reservations': reservations})


@login_required
def reservationCancelView(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, guest=request.user)
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Бронирование отменено.')
    return redirect('my_reservations')


@login_required
def reviewCreateView(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)

    stays = Stay.objects.filter(
        guest=request.user,
        room__room_type__hotel=hotel,
        checked_out_at__isnull=False,
    ).select_related('room__room_type').order_by('-checked_out_at')

    if not stays.exists():
        messages.error(request, 'Вы можете оставить отзыв только после проживания в этом отеле.')
        return redirect('hotel_detail', hotel_id=hotel.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user, hotel=hotel)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('hotel_detail', hotel_id=hotel.pk)
    else:
        form = ReviewForm(user=request.user, hotel=hotel)

    return render(request, 'review_form.html', {
        'hotel': hotel,
        'form': form,
    })

@staff_member_required
def allReservationsView(request):
    reservations = Reservation.objects.all().order_by('-created_at')
    return render(request, 'all_reservations.html', {'reservations': reservations})


@staff_member_required
@require_POST
def reservationSetStatusView(request, pk, new_status):
    ALLOWED_TRANSITIONS = {
        'pending': {'confirmed', 'cancelled'},
        'confirmed': {'checked_in', 'cancelled'},
        'checked_in': {'checked_out'},
    }

    reservation = get_object_or_404(Reservation, pk=pk)
    current = reservation.status

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if new_status not in allowed:
        messages.error(request, f'Нельзя перевести бронь из «{current}» в «{new_status}».')
        return redirect('all_reservations')

    reservation.status = new_status
    reservation.save()

    messages.success(
        request,
        f'Бронь #{reservation.pk}: статус изменён на «{reservation.get_status_display()}».'
    )
    return redirect('all_reservations')


@login_required
def reservationEditView(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, guest=request.user)

    if reservation.status not in ('pending', 'confirmed'):
        messages.error(request, 'Эту бронь нельзя изменить — она уже заселёна, выселена или отменена.')
        return redirect('my_reservations')

    room_type = reservation.room.room_type

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation, room_type=room_type)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            busy_room_ids = Reservation.objects.filter(
                room__room_type=room_type,
                status__in=['pending', 'confirmed', 'checked_in'],
                date_from__lt=date_to,
                date_to__gt=date_from,
            ).exclude(pk=reservation.pk).values_list('room_id', flat=True)

            if reservation.room_id in busy_room_ids:
                free_room = room_type.room_set.filter(
                    is_available=True
                ).exclude(pk__in=busy_room_ids).first()
            else:
                free_room = reservation.room

            if not free_room:
                form.add_error(None, 'На выбранные даты нет свободных номеров этого типа.')
            else:
                updated = form.save(commit=False)
                updated.room = free_room
                updated.save()
                messages.success(request, 'Бронирование обновлено.')
                return redirect('my_reservations')
    else:
        form = ReservationForm(instance=reservation, room_type=room_type)

    return render(request, 'room_book.html', {
        'room_type': room_type,
        'hotel': room_type.hotel,
        'form': form,
        'reservation': reservation,
        'is_edit': True,
    })

@login_required
@require_POST
def reviewDeleteView(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if review.author != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете удалить чужой отзыв.')
        return redirect('hotel_detail', hotel_id=review.stay.room.room_type.hotel.pk)

    hotel_id = review.stay.room.room_type.hotel.pk if review.stay else None
    review.delete()
    messages.success(request, 'Отзыв удалён.')

    if hotel_id:
        return redirect('hotel_detail', hotel_id=hotel_id)
    return redirect('home')

@staff_member_required
def monthlyGuestsView(request):
    today = date.today()
    month_ago = today - timedelta(days=30)

    stays = Stay.objects.filter(
        checked_in_at__date__lte=today,
    ).filter(
        Q(checked_out_at__isnull=True) | Q(checked_out_at__date__gte=month_ago)
    ).select_related(
        'guest', 'room__room_type__hotel'
    ).order_by('-checked_in_at')

    return render(request, 'monthly_guests.html', {
        'stays': stays,
        'today': today,
        'month_ago': month_ago,
    })
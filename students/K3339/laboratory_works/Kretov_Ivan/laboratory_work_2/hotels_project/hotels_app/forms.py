from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.utils import timezone

from .models import Reservation, Review, Stay


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'phone', 'birthday', 'passport_number', 'nationality', 'address')

        widgets = { 'birthday': forms.DateInput(attrs={'type': 'date'}), }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'phone', 'birthday', 'passport_number', 'nationality', 'address')
        widgets = { 'birthday': forms.DateInput(attrs={'type': 'date'}), }

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = get_user_model().objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('date_from', 'date_to', 'guests_count', 'comments')
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'date_to':   forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'guests_count': forms.NumberInput(attrs={'min': 1, 'class': 'form-input'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-input', 'placeholder': 'Пожелания (необязательно)'}),
        }

    def __init__(self, *args, room_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_type = room_type
        if room_type:
            self.fields['guests_count'].widget.attrs['max'] = room_type.capacity
            self.fields['guests_count'].initial = 1

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        guests = cleaned.get('guests_count')

        if date_from and date_from < timezone.localdate():
            self.add_error('date_from', 'Дата заезда не может быть в прошлом.')

        if date_from and date_to and date_to <= date_from:
            self.add_error('date_to', 'Дата выезда должна быть позже даты заезда.')

        if self.room_type and guests and guests > self.room_type.capacity:
            self.add_error('guests_count',
                           f'Максимум {self.room_type.capacity} гостей для этого номера.')

        return cleaned

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Оценка (1–10)',
    )

    class Meta:
        model = Review
        fields = ('stay', 'text', 'rating')
        widgets = {
            'stay': forms.Select(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-input',
                'placeholder': 'Расскажите о проживании...',
            }),
        }

    def __init__(self, *args, user=None, hotel=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and hotel:
            self.fields['stay'].queryset = Stay.objects.filter(
                guest=user,
                room__room_type__hotel=hotel,
                checked_out_at__isnull=False,
            ).exclude(
                review__isnull=False
            ).select_related('room__room_type').order_by('-checked_out_at')

            self.fields['stay'].label_from_instance = (
                lambda s: f"{s.room.room_type.name} №{s.room.number}: "
                          f"{s.checked_in_at:%d.%m.%Y} — {s.checked_out_at:%d.%m.%Y}"
            )

            qs = self.fields['stay'].queryset
            if qs.count() == 1:
                self.fields['stay'].initial = qs.first()
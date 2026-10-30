from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView

from .forms import CarOwnerForm
from .models import DriverLicense, Ownership, Car

# Create your views here.
def owner_detail(request, owner_id):
    owner = get_object_or_404(get_user_model(), pk=owner_id)
    license = DriverLicense.objects.filter(id_carOwner=owner).first()
    ownerships = Ownership.objects.filter(id_carOwner=owner).select_related('id_car')
    return render(request, 'owner.html', {
        'owner': owner,
        'license': license,
        'ownerships': ownerships,
    })

def owner_list(request):
    owners = get_user_model().objects.filter(is_superuser=False)

    return render(request, 'owner_list.html', {'owners': owners})

def create_owner(request):
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerForm()
    return render(request, 'create_owner.html', {'form': form})


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'

class CarUpdateView(UpdateView):
    model = Car
    template_name = 'car_edit.html'
    fields = ['gos_number', 'brand', 'model', 'color']
    success_url = '/car/list/'

class CarCreateView(CreateView):
    model = Car
    template_name = 'create_car.html'
    fields = ['gos_number', 'brand', 'model', 'color']
    success_url = '/car/list/'

class CarDeleteView(DeleteView):
    model = Car
    template_name = 'delete_car.html'
    success_url = '/car/list/'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from usuarios.forms import RegistroUserForm
from reservas.forms import TrainingReservationForm
from reservas.models import TrainingReservation
from .google_calender import GoogleCalendarManager
import datetime as dt
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def index(request):
    return render(request,'index/index.html',{
    })

def logout_view(request):
    logout(request)
    return redirect('index')

def auth(request):
    if request.method == 'POST':
        if 'register_submit' in request.POST:
            form = RegistroUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data['username']
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            else:
                context = {'form': form}
                return render(request, 'auth/auth.html', context)
        elif 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
                else:
                    return render(request, 'auth/auth.html', {'login_form': login_form, 'show_login': True})
            else:
                return render(request, 'auth/auth.html', {'login_form': login_form, 'show_login': True})
    else:
        registro_form = RegistroUserForm()
        login_form = AuthenticationForm()
        context = {'form': registro_form, 'login_form': login_form}
        return render(request, 'auth/auth.html', context)

@login_required(login_url='auth')
def home(request):
    return render(request,'home/home.html',{
    })

@login_required(login_url='auth')
def reserve_done(request):
    return render(request, 'reserve/reserve_done.html',{
    })

@login_required(login_url='auth')
def reserve(request):
    calendar = GoogleCalendarManager()
    try:
        # Obtiene la fecha de la URL
        selected_date_str = request.GET.get('date', dt.date.today().isoformat())
        selected_date = dt.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = dt.date.today()

    # Llama a la función para obtener los horarios disponibles
    available_slots = calendar.get_available_slots(selected_date)

    if request.method == 'POST':
        # Valida los horarios de esa fecha
        form = TrainingReservationForm(request.POST, available_slots=available_slots)
        if form.is_valid():
            nueva_reserva = form.save(commit=False)
            nueva_reserva.user = request.user
            nueva_reserva.save()
            form.save_m2m()

            # Crea el evento en Google Calendar
            start_time = dt.datetime.combine(nueva_reserva.date, nueva_reserva.time)
            start_time_aware = timezone.make_aware(start_time)
            end_time_aware = start_time_aware + dt.timedelta(hours=1)

            if nueva_reserva.training_type:
                summary = f"Entrenamiento de {nueva_reserva.training_type.name}"
            else:
                summary = "Entrenamiento sin especificar"

            description = f"Reserva para: {request.user.username}"

            created_event = calendar.create_event(
                summary,
                start_time_aware,
                end_time_aware,
                attendees=[request.user.email] if request.user.email else [],
                description=description
            )

            if created_event:
                nueva_reserva.google_event_id = created_event.get('id')
                nueva_reserva.save()

            #Función para mandar el correo
                context = {
                    'user': nueva_reserva.user,
                    'reserva': nueva_reserva,
                }

                html_message = render_to_string('emails/email.html', context)

                subject = 'Confirmación de tu Reserva de Entrenamiento'
                from_email = 'belalcazartrainer@gmail.com'
                to_email = [nueva_reserva.user.email]

                email = EmailMessage(subject, html_message, from_email, to_email)
                email.content_subtype = "html"
                email.send()
            return redirect('reserve_done')
    else:
        # Al cargar la página, muestra el formulario con los horarios disponibles
        form = TrainingReservationForm(
            initial={'date': selected_date},
            available_slots=available_slots
        )

    return render(request, 'reserve/reserve.html', {'form': form, 'selected_date': selected_date.isoformat()})

@login_required(login_url='auth')
def view_reservations(request):
    reservas_del_usuario = TrainingReservation.objects.filter(user=request.user, completed=False).prefetch_related('training_type').order_by('date', 'time')
    contexto = {
        'reservas': reservas_del_usuario
    }
    return render(request, 'reserve/view_reservations.html', contexto)

@login_required(login_url='auth')
def delete_reservation(request, reservation_id):

    reserva = get_object_or_404(TrainingReservation, id=reservation_id, user=request.user)

    if request.method == 'POST':

        if reserva.google_event_id:
            try:
                calendar = GoogleCalendarManager()
                calendar.delete_event(reserva.google_event_id)
                print(f"Evento {reserva.google_event_id} ha sido borrado de Google Calendar.")
            except Exception as e:
                print(f"Error al borrar evento de Google Calendar: {e}")

        reserva.delete()
        return redirect('view_reservations')

    return redirect ('view_reservations')

@login_required(login_url='auth')
def edit_reservation(request, reservation_id):
    reserva = get_object_or_404(TrainingReservation, id=reservation_id, user=request.user)
    calendar = GoogleCalendarManager()

    if request.method == 'POST':
        date_str = request.POST.get('date')
        selected_date = dt.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else reserva.date
        available_slots = calendar.get_available_slots(selected_date)
        form = TrainingReservationForm(request.POST, instance=reserva, available_slots=available_slots)

        if form.is_valid():
            updated_reserva = form.save()

            if updated_reserva.google_event_id:
                try:
                    start_time = dt.datetime.combine(updated_reserva.date, updated_reserva.time)
                    start_time_aware = timezone.make_aware(start_time)
                    end_time_aware = start_time_aware + dt.timedelta(hours=1)
                    summary = f"Entrenamiento de {updated_reserva.training_type.name}" if updated_reserva.training_type else "Entrenamiento sin especificar"

                    calendar.update_event(
                        event_id=updated_reserva.google_event_id,
                        summary=summary,
                        start_time=start_time_aware,
                        end_time=end_time_aware
                    )
                except Exception as e:
                    print(f"Error al actualizar el evento en Google Calendar: {e}")

            return redirect('edit_reservation_done')
        else:
            print("El formulario de edición no es válido. Errores:")
            print(form.errors)
    else:
        date_str = request.GET.get('date', reserva.date.isoformat())
        try:
            selected_date = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = reserva.date

        available_slots = calendar.get_available_slots(selected_date)

        form = TrainingReservationForm(
            instance=reserva,
            initial={'date': selected_date},
            available_slots=available_slots
        )

    return render(request, 'reserve/edit_reservation.html', {
        'form': form,
        'reserva': reserva,
        'selected_date': selected_date.isoformat()
    })

@login_required(login_url='auth')
def edit_reservation_done (request):
    return render(request, 'reserve/edit_reservation_done.html',{
    })
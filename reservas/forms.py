from django import forms
from .models import TrainingReservation

class TrainingReservationForm(forms.ModelForm):
    class Meta:
        model = TrainingReservation
        fields = ['date', 'time', 'location', 'training_type', 'phone', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        available_slots = kwargs.pop('available_slots', [])

        super().__init__(*args, **kwargs)

        if available_slots:
            self.fields['time'].widget = forms.Select(choices=available_slots)

        else:
            self.fields['time'].widget = forms.Select(choices=[('', 'No hay horas disponibles')])
            self.fields['time'].disabled = True

        self.fields['notes'].required = False

        self.fields['location'].widget.attrs.update({'placeholder': 'Dirección o parque'})
        self.fields['phone'].widget.attrs.update({'placeholder': '3001234567'})
        self.fields['notes'].widget.attrs.update({'rows': 1, 'placeholder': '¿Alguna lesión o condición?'})
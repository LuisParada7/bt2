from django.contrib import admin
from .models import TrainingType, TrainingReservation
from import_export.admin import ImportExportModelAdmin


@admin.register(TrainingType)
class TrainingTypeAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name', 'description')
    ordering = ['name']

@admin.register(TrainingReservation)
class TrainingReservationAdmin(ImportExportModelAdmin):
    list_display = ('user', 'date', 'time', 'location', 'display_training_type', 'phone', 'notes', 'completed',)
    list_filter = ('date', 'completed', 'user', 'training_type',)
    search_fields = ('user__username', 'user__email', 'location', 'training_type__name')
    ordering = ['-date', '-time']

    def display_training_type(self, obj):
        """
        Muestra el nombre del TrainingType asociado.
        """
        if obj.training_type:
            return obj.training_type.name
        return "Sin asignar"

    display_training_type.short_description = "Tipo de Entrenamiento"

    fieldsets = (
        (None, {
            'fields': ('user', 'date', 'time', 'location')
        }),
        ('Detalles del Entrenamiento', {
            'fields': ('training_type', 'phone', 'notes')
        }),
        ('Estado', {
            'fields': ('completed',)
        }),
    )
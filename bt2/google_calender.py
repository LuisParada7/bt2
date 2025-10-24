# google_calendar.py

import os.path
import datetime as dt
from django.utils import timezone
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Permisos
SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarManager:
    """
    Una clase para gestionar las interacciones con la API de Google Calendar.
    """

    def __init__(self, credentials_path='client_secret_app_escritorio_oauth.json', token_path='token.json'):
        """
        Inicializa el servicio de Google Calendar.

        Args:
            credentials_path (str): La ruta al archivo de credenciales de la API.
            token_path (str): La ruta al archivo de token de usuario.
        """
        self.service = self._authenticate(credentials_path, token_path)

    def _authenticate(self, credentials_path, token_path):
        """
        Autentica con la API de Google Calendar usando OAuth 2.0.
        Detecta si es Vercel (Producción) para usar variables de entorno.
        """
        creds = None
        IS_PROD = os.getenv('VERCEL') == '1'

        if IS_PROD:
            token_json_string = os.getenv('GOOGLE_TOKEN_JSON')
            if token_json_string:
                token_info = json.loads(token_json_string)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)

        elif os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if IS_PROD:
                    raise Exception(
                        "Autenticación fallida en Vercel. El token guardado es inválido o no existe. "
                        "Actualiza la variable GOOGLE_TOKEN_JSON con un nuevo token generado localmente."
                    )
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                    with open(token_path, "w") as token:
                        token.write(creds.to_json())

        if not creds or not creds.valid:
             raise Exception("Fallo la autenticación de Google Calendar. Verifica credenciales/token.")

        return build("calendar", "v3", credentials=creds)

    def get_available_slots(self, date, duration_minutes=60):
        """
        Usa la lista de eventos para encontrar y devolver los horarios disponibles.
        """
        # Define el rango de trabajo para el día.
        start_of_day = timezone.make_aware(dt.datetime.combine(date, dt.time(8, 0)))
        end_of_day = timezone.make_aware(dt.datetime.combine(date, dt.time(20, 0)))

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True
            ).execute()
            busy_events = events_result.get('items', [])
        except Exception as e:
            print(f"Error al conectar con Google Calendar: {e}")
            return []

        # Compara los horarios posibles con los horarios ocupados.
        available_slots = []
        current_time = start_of_day

        while current_time < end_of_day:
            is_available = True
            slot_end_time = current_time + dt.timedelta(minutes=duration_minutes)

            for event in busy_events:
                if 'dateTime' not in event.get('start', {}):
                    continue

                event_start = dt.datetime.fromisoformat(event['start']['dateTime'])
                event_end = dt.datetime.fromisoformat(event['end']['dateTime'])

                # Si el horario choca con un evento ocupado, no está disponible.
                if max(current_time, event_start) < min(slot_end_time, event_end):
                    is_available = False
                    break

            if is_available:
                local_time = timezone.localtime(current_time)
                available_slots.append((local_time.time(), local_time.strftime("%H:%M")))

            current_time += dt.timedelta(minutes=duration_minutes)

        return available_slots


    def create_event(self, summary, start_time, end_time, attendees=None, description=''):
        """
        Crea un nuevo evento en el calendario.

        Args:
            summary (str): El título del evento.
            start_time (datetime.datetime): La fecha y hora de inicio del evento.
            end_time (datetime.datetime): La fecha y hora de fin del evento.
            attendees (list): Una lista de correos electrónicos de los asistentes.
            description (str): La descripción del evento.

        Returns:
            El evento creado o None si hubo un error.
        """
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Bogota',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Bogota',
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        try:
            created_event = self.service.events().insert(calendarId="primary", body=event).execute()
            print(f"Evento creado: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as error:
            print(f"Ocurrió un error: {error}")
            return None

    def update_event(self, event_id, summary=None, start_time=None, end_time=None):
    # Obtenemos el evento existente de Google para modificarlo.
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

        if summary:
           event['summary'] = summary

        if start_time:
        # Usamos .isoformat() para conservar la zona horaria.
           event['start']['dateTime'] = start_time.isoformat()

        if end_time:
           event['end']['dateTime'] = end_time.isoformat()

    # Enviamos el objeto 'event' modificado de vuelta a Google.
        updated_event = self.service.events().update(
            calendarId='primary', eventId=event_id, body=event).execute()

        print(f"Evento {event_id} actualizado en Google Calendar.")
        return updated_event

    def delete_event(self, event_id):
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
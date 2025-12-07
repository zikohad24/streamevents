from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from datetime import timedelta


class Command(BaseCommand):
    help = 'Actualitza els estats dels esdeveniments automàticament'

    def handle(self, *args, **options):
        now = timezone.now()
        updated_count = 0

        # Esdeveniments programats que han de començar
        scheduled_to_live = Event.objects.filter(
            status='scheduled',
            scheduled_date__lte=now
        )

        for event in scheduled_to_live:
            event.status = 'live'
            event.save()
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Esdeveniment "{event.title}" passat a EN DIRECTE')
            )

        # Esdeveniments en directe que han de finalitzar
        live_events = Event.objects.filter(status='live')
        for event in live_events:
            end_time = event.scheduled_date + timedelta(minutes=event.get_duration())
            if now >= end_time:
                event.status = 'finished'
                event.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Esdeveniment "{event.title}" FINALITZAT')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Actualitzats {updated_count} esdeveniments')
        )
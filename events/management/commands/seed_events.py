from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from events.models import Event
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea esdeveniments de prova per a la base de dades'

    def handle(self, *args, **options):
        users = User.objects.all()
        if not users:
            self.stdout.write(
                self.style.ERROR('No hi ha usuaris a la base de dades. Executa primer seed_users.')
            )
            return

        events_data = [
            {
                'title': 'Marató de Gaming: Fortnite Tournament',
                'description': 'Torneig de Fortnite amb premis increïbles! Uneix-te a la competició més esperada de l\'any. Competeix amb els millors jugadors i guanya premis exclusius.',
                'category': 'gaming',
                'max_viewers': 500,
                'is_featured': True,
                'tags': 'gaming,fortnite,tournament,esports',
                'stream_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title': 'Concert Acústic: Música Indie',
                'description': 'Sessió acústica amb les millors bandes indie del moment. No et perdis aquesta experiència única de música en viu amb artistes emergents.',
                'category': 'music',
                'max_viewers': 200,
                'is_featured': True,
                'tags': 'music,indie,acoustic,live',
                'stream_url': 'https://www.twitch.tv/musiclive'
            },
            {
                'title': 'Xerrada sobre Intel·ligència Artificial',
                'description': 'Descobreix els últims avenços en IA i com estan transformant la societat. Experts del sector compartiran les seves experiències.',
                'category': 'technology',
                'max_viewers': 300,
                'is_featured': False,
                'tags': 'technology,ai,inteligencia artificial,xerrada',
                'stream_url': 'https://www.youtube.com/watch?v=abcdefghijk'
            },
            {
                'title': 'Tutorial de Programació Python',
                'description': 'Aprèn Python des de zero amb aquest tutorial complet. Perfecte per a principiants que volen iniciar-se en la programació.',
                'category': 'education',
                'max_viewers': 150,
                'is_featured': False,
                'tags': 'education,python,programming,tutorial',
                'stream_url': 'https://www.youtube.com/watch?v=python123'
            },
            {
                'title': 'Directe de Art Digital',
                'description': 'Sessió de creació d\'art digital en directe. Observa com es crea una peça d\'art des de zero amb eines digitals.',
                'category': 'art',
                'max_viewers': 100,
                'is_featured': False,
                'tags': 'art,digital,creativity,live',
                'stream_url': 'https://www.twitch.tv/artdigital'
            },
            {
                'title': 'Partit de Lliga de Videojocs',
                'description': 'Segueix en directe aquest emocionant partit de la lliga professional de videojocs. Els millors equips es enfrenten.',
                'category': 'gaming',
                'max_viewers': 1000,
                'is_featured': True,
                'tags': 'gaming,esports,competition,live',
                'stream_url': 'https://www.twitch.tv/esports'
            },
            {
                'title': 'Debat sobre Canvi Climàtic',
                'description': 'Debat entre experts sobre les solucions al canvi climàtic. Una conversa necessària per al futur del planeta.',
                'category': 'talk',
                'max_viewers': 250,
                'is_featured': False,
                'tags': 'talk,climate,environment,debat',
                'stream_url': 'https://www.youtube.com/watch?v=climate123'
            },
            {
                'title': 'Sessió de Yoga en Directe',
                'description': 'Classe de yoga per a tots els nivells. Connecta amb el teu cos i ment en aquesta sessió relaxant.',
                'category': 'sports',
                'max_viewers': 80,
                'is_featured': False,
                'tags': 'sports,yoga,wellness,health',
                'stream_url': 'https://www.youtube.com/watch?v=yoga456'
            },
            {
                'title': 'Festival de Música Electrónica',
                'description': 'Festival virtual de música electrónica amb els millors DJs internacionals. Una experiència sonora única.',
                'category': 'music',
                'max_viewers': 5000,
                'is_featured': True,
                'tags': 'music,electronic,festival,dj',
                'stream_url': 'https://www.youtube.com/watch?v=electronic789'
            },
            {
                'title': 'Taller d\'Emprenedoria',
                'description': 'Aprèn a crear el teu propi negoci amb aquest taller pràctic. Experts en emprenedoria compartiran els seus consells.',
                'category': 'education',
                'max_viewers': 200,
                'is_featured': False,
                'tags': 'education,entrepreneurship,business,workshop',
                'stream_url': 'https://www.youtube.com/watch?v=business456'
            }
        ]

        created_count = 0

        for i, event_data in enumerate(events_data):
            days_ago = random.randint(0, 30)
            hours_from_now = random.randint(1, 48)

            scheduled_date = timezone.now() - timedelta(days=days_ago) + timedelta(hours=hours_from_now)

            # Assignar estat basat en la data
            if scheduled_date < timezone.now():
                status = random.choice(['live', 'finished'])
            else:
                status = 'scheduled'

            event = Event.objects.create(
                title=event_data['title'],
                description=event_data['description'],
                creator=random.choice(users),
                category=event_data['category'],
                scheduled_date=scheduled_date,
                status=status,
                max_viewers=event_data['max_viewers'],
                is_featured=event_data.get('is_featured', False),
                tags=event_data['tags'],
                stream_url=event_data['stream_url']
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Creat esdeveniment: {event.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'S\'han creat {created_count} esdeveniments de prova')
        )
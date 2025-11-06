from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from faker import Faker
import unicodedata

User = get_user_model()

class Command(BaseCommand):
    """🌱 Genera usuaris i grups de prova per a StreamEvents."""
    help = "🌱 Genera usuaris de prova"

    def add_arguments(self, parser):
        # Arguments opcionals
        parser.add_argument("--users", type=int, default=10, help="Nombre d'usuaris a crear")
        parser.add_argument("--clear", action="store_true", help="Elimina usuaris existents")

    @transaction.atomic
    def handle(self, *args, **options):
        num_users = options["users"]
        clear = options["clear"]
        fake = Faker("es_ES")

        # 🧹 Elimina usuaris si cal
        if clear:
            deleted = User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING(f"🗑️ Eliminats {deleted[0]} usuaris."))

        # 👥 Crear grups
        groups = {}
        for name in ["Organitzadors", "Participants", "Moderadors"]:
            group, _ = Group.objects.get_or_create(name=name)
            groups[name] = group
        self.stdout.write(self.style.SUCCESS("✅ Grups assegurats."))

        # 👑 Crear admin
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@streamevents.com",
                "first_name": "Admin",
                "last_name": "Sistema",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            admin.groups.add(groups["Organitzadors"])
            self.stdout.write(self.style.SUCCESS("👑 Superusuari creat."))

        # 👨‍💻 Crear usuaris de prova
        for i in range(num_users):
            first = fake.first_name()
            last = fake.last_name()
            username = self.clean_username(f"{first.lower()}.{last.lower()}{i+1}")
            email = f"{username}@streamevents.com"

            if (i + 1) % 5 == 0:
                group = groups["Organitzadors"]
                display = f"🎯 {first} {last}"
            elif (i + 1) % 3 == 0:
                group = groups["Moderadors"]
                display = f"🛡 {first} {last}"
            else:
                group = groups["Participants"]
                display = f"{first} {last}"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "is_active": True,
                    "display_name": display,
                    "bio": f"Usuari de prova: {display}",
                },
            )

            if created:
                user.set_password("password123")
                user.save()
                user.groups.add(group)
                self.stdout.write(f"✅ {username} → {group.name}")

        self.stdout.write(self.style.SUCCESS(f"🎉 {num_users} usuaris creats!"))

    def clean_username(self, username):
        """
        Elimina accents dels usernames.

        >>> cmd = Command()
        >>> cmd.clean_username('josé.garcía')
        'jose.garcia'
        >>> cmd.clean_username('iñaki.lópez')
        'inaki.lopez'
        """
        return ''.join(
            c for c in unicodedata.normalize('NFD', username)
            if unicodedata.category(c) != 'Mn'
        )

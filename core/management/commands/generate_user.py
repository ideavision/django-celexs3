from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Generating fake user by running python manage.py generate_user"

    def handle(self, *args, **kwargs):
        for i in range(0, 500):
            User.objects.create_user(
                name="name_%s" % i,
                email="name_%s@email.com" % i,
                phone="phone_%s_123" % i,
                is_superuser=bool(i % 2 == 0),
                is_staff=bool(i % 2 != 0)
            )
            print("Insrting item %s" % i)

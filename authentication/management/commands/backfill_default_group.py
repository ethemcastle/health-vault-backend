from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from authentication.const import PATIENT

class Command(BaseCommand):
    help = "Assign Patient group to users missing group"

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            patient = Group.objects.get(name=PATIENT)
        except Group.DoesNotExist:
            self.stderr.write("Patient group not found. Run migrations first.")
            return
        qs = User.objects.filter(group__isnull=True)
        updated = 0
        for u in qs:
            u.group = patient
            u.save(update_fields=["group"])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} users."))

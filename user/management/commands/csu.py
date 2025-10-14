from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from user.models import User


class Command(BaseCommand):
    help = "Добавление суперюзера"

    def handle(self, *args, **options):
        # managers_group, created = Group.objects.get_or_create(name="Manager")
        # if created:
        #     permissions = Permission.objects.filter(
        #         codename__in=["add_mailing", "change_mailing", "can_block_user", "view_mailing", "view_client", "view_user",]
        #     )
        #     managers_group.permissions.set(permissions)

        super_user = User.objects.create(
            email="admin@admin.com",
            first_name="Admin",
            last_name="Adminexin",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        super_user.set_password("1234qwer")
        super_user.save()
        self.stdout.write(self.style.SUCCESS("✅ Суперпользователь успешно создан!"))

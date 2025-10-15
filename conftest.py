import pytest
import django
import os


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


@pytest.fixture(scope="session")
def django_db_setup():
    """Настройка БД для тестов"""
    from django.test.utils import setup_databases, teardown_databases
    from django.conf import settings

    setup_databases(verbosity=1, interactive=False)
    yield
    teardown_databases(settings.DATABASES, verbosity=1)

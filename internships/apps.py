from django.apps import AppConfig

class InternshipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'internships'

    def ready(self):
        import internships.wagtail_hooks  # Ensure wagtail_hooks.py is loaded

from django.apps import AppConfig


class PolizasConfig(AppConfig):
    name = 'polizas'

    def ready(self):
        import polizas.signals

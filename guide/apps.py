from django.apps import AppConfig


class GuideConfig(AppConfig):
    name = 'guide'

    def ready(self):
        import guide.signals

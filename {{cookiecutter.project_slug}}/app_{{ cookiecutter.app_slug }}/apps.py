from django.apps import AppConfig


class App{{ cookiecutter.app_config_slug }}Config(AppConfig):
    name = '{{ cookiecutter.app_slug}}'

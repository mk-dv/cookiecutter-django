import os
import random
import shutil
import string
from dynaconf import loaders

try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    print('Sysrandom not used.')

TERMINATOR = "\x1b[0m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

CONFIG_PATH = 'settings.toml'
SECRETS_PATH = '.secrets.toml'

DEBUG_VALUE = "debug"


def remove_pycharm_files():
    idea_dir_path = ".idea"
    if os.path.exists(idea_dir_path):
        shutil.rmtree(idea_dir_path)


def append_to_project_gitignore(path):
    gitignore_file_path = ".gitignore"
    with open(gitignore_file_path, "a") as gitignore_file:
        gitignore_file.write(path)
        gitignore_file.write(os.linesep)


def generate_random_string(
    length, using_digits=True, using_ascii_letters=True, using_punctuation=False
):
    """
    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        return None

    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', "\\", "$"}
        suitable = all_punctuation.difference(unsuitable)
        symbols += "".join(suitable)
    return "".join([random.choice(symbols) for _ in range(length)])


def append_to_gitignore_file(s):
    with open(".gitignore", "a") as gitignore_file:
        gitignore_file.write(s)
        gitignore_file.write(os.linesep)


def set_flags_in_toml(path, flags, environement='develop'):
    loaders.toml_loader.write(path, {environement: flags}, merge=True)


def set_flags_in_config(**flags, environement='develop'):
    set_flags_in_toml(CONFIG_PATH, flags, environement)


def set_flags_in_secrets(**secrets):
    set_flags_in_toml(SECRETS_PATH, secrets, environement='develop')


def main():
    if "{{ cookiecutter.use_pycharm }}".lower() == "n":
        remove_pycharm_files()

    if "{{ cookiecutter.keep_config_in_git }}".lower() == "n":
        append_to_gitignore_file(CONFIG_PATH)

    if "{{ cookiecutter.use_postgresql }}".lower() == "y":
        # TODO(mk-dv): Add values check.
        postgresql_database_name = input(
            'Database name [{{ cookiecutter.project_slug }}]:'
        )
        postgresql_user_name = input('PostgreSQL username [postgres]:')
        postgresql_user_password = input(
            'PostgreSQL password[generate password]:'
        )

        if not postgresql_user_name:
            postgresql_user_name = 'postgres'

        if not postgresql_user_password:
            postgresql_user_password = generate_random_string(length=10)


        set_flags_in_config(
            POSTGRESQL_DATABASE_NAME=postgresql_database_name,
            POSTGRESQL_USER_NAME=postgresql_user_name,
            POSTGRESQL_USER_PASSWORD=postgresql_user_password,
            environement='develop'
        )

        secret_key = generate_random_string(length=64)

        set_flags_in_secrets(
            SECRET_KEY=secret_key,
            environement='develop'
        )

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()

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
    using_sysrandom = False

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

DEBUG_VALUE = "debug"


def remove_pycharm_files():
    idea_dir_path = ".idea"
    if os.path.exists(idea_dir_path):
        shutil.rmtree(idea_dir_path)

    docs_dir_path = os.path.join("docs", "pycharm")
    if os.path.exists(docs_dir_path):
        shutil.rmtree(docs_dir_path)






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


def set_flag(file_path, flag, value=None, formatted=None, *args, **kwargs):
    if value is None:
        random_string = generate_random_string(*args, **kwargs)
        if random_string is None:
            print(
                "We couldn't find a secure pseudo-random number generator on your system. "
                "Please, make sure to manually {} later.".format(flag)
            )
            random_string = flag
        if formatted is not None:
            random_string = formatted.format(random_string)
        value = random_string

    with open(file_path, "r+") as f:
        file_contents = f.read().replace(flag, value)
        f.seek(0)
        f.write(file_contents)
        f.truncate()

    return value



def set_django_secret_key(file_path):
    django_secret_key = set_flag(
        file_path,
        "!!!SET DJANGO_SECRET_KEY!!!",
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_secret_key



def set_django_admin_url(file_path):
    django_admin_url = set_flag(
        file_path,
        "!!!SET DJANGO_ADMIN_URL!!!",
        formatted="{}/",
        length=32,
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_admin_url


def generate_random_user():
    return generate_random_string(length=32, using_ascii_letters=True)




def set_postgres_user(file_path, value):
    postgres_user = set_flag(file_path, "!!!SET POSTGRES_USER!!!", value=value)
    return postgres_user


def set_postgres_password(file_path, value=None):
    postgres_password = set_flag(
        file_path,
        "!!!SET POSTGRES_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return postgres_password




def append_to_gitignore_file(s):
    with open(".gitignore", "a") as gitignore_file:
        gitignore_file.write(s)
        gitignore_file.write(os.linesep)


def set_flags_in_toml(path):
    loaders.toml_loader.write('settings.toml', {'default': dict(asd='new_val')}, merge=True)


# TODO(mk-dv): Формируем словарь, передаем его в set_flags.
def set_flags_in_config(**flags):
    set_flags_in_toml(CONFIG_PATH, flags)

def set_flags_in_secrets(**secrets):
    set_flags_in_toml(SECRETS_PATH, secrets)
    # set_django_secret_key(production_django_envs_path)
    # set_django_admin_url(production_django_envs_path)
    #
    # set_postgres_user(local_postgres_envs_path, value=postgres_user)
    # set_postgres_password(
    #     local_postgres_envs_path, value=DEBUG_VALUE if debug else None
    # )
    # set_postgres_user(production_postgres_envs_path, value=postgres_user)
    # set_postgres_password(
    #     production_postgres_envs_path, value=DEBUG_VALUE if debug else None
    # )


# def set_flags_in_settings_files():
#     set_django_secret_key(os.path.join("config", "settings", "local.py"))
#     set_django_secret_key(os.path.join("config", "settings", "test.py"))


def main():
    debug = ('{{ cookiecutter.debug }}'.lower() == 'y')
    if "{{ cookiecutter.use_pycharm }}".lower() == "n":
        remove_pycharm_files()


    append_to_gitignore_file("production.env")
    if "{{ cookiecutter.keep_develop_env_in_vcs }}".lower() == "n":
        append_to_gitignore_file("develop.env")

    if "{{ cookiecutter.use_postgresql }}".lower() == "y":
        # TODO(mk-dv): Add values check.
        postgresql_database_name = input(
            'Database name [{{ cookiecutter.project_slug }}]:'
        )
        postgresql_user_name = input('PostgreSQL username [postgres]:')
        if not postgresql_user_name:
            postgresql_user_name = 'postgres'

        postgresql_user_password = input(
            'PostgreSQL password[generate password]:'
        )
        if not postgresql_user_password:
            postgresql_user_password = generate_random_string(length=10)


        set_flags_in_envs(
            POSTGRESQL_DATABASE_NAME=postgresql_database_name,
            POSTGRESQL_USER_NAME=postgresql_user_name,
            POSTGRESQL_USER_PASSWORD=postgresql_user_password,
            debug=debug,
        )
        secret_key = generate_random_string(length=64)
        set_secrets(SECRET_KEY=secret_key)
    # TODO(mk-dv): This gettings flags from env?
    set_flags_in_settings_files()




    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()

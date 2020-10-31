from django.shortcuts import render


# TODO(mk-dv): Write view.
def app_base_index(request):
    return render(
        request,
        '{{ cookiecutter.project_slug }}/templates/pages/home.html',
        {}
    )

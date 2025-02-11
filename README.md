# dsd-digitalocean

A plugin for deploying Django projects to Digital Ocean, using django-simple-deploy.

Quick Start
---

To deploy your project to Digital Ocean, you'll need to ...

## Prerequisites

Deployment to Digital Ocean requires the following:

- You must be using Git to track your project.
- You need to be tracking your dependencies with a `requirements.txt` file, or be using Poetry or Pipenv.
- You'll need...

## Configuration-only deployment

First, install `dsd-digitalocean` and add `django_simple_deploy` to `INSTALLED_APPS` in *settings.py*:

```sh
$ pip install dsd-digitalocean
# Add "django_simple_deploy" to INSTALLED_APPS in settings.py.
$ git commit -am "Added django_simple_deploy to INSTALLED_APPS."
```

When you install `dsd-digitalocean`, it will install `django-simple-deploy` as a dependency.

Now run the `deploy` command:

```sh
$ python manage.py deploy
```

This is the `deploy` command from `django-simple-deploy`, which makes all the changes you need to run your project on Digital Ocean.

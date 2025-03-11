# dsd-vps

A plugin for deploying Django projects to any VPS provider, using django-simple-deploy.

Quick Start
---

To deploy your project to a VPS, you'll need to ...

## Prerequisites

Deployment to a VPS requires the following:

- You must be using Git to track your project.
- You need to be tracking your dependencies with a `requirements.txt` file, or be using Poetry or Pipenv.
- You'll need...

## Configuration-only deployment (NOT SUPPORTED YET)

First, install `dsd-vps` and add `django_simple_deploy` to `INSTALLED_APPS` in *settings.py*:

```sh
$ pip install dsd-vps
# Add "django_simple_deploy" to INSTALLED_APPS in settings.py.
$ git commit -am "Added django_simple_deploy to INSTALLED_APPS."
```

When you install `dsd-vps`, it will install `django-simple-deploy` as a dependency.

Now run the `deploy` command:

```sh
$ python manage.py deploy
```

This is the `deploy` command from `django-simple-deploy`, which makes all the changes you need to run your project on a VPS.

## Automated deployment

This is experimental, and you should review the codebase before running this early version on your system. It will modify local files outside of your project, such as `~/.ssh/config` and `~/.ssh/id_rsa_git`.

- Create a new VPS instance.
    - I'm Using Ubuntu 24.04 on Digital Ocean for development work; any debian-based OS on any VPS provider should work.
    - Choose SSH username/password login approach.
- Set two env vars:
    - `$ export DSD_HOST_IPADDR=<droplet-ip-address>`
    - `$ export DSD_HOST_PW=<droplet-pw>`
- Install `dsd-vps`.
    - This will be changed to `dsd-vps` shortly, as it should work for all VPS hosting platforms.
    - This plugin is not yet available on PyPI; I'm currently using an editable install of the repo.
- Add `django_simple_deploy` to `INSTALLED_APPS`.
- Run `python manage.py deploy --automate-all`.

The `deploy` command will add a new user named `django_user` to the droplet, with the same password you originally chose. It will update and configure the server, configure Git on the server, configure the project to be served from the droplet, commit changes, push the project, and open the remote project in a new browser tab.

It will add a local ssh key pair for Git, modifying `~/.ssh/config`. The key will be stored at `~/.ssh/id_rsa_git`.

The project will be served over http, which means the browser will probably flag it as insecure.

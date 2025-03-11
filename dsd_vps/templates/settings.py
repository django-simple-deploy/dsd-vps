{{current_settings}}

# VPS settings.
import os

if os.environ.get("ON_DIGITALOCEAN"):
    # from https://whitenoise.evans.io/en/stable/#quickstart-for-django-apps
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATIC_URL = "/static/"
    # try:
    #     STATICFILES_DIRS.append(os.path.join(BASE_DIR, "static"))
    # except NameError:
    #     STATICFILES_DIRS = [
    #         os.path.join(BASE_DIR, "static"),
    #     ]

    # i = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    # MIDDLEWARE.insert(i + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

    # Use secret, if set, to update DEBUG value.
    if os.environ.get("DEBUG") == "TRUE":
        DEBUG = True
    else:
        DEBUG = False

    # Set a platform-specific allowed host.
    ALLOWED_HOSTS.append("*")#"{{ deployed_project_name }}.fly.dev")

    # Prevent CSRF "Origin checking failed" issue.
    # CSRF_TRUSTED_ORIGINS = ["https://{{ deployed_project_name }}.fly.dev"]

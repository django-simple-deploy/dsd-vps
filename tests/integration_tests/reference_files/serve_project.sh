# Start serving project after receiving code.

# Build a venv.
cd /home/django_user/blog
/home/django_user/.local/bin/uv venv .venv
source .venv/bin/activate
/home/django_user/.local/bin/uv pip install -r requirements.txt

# # Set env vars.
export DEBUG=TRUE
export ON_DIGITALOCEAN=1

# Migrate, and run collectstatic.
/home/django_user/blog/.venv/bin/python manage.py migrate
/home/django_user/blog/.venv/bin/python manage.py collectstatic --noinput

# Serve project. Reload service files, start gunicorn, start caddy.
# The logic here allows this script to be run after services have been 
# started. This is especially helpful during development work.
sudo /usr/bin/systemctl daemon-reload

sudo /usr/bin/systemctl enable gunicorn.socket
if systemctl is-active --quiet gunicorn.socket; then
    sudo /usr/bin/systemctl restart gunicorn.socket
else
    sudo /usr/bin/systemctl start gunicorn.socket
fi

sudo /usr/bin/systemctl enable caddy
if systemctl is-active --quiet caddy; then
    sudo /usr/bin/systemctl restart caddy
else
    sudo /usr/bin/systemctl start caddy
fi

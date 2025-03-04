# Start serving project after receiving code.

# Build a venv.
cd {{ project_path }}
{{ uv_path }} venv .venv
source .venv/bin/activate
{{ uv_path }} pip install -r requirements.txt

# # Set env vars.
export DEBUG=TRUE
export ON_DIGITALOCEAN=1

# Migrate, and run collectstatic.
{{ project_path }}/.venv/bin/python manage.py migrate
{{ project_path }}/.venv/bin/python manage.py collectstatic --noinput

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

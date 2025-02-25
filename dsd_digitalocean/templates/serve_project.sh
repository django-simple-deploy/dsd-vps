# Start serving project after receiving code.

# Build a venv.
cd {{ project_path }}
{{ uv_path }} venv .venv
source .venv/bin/activate
{{ uv_path }} pip install -r requirements.txt

# Set env vars.
export DEBUG=FALSE
export ON_DIGITALOCEAN=1

# Migrate, and run collectstatic.
{{ project_path }}/.venv/bin/python manage.py migrate
{{ project_path }}/.venv/bin/python manage.py collectstatic --noinput

# Serve project.
# nohup {{ project_path }}/.venv/bin/gunicorn --bind 0.0.0.0:8000 blog.wsgi > gunicorn.log f2>&1

sudo /usr/bin/systemctl start gunicorn.socket
sudo /usr/bin/systemctl enable gunicorn.socket

# Start serving project after receiving code.

cd {{ project_path }}
{{ uv_path }} venv .venv
source .venv/bin/activate
{{ uv_path }} pip install -r requirements.txt

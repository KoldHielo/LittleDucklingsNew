command = '/home/ubuntu/webdev/venv/bin/gunicorn'
pythonpath = '/home/ubuntu/webdev/littleducklings'
bind = '127.0.0.1:8046'
workers = 1
certfile='/etc/letsencrypt/live/littleducklingschildminding.co.uk/fullchain.pem'
keyfile='/etc/letsencrypt/live/littleducklingschildminding.co.uk/privkey.pem'

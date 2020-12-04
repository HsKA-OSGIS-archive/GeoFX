# GeoFX: Geofencing web maps for everyone!
Brought to you by GeofencingX

## Installation
Pre-requisites: access to a terminal, Python 3.X, a Postgres DB, Geoserver running at port 8080
Tested on Lubuntu based on Ubuntu 18.04.5 (OSGeo-Live)
```bash
sudo apt-get install python3-venv
# Create a virtual environment for the Python application
python3 -m venv env
# Activate the virtual environment
source env/bin/activate
# Install dependencies
pip install Django psycopg2-binary djangorestframework
# Create a database for the application
# Enter postgres console to create a database and user
psql
```

```SQL
CREATE DATABASE geofx;
# Create user (make sure to set your own password)
CREATE USER geofx_user WITH ENCRYPTED PASSWORD '<your_password>';
GRANT ALL PRIVILEGES ON DATABASE geofx to geofx_user;
# exit pqsl
\q
```

Now open the settings file located at

src/geofx/geofx/settings.py

and update the password with the one you assigned in postgres (approximately in line 85)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geofx',
        'USER': 'geofx_user',
        'PASSWORD': '<your_password>',
        'HOST': 'localhost',
        'PORT': 5432
    }
}
```

```bash
# Now we setup nginx so that both the django app and geoserver
# will be proxied via localhost:80. This assumes that your geoserver
# instance is up and runnin on port 8080 !
sudo apt-get install nginx
sudo rm /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-available/default
# Copy the nginx configuration file (make sure you execute this
# from the root folder of this repository)
sudo cp config/geofx /etc/nginx/sites-available/geofx
# Symlink
sudo ln -s /etc/nginx/sites-available/geofx /etc/nginx/sites-enabled/geofx
# Restart nginx so that the changes will be applied
sudo service nginx restart
```

## Run the application
```bash
# Activate the virtual environment (if not yet activated)
source env/bin/activate
cd src/geofx
python manage.py runserver
```

## Notes
When any changes to the model have been made, this must be updated in django like this:
```bash
cd src/geofx
python manage.py makemigrations
python manage.py migrate
# (this has to be repeated anytime the model is changed)
```


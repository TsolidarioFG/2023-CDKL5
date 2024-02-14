#!/bin/bash
#Script de inicialización de APP CDKL5

#INSTALACIÓN Y CONFIGURACIÓN INICIAL
echo "Iniciando proceso de instalación APP CDKL5"
DJANGOPWD=`pwd`

echo "Actualizando máquina......"

sudo apt-get update
sudo apt-get upgrade -y

echo "Instalando python y entorno virtual......"

sudo apt-get install python3-pip -y

sudo -H pip3 install virtualenv

cd ..

echo "Configurando entorno virtual......"

virtualenv venv
source venv/bin/activate

pip3 install django

python3 -m pip install django-allauth django-crontab

echo "Instalando MySQL......"

sudo apt-get install -y gcc default-libmysqlclient-dev pkg-config

pip3 install mysqlclient

sudo apt-get install mysql-server -y

echo "CREATE USER 'django'@'localhost' IDENTIFIED BY 'password';" | sudo mysql
echo "CREATE DATABASE tfgdb;" | sudo mysql
echo "GRANT ALL PRIVILEGES ON tfgdb.* TO 'django'@'localhost';" | sudo mysql
echo "FLUSH PRIVILEGES;" | sudo mysql

#INSTALACIÓN DE LA APP

#PASO 1 --- INSTANCIAR BASE DE DATOS

echo "--- INSTALANDO APLICACIÓN ---"

echo "--- Configurando Bases de datos......"

echo "DROP DATABASE tfgdb; CREATE DATABASE tfgdb;" | mysql tfgdb --user='django' --password='password'

cd $DJANGOPWD

python3 manage.py makemigrations login
python3 manage.py makemigrations dataManagement
python3 manage.py makemigrations foro
python3 manage.py makemigrations notificaciones
python3 manage.py migrate

#PASO 2 --- SuperUser para administrador

echo "--- Creando superusuario......"

echo "from django.contrib.auth import get_user_model; CustomUser = get_user_model();  CustomUser.objects.create_superuser('admin', 'admin@email.com', 'password')" | python3 manage.py shell

#PASO 3 --- Instancia Inicial de Variables de pago

echo "INSERT INTO tfgdb.dataManagement_macros(TarifaSocios, MinimoAmigos, diaCobro, MesCobro) VALUES(36, 20, 15, 4);" | mysql tfgdb --user='django' --password='password'

#PASO 4 --- Generar crontable para funciones automatizadas

python3 manage.py crontab add

#PASO 5 --- Preparar ejecución

python3 manage.py clearsessions
echo "yes" | python3 manage.py collectstatic
echo "Aplicación instalada correctamente."
echo "para probarla, puede ejecutar el comando:"
echo "\"python3 manage.py runserver\""

#Salir del entorno virtual
deactivate
echo "Proceso de instalación finalizado."

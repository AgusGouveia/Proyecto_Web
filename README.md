# Proyecto_Web
Proyecto Web - Crypto Exchange.

Aquí iran todas las instrucciones/pasos a seguir y cosas a tener en cuenta al usar/instalar nuestro programa.

1) Creamos el entorno virtual: python3 -m venv venv 

2) activamos el entorno virtual: . venv/bin/activate

3) Instalamos flask: pip install flask

4) Instalamos las variables de enterno: pip install python-dotenv

5) debemos crear una base de datos en SQLite. Esto podemos hacerlo de forma sencilla usando DB Browser forSQLite con la siguiente sentencia: 
CREATE TABLE "movimientos" (
	"id"	INTEGER,
	"date"	TEXT,
	"time"	TEXT,
	"moneda_from"	TEXT,
	"cantidad_from"	REAL DEFAULT 0,
	"moneda_to"	TEXT,
	"cantidad_to"	REAL DEFAULT 0,
	PRIMARY KEY("id")
);

6) Consigue tu propia API KEY registrandote en https://pro.coinmarketcap.com/account

---requirements.txt:

certifi==2021.5.30
chardet==4.0.0
click==8.0.1
Flask==2.0.1
idna==2.10
itsdangerous==2.0.1
Jinja2==3.0.1
MarkupSafe==2.0.1
python-dotenv==0.17.1
requests==2.25.1
urllib3==1.26.6
Werkzeug==2.0.1

7) Para poner todo en marcha: flask run
Flask nos levantará un servidor en el puerto localhost:5000. Usarlo juntos a las distintas rutas (@app.route('/<...>')) para acceder a comportamientos/datos especificos de la api.

¡Gracías por usar mi primer proyecto!
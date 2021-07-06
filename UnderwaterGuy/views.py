from UnderwaterGuy import app
from UnderwaterGuy.dataaccess import DBmanager
from flask import jsonify, render_template, request, Response
import sqlite3, requests
from http import HTTPStatus
from datetime import date, time

dbManager = DBmanager(app.config.get('DATABASE'))


#Me devuelve el esqueleto basico de HTML
@app.route('/')
def listaMovimientos():
    return render_template('UnderwaterGuy.html')

#Muestra/añade los movimientos existentes en la base de dato a nuestro HTML
@app.route('/api/v1/movimientos')
def movimientosAPI():
    query = "SELECT * FROM movimientos ORDER BY fecha;"

    try:
        lista = dbManager.consultaMuchasSQL(query)
        return jsonify({'status': 'success', 'data': lista})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

#Me devuelve la respuesta de la API de ConinMarketCap
@app.route('/api/v1/par/<from_moneda>/<to_moneda>/<amount>')
@app.route('/api/v1/par/<_from>/<_to>')
def par(from_moneda, to_moneda, amount = 1.0):
    url = f"https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={amount}&symbol={from_moneda}&convert={to_moneda}&CMC_PRO_API_KEY=46341c71-80dc-48ec-8a33-056636905126"
    res = requests.get(url)
    return Response(res) #Response es un objeto de tipo respuesta del metodo requests 

#Según la pètición, me devuelve 1 movimiento mediante el ID o realiza un POST
@app.route('/api/v1/movimiento/<int:id>', methods=['GET'])
@app.route('/api/v1/movimiento', methods=['POST'])
def detalleMovimiento(id=None):

    try:
        if request.method == 'GET':
            data = dbManager.consultaUnaSQL("SELECT * FROM movimientos WHERE id = ?", [id])
            if data:
                return jsonify({
                    "status": "success",
                    "data": data
                })
            else:
                return jsonify({"status": "fail", "mensaje": "data no encontrada"}), HTTPStatus.BAD_REQUEST

        if request.method == 'POST':
             #if request.json['from_moneda'] != 'EUR':
                #if calculaSaldoNecesario(request.json['from_moneda']) < float(request.json['from_cantidad']):
                    #return jsonify({"status": "fail", "mensaje": "Saldo insuficiente"}), HTTPStatus.OK
            
            #datos = request.json
            #datos["fecha"] = str(fecha)
            #datos["hora"] = str(hora)

            #HAY QUE VALIDAR que la moneda sea EUR. De no serlo, comprobar que exista suficiente saldo para grabar el movimiento

            #Abrimos la base de la datos con la tabla modificar (falta agregar los pares de monedas)
            dbManager.modificaTablaSQL("""
                INSERT INTO movimientos 
                       (fecha, hora, from_moneda, from_cantidad, to_moneda, to_cantidad)
                VALUES (:fecha, :hora, :from_moneda, :from_cantidad, :to_moneda, :to_cantidad) 
                """, request.json)
            return jsonify({"status": "success", "id": "Nuevo id creado", "monedas": "Aquí irian monedas from y to"}), HTTPStatus.CREATED


    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST

#Devolverá el estado de la inversión
@app.route('/api/vi/status')
def statusInversion():
    query = "SELECT  FROM movimientos ORDER BY fecha;"
    balance = inversiones 

    try:
        return jsonify ({'status': 'success', 'data': balance})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

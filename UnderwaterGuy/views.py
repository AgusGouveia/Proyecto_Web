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
    query = "SELECT * FROM movimientos ORDER BY date;"

    try:
        lista = dbManager.consultaMuchasSQL(query)
        return jsonify({'status': 'success', 'data': lista})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

#Me devuelve la respuesta de la API de ConinMarketCap
@app.route('/api/v1/par/<moneda_from>/<moneda_to>/<amount>')
@app.route('/api/v1/par/<_from>/<_to>')
def par(moneda_from, moneda_to, amount = 1.0):
    url = f"https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={amount}&symbol={moneda_from}&convert={moneda_to}&CMC_PRO_API_KEY=46341c71-80dc-48ec-8a33-056636905126"
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
                       (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to)
                VALUES (:date, :time, :moneda_from, :cantidad_from, :moneda_to, :cantidad_to) 
                """, request.json)
            return jsonify({"status": "success", "id": "Nuevo id creado", "monedas": "Aquí irian monedas from y to"}), HTTPStatus.CREATED


    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST

#Devolverá el estado de la inversión
@app.route('/api/v1/status')
def statusInversion():
    totalEurosInvertidos = "SELECT SUM(cantidad_from) FROM movimientos WHERE moneda_from = 'EUR';" #Invertido
    cantidadToEuro = "SELECT SUM(cantidad_to) FROM movimientos WHERE moneda_to = 'EUR';"

    try:
        lista = dbManager.consultaMuchasSQL(totalEurosInvertidos) + dbManager.consultaMuchasSQL(cantidadToEuro)
        listaDic1 = lista[0]
        listaDic2 = lista[1]
        saldoEurosInvertidos = listaDic1.get('SUM(cantidad_from)') - listaDic2.get('SUM(cantidad_to)')
        
        #lista3 = dbManager.consultaMuchasSQL(saldoEurosInvertidos)
        return jsonify ({'status': 'success', 'Total de € Invertidos': listaDic1.get('SUM(cantidad_from)'), 'Saldo de € Invertidos': saldoEurosInvertidos})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

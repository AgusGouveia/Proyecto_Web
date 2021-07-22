from UnderwaterGuy import app
from UnderwaterGuy.dataaccess import DBmanager
from flask import jsonify, render_template, request, Response
import sqlite3, requests
from http import HTTPStatus
from datetime import date, time
import json

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
@app.route('/api/v1/par/<moneda_from>/<moneda_to>')
def par(moneda_from, moneda_to, amount = 1.0):
    url = f"https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={amount}&symbol={moneda_from}&convert={moneda_to}&CMC_PRO_API_KEY=46341c71-80dc-48ec-8a33-056636905126"
    res = requests.get(url) 
    return res.json()['data']['quote']['EUR']['price'] #Response es un objeto de tipo respuesta del metodo requests(He modificado esta linea)

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
            dbManager.modificaTablaSQL("""
                INSERT INTO movimientos 
                       (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to)
                VALUES (:date, :time, :moneda_from, :cantidad_from, :moneda_to, :cantidad_to) 
                """, request.json)
            return jsonify({"status": "success", "id": "Nuevo id creado", "moneda_from": request.json['moneda_from'], 'moneda_to': request.json['moneda_to']}), HTTPStatus.CREATED


    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST

#Devolverá el estado de la inversión
@app.route('/api/v1/status')
def statusInversion():
    totalEurosInvertidos = "SELECT SUM(cantidad_from) FROM movimientos WHERE moneda_from = 'EUR';" #Invertido
    cantidadToEuro = "SELECT SUM(cantidad_to) FROM movimientos WHERE moneda_to = 'EUR';"
    
    categorias = {
        'EUR': 'Euro(EUR)',
        'BTC': 'Bitcoin(BTC)',
        'ETH': 'Ethereum(ETH)',
        'LTC': 'Litecoin(LTC)',
        'DOGE': 'Dogecoin(DOGE)'
    }

    cantidadTo = {
        'EUR': 0,
        'BTC': 0,
        'ETH': 0,
        'LTC': 0,
        'DOGE': 0
    }

    cantidadFrom = {
        'EUR': 0,
        'BTC': 0,
        'ETH': 0,
        'LTC': 0,
        'DOGE': 0
    }
    total = {
        'EUR': 0,
        'BTC': 0,
        'ETH': 0,
        'LTC': 0,
        'DOGE': 0
    }
    ValorActualCryptos = {'Euros' : 0}

    for clave in categorias:
        cryptosCompradas = dbManager.consultaMuchasSQL("SELECT SUM(cantidad_to) as total FROM movimientos WHERE moneda_to = ?", [clave])
        cantidadTo[clave] = (cryptosCompradas[0].get('total')) or 0
        cryptosVendidas = dbManager.consultaMuchasSQL("SELECT SUM(cantidad_from) as total FROM movimientos WHERE moneda_from = ?", [clave])
        cantidadFrom[clave] = (cryptosVendidas[0].get('total')) or 0
        if cantidadTo.get(clave) and cantidadFrom.get(clave) != None:
            total[clave] = float(cantidadTo.get(clave)) - float(cantidadFrom.get(clave))
        if float(total.get(clave)) > 0:
            ValorActualCryptos['Euros'] += par(clave, 'EUR', float(total.get(clave)))
       
    try:
        lista = dbManager.consultaMuchasSQL(totalEurosInvertidos) + dbManager.consultaMuchasSQL(cantidadToEuro)
        listaDic1 = lista[0]
        listaDic2 = lista[1]
        saldoEurosInvertidos = listaDic1.get('SUM(cantidad_from)') - listaDic2.get('SUM(cantidad_to)') #De cripto a € (Criptos vendidas por €, o sea, saldo de € ACTUAL)
        resultado = (ValorActualCryptos['Euros'] + listaDic1.get('SUM(cantidad_from)') + saldoEurosInvertidos)  
        return jsonify ({'status': 'success', 'data': {'Total_€_Invertidos': listaDic1.get('SUM(cantidad_from)'), 'Saldo_€_Invertidos': saldoEurosInvertidos, 'Valor_Actual_Cryptos': ValorActualCryptos['Euros'], 'Resultado': resultado}})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

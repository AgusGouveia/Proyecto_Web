from os import abort
from UnderwaterGuy import app
from UnderwaterGuy.dataaccess import DBmanager
from flask import jsonify, render_template, request, Response
import sqlite3, requests
from http import HTTPStatus
from datetime import date, time, datetime
import json

dbManager = DBmanager(app.config.get('DATABASE'))
    
#Me devuelve el esqueleto basico de HTML
@app.route('/')
def listaMovimientos():
    return render_template('UnderwaterGuy.html')

#Muestra/añade los movimientos existentes en la base de dato a nuestro HTML
@app.route('/api/v1/movimientos')
def movimientosAPI():
    query = "SELECT * FROM movimientos ORDER BY date DESC;"

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
    return Response(res) #Response es un objeto de tipo respuesta del metodo requests(He modificado esta linea)

#Según la pètición, me devuelve 1 movimiento mediante el ID o realiza un POST
@app.route('/api/v1/movimiento/<int:id>', methods=['GET'])
@app.route('/api/v1/movimiento', methods=['POST'])
def detalleMovimiento(id=None):
    today = date.today()
    hora = datetime.now()
    hora = hora.strftime('%H:%M:%S')
    fecha = today.isoformat()

    try:
        if request.method == 'GET':
            data = dbManager.consultaUnaSQL("SELECT * FROM movimientos WHERE id = ?", [id])
            if data:
                return jsonify({"status": "success", "data": data})
            else:
                return jsonify({"status": "fail", "mensaje": "data no encontrada"}), HTTPStatus.BAD_REQUEST

        if request.method == 'POST':
            datos = request.json
            datos['date'] = fecha
            datos['time'] = hora

            if request.json['moneda_from'] != 'EUR' or request.json['moneda_from'] and request.json['moneda_to'] == 'EUR':
                if request.json['moneda_from'] == request.json['moneda_to']:
                    return jsonify({"status": "fail", "mensaje": "Las monedas tienen que ser diferentes"}), HTTPStatus.OK

            saldoExistente = calculaSaldoExistente()
            calculaCantidadTo = par(request.json['moneda_from'], request.json['moneda_to'], float(request.json['cantidad_from']))
            transformaAJson = json.loads(calculaCantidadTo.data)
            valorCantidadTo = transformaAJson['data']['quote'][request.json['moneda_to']]['price']
            request.json['cantidad_to'] = valorCantidadTo

            if (float(request.json['cantidad_from']) > saldoExistente['Monedas_Disponibles'][request.json['moneda_from']] and request.json['moneda_from'] != 'EUR') or (float(request.json['cantidad_to']) != valorCantidadTo):
                return jsonify({"status": "fail", "mensaje": "Saldo insuficiente"}), HTTPStatus.OK

            else:
                dbManager.modificaTablaSQL("""
                    INSERT INTO movimientos 
                        (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to)
                    VALUES (:date, :time, :moneda_from, :cantidad_from, :moneda_to, :cantidad_to) 
                    """, request.json)
                return jsonify({"status": "success", "mensaje": "Compra realizada", "id": "Nuevo id creado", "Vendiste": request.json['moneda_from'], 'Compraste': request.json['moneda_to']}), HTTPStatus.CREATED
                

    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST

#Devolverá el estado de la inversión
@app.route('/api/v1/status')
def statusInversion():
    try:
        status = calculaSaldoExistente()
        return jsonify ({'status': 'success', 'data': status})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

def calculaSaldoExistente():
    totalEurosInvertidos = "SELECT SUM(cantidad_from) FROM movimientos WHERE moneda_from = 'EUR';" #Invertido
    cantidadToEuro = "SELECT SUM(cantidad_to) FROM movimientos WHERE moneda_to = 'EUR';"
    
    categorias = {
        'EUR': 'Euro(EUR)',
        'BTC': 'Bitcoin(BTC)',
        'ETH': 'Ethereum(ETH)',
        'LTC': 'Litecoin(LTC)',
        'DOGE': 'Dogecoin(DOGE)',
        'BNB': 'BinanceCoin(BNB)',
        'EOS': 'EOS(EOS)',
        'XLM': 'Stellar(XLM)',
        'TRX': 'Tron(TRX)',
        'XRP': 'Ripple(XRP)',
        'BCH': 'BitcoinCash(BCH)',
        'USDT': 'Tether(USDT)',
        'BSV': 'BitcoinSV(BSV)',
        'ADA': 'Cardano(ADA)'
    }

    cantidadTo = {
        'EUR': 0,
        'BTC': 0,
        'ETH': 0,
        'LTC': 0,
        'DOGE': 0,
        'BNB': 0,
        'EOS': 0,
        'XLM': 0,
        'TRX': 0,
        'XRP': 0,
        'BCH': 0,
        'USDT': 0,
        'BSV': 0,
        'ADA': 0
    }

    cantidadFrom = {
       'EUR': 0,
        'BTC': 0,
        'ETH': 0,
        'LTC': 0,
        'DOGE': 0,
        'BNB': 0,
        'EOS': 0,
        'XLM': 0,
        'TRX': 0,
        'XRP': 0,
        'BCH': 0,
        'USDT': 0,
        'BSV': 0,
        'ADA': 0
    }
    total = {
        'EUR': 0,
        'BTC': 0,
        'ETH': 0,
        'LTC': 0,
        'DOGE': 0,
        'BNB': 0,
        'EOS': 0,
        'XLM': 0,
        'TRX': 0,
        'XRP': 0,
        'BCH': 0,
        'USDT': 0,
        'BSV': 0,
        'ADA': 0
    }
    ValorActualCryptos = {'Euros' : 0}

    for clave in categorias:
        cryptosCompradas = dbManager.consultaMuchasSQL("SELECT SUM(cantidad_to) as total FROM movimientos WHERE moneda_to = ?", [clave])
        cantidadTo[clave] = (cryptosCompradas[0].get('total')) or 0
        cryptosVendidas = dbManager.consultaMuchasSQL("SELECT SUM(cantidad_from) as total FROM movimientos WHERE moneda_from = ?", [clave])
        cantidadFrom[clave] = (cryptosVendidas[0].get('total')) or 0
        if cantidadTo.get(clave) != None and cantidadFrom.get(clave) != None:
            total[clave] = float(cantidadTo.get(clave)) - float(cantidadFrom.get(clave))
        if float(total.get(clave)) > 0:
            llamadaApiStatus = par(clave, 'EUR', float(total.get(clave)))
            transformaJson = json.loads(llamadaApiStatus.data)
            valorEnEuros = transformaJson['data']['quote']['EUR']['price']
            ValorActualCryptos['Euros'] += valorEnEuros
    totalMonedas = total
    
    lista = dbManager.consultaMuchasSQL(totalEurosInvertidos) + dbManager.consultaMuchasSQL(cantidadToEuro)
    listaDic1 = lista[0]
    listaDic2 = lista[1]
    saldoEurosInvertidos = listaDic2.get('SUM(cantidad_to)') - listaDic1.get('SUM(cantidad_from)') #De cripto a € (Criptos vendidas por €, o sea, saldo de € ACTUAL)
    ValorActualInversion = (ValorActualCryptos['Euros'] + listaDic1.get('SUM(cantidad_from)') + saldoEurosInvertidos)
    profit = ValorActualInversion - listaDic1.get('SUM(cantidad_from)')
    data = {'Total_Euros_Invertidos': listaDic1.get('SUM(cantidad_from)'), 'Saldo_Euros_Invertidos': saldoEurosInvertidos, 'Valor_Actual_Cryptos_En_Euros': ValorActualCryptos['Euros'], 'Valor_Actual_Inversion': ValorActualInversion, 'Monedas_Disponibles': totalMonedas, 'Resultado': profit}
    return data

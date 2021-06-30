from UnderwaterGuy import app
from UnderwaterGuy.dataaccess import DBmanager
from flask import jsonify, render_template, request
import sqlite3
from http import HTTPStatus

dbManager = DBmanager(app.config.get('DATABASE'))

@app.route('/')
def listaMovimientos():
    return render_template('UnderwaterGuy.html')

@app.route('/api/v1/movimientos')
def movimientosAPI():
    query = "SELECT * FROM movimientos ORDER BY fecha;"

    try:
        lista = dbManager.consultaMuchasSQL(query)
        return jsonify({'status': 'success', 'movimientos': lista})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)})

@app.route('/api/v1/movimiento/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/v1/movimiento', methods=['POST'])
def detalleMovimiento(id=None):

    try:
        if request.method in ('GET', 'PUT', 'DELETE'):
            movimiento = dbManager.consultaUnaSQL("SELECT * FROM movimientos WHERE id = ?", [id])
        
        if request.method == 'GET':
            if movimiento:
                return jsonify({
                    "status": "success",
                    "movimiento": movimiento
                })
            else:
                return jsonify({"status": "fail", "mensaje": "movimiento no encontrado"}), HTTPStatus.NOT_FOUND

        if request.method == 'PUT':
            dbManager.modificaTablaSQL("""
                UPDATE movimientos 
                SET fecha=:fecha, hora=:hora, from_moneda=:from_moneda, from_cantidad=:from_cantidad, to_moneda=:to_moneda, to_cantidad=:to_cantidad
                WHERE id = {}""".format(id), request.json)

            return jsonify({"status": "success", "mensaje": "registro modificado"})

        if request.method == 'DELETE':
            dbManager.modificaTablaSQL("""
                DELETE FROM movimientos 
                WHERE id = ?""", [id])

            return jsonify({"status": "success", "mensaje": "registro borrado"})

        if request.method == 'POST':
            dbManager.modificaTablaSQL("""
                INSERT INTO movimientos 
                       (fecha, hora, from_moneda, from_cantidad, to_moneda, to_cantidad)
                VALUES (:fecha, :hora, :from_moneda, :from_cantidad, :to_moneda, :to_cantidad) 
                """, request.json)
            return jsonify({"status": "success", "mensaje": "registro creado"}), HTTPStatus.CREATED


    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST
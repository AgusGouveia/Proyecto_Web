/* La carpeta static guardará los recursos 
a los que se acceden desde el NAVEGADOR */

//Los objetos en JS tienen CASI la misma estructura que los dicc en Python
const categorias = {
    EUR: 'Euro(EUR)',
    BTC: 'Bitcoin(BTC)',
    ETH: 'Ethereum(ETH)',
    LTC: 'Litecoin(LTC)',
    DOGE: 'Dogecoin(DOGE)',
    BNB: 'BinanceCoin(BNB)',
    EOS: 'EOS(EOS)',
    XLM: 'Stellar(XLM)',
    TRX: 'Tron(TRX)',
    XRP: 'Ripple(XRP)',
    BCH: 'BitcoinCash(BCH)',
    USDT: 'Tether(USDT)',
    BSV: 'BitcoinSV(BSV)',
    ADA: 'Cardano(ADA)'

}

let losMovimientos 
xhr = new XMLHttpRequest() // Manejador de peticiones de forma asincrona
xhr2 = new XMLHttpRequest() // Necesitamos 2 para poder hacer dos llamadas sin que se pisen una a la otra
xhr3 = new XMLHttpRequest() // necesitamos 3 ... 
function recibeRespuestaStatus() {
    if (this.readyState === 4 && (this.status === 200 || this.status === 201)) {
        const respuesta = JSON.parse(this.responseText)
        if (respuesta.status !== 'success') {
            alert("Se ha producido un error en acceso a servidor: "+ respuesta.mensaje)
            return
        }
        const data = respuesta.data
        const invertido = document.getElementById('invertido')
        const valorActual = document.getElementById('valor-inversion') 
        const resultadoInversion = document.getElementById('resultado')
        invertido.value = data.Total_Euros_Invertidos + "€"
        valorActual.value = data.Valor_Actual_Inversion.toFixed(8) + "€"
        resultadoInversion.value = data.Resultado.toFixed(8) + "€"
        
    }
    else {
        alert("Se ha producido un error interno al calcular el estado de tu inversión: " + this.status)
    }

}

function recibeRespuesta() {
    if (this.readyState === 4 && (this.status === 200 || this.status === 201)) {
        const respuesta = JSON.parse(this.responseText)
        console.log(respuesta)

        if (respuesta.status !== 'success') {
            alert("Se ha producido un error en acceso al servidor: " + respuesta.mensaje)
            return
        }

        alert(respuesta.mensaje)

        llamaApiMovimientos()
    }
}

function muestraMovimientos() { 
    if (this.readyState === 4 && this.status === 200) {
        const respuesta = JSON.parse(this.responseText) //Convierte de string a objeto JSON

        if (respuesta.status !== 'success') {
            alert("Se ha producido un error en la consulta de movimientos")
            return
        }

        losMovimientos = respuesta.data
        const tbody = document.querySelector(".tabla-movimientos tbody") // Seleccionamos la clase tabla-movi para insentar cosas dentro de tbody
        tbody.innerHTML = ""

        for (let i = 0; i < respuesta.data.length; i++) {
            const movimiento = respuesta.data[i]
            const fila = document.createElement("tr")


            const dentro = `
                <td>${movimiento.date}</td>
                <td>${movimiento.time}</td>
                <td>${movimiento.moneda_from}</td>
                <td>${movimiento.cantidad_from}</td>
                <td>${movimiento.moneda_to}</td>
                <td>${movimiento.cantidad_to}</td>
            `
            fila.innerHTML = dentro
            tbody.appendChild(fila)
        }
    }
    else {
        alert("Se ha producido un error interno al mostrar tus movimientos: " + this.status)
    }
}


function llamaApiMovimientos() {
    xhr.open('GET', `http://localhost:5000/api/v1/movimientos`, true) //Petición de tipo GET
    xhr.onload = muestraMovimientos 
    xhr.send() // Envio de petición a la URL
}

function capturaFormMovimiento() {
    const movimiento = {} // Esta función captura los valores en el formulario y los guarda en la variable movimiento, en un objeto
    movimiento.moneda_from = document.querySelector("#moneda_from").value // movimiento es el objeto, from_moneda es el atributo
    movimiento.cantidad_from = document.querySelector("#cantidad_from").value
    movimiento.moneda_to = document.querySelector("#moneda_to").value
    movimiento.cantidad_to = document.querySelector("#cantidad_to").value
    
    return movimiento    
}   


/*function validar(movimiento) {

    if (movimiento.concepto === "") {
        alert("Concepto obligatorio")
        return false
    }

    if (movimiento.cantidad <= 0) {
        alert("La cantidad ha de ser positiva")
        return false
    }

    return true
}*/

function llamaApiCreaMovimiento(ev) {
    ev.preventDefault()


   const movimiento = capturaFormMovimiento()
    /*if (!validar(movimiento)) {
        return
    }*/


    xhr.open("POST", `http://localhost:5000/api/v1/movimiento`, true)
    xhr.onload = recibeRespuesta //El metodo onload es el que se mantiene esperando la respuesta asincrona para luego procesarla

    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8") // Informamos al servidor que los datos que vamos a mandar son de tipo JSON

    xhr.send(JSON.stringify(movimiento)) // Cadeniza el movimiento que deseamos enviar
}

function llamaApiStatus() {
    xhr2.open ("GET", `http://localhost:5000/api/v1/status`, true) //Crea la URL
    xhr2.onload = recibeRespuestaStatus
    xhr2.send() // Envia la URL
}



window.onload = function() {
    /* Todo lo que haya aquí adentro se ejecutará una vez que el HTML se renderice, o sea, exactamente despues
    de que la pagina acabe de cargarse, evitando que el JS entre en juego antes de tiempo. */  
    
    llamaApiMovimientos()
    llamaApiStatus()

   /* document.querySelector("#modificar")
        .addEventListener("click", llamaApiModificaMovimiento) */

    document.querySelector("#aceptar")
        .addEventListener("click", llamaApiCreaMovimiento)

}

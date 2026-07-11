$(document).ready(function() {
    // Reloj en vivo: fecha/hora gregoriana + fecha hijri en el menú superior
    function actualizarReloj() {
        var elG = document.getElementById('fecha-gregoriana');
        if (elG) {
            elG.textContent = new Date().toLocaleString('es-ES', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
        }
        var elH = document.getElementById('fecha-hijri');
        if (elH && typeof moment !== 'undefined' && typeof moment().iDate === 'function') {
            var diaAr = '';
            try { diaAr = new Date().toLocaleDateString('ar', { weekday: 'long' }) + ' '; } catch (e) {}
            try {
                elH.textContent = diaAr + moment().locale('ar').format('iDD iMMMM iYYYY');
            } catch (e) {
                elH.textContent = diaAr + moment().locale('ar').format('iYYYY/iM/iD');
            }
        } else if (elH) {
            elH.textContent = '';
        }
        setTimeout(actualizarReloj, 1000);
    }
    actualizarReloj();

    // Horarios de salat del día vía API de Aladhan (ciudad seleccionable)
    var CIUDADES_DISPLAY = {
        'Rabat': 'Rabat', 'Casablanca': 'Casablanca', 'Marrakech': 'Marrakech',
        'Fes': 'Fès', 'Tangier': 'Tánger',
        'Seville': 'Sevilla', 'Madrid': 'Madrid', 'Barcelona': 'Barcelona',
        'Malaga': 'Málaga', 'Granada': 'Granada'
    };
    // Etiquetas mostradas en el aviso y horas guardadas en memoria
    var SALAT_LABELS = { Fajr: 'Fajr', Dhuhr: 'Duhr', Asr: 'Asr', Maghrib: 'Maghrib', Isha: 'Isha' };
    var salatTimings = {};              // { Fajr: '05:12', Dhuhr: '13:40', ... }
    var salatNotificados = {};          // evita repetir el mismo aviso
    var SALAT_AVISO_MIN = 10;           // minutos de antelación para el pre-aviso

    function cargarSalat(ciudad, pais) {
        var nombreEl = document.getElementById('salat-ciudad-nombre');
        if (nombreEl) nombreEl.textContent = CIUDADES_DISPLAY[ciudad] || ciudad;
        var hoy = new Date();
        var y = hoy.getFullYear();
        var m = ('0' + (hoy.getMonth() + 1)).slice(-2);
        var d = ('0' + hoy.getDate()).slice(-2);
        var method = (pais === 'Spain') ? 3 : 2;  // MWL en España, ISNA en Marruecos
        var url = 'https://api.aladhan.com/v1/timingsByCity?city=' + encodeURIComponent(ciudad) +
                  '&country=' + encodeURIComponent(pais) + '&method=' + method + '&date=' + y + '-' + m + '-' + d;
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.data && data.data.timings) {
                    var t = data.data.timings;
                    var map = { Fajr: 'salat-fajr', Dhuhr: 'salat-duhr', Asr: 'salat-asr', Maghrib: 'salat-maghrib', Isha: 'salat-isha' };
                    salatTimings = {};
                    Object.keys(map).forEach(function (k) {
                        var valor = (t[k] || '—').replace(' (MA)', '').replace(' (EET)', '').trim();
                        var el = document.getElementById(map[k]);
                        if (el) el.textContent = valor;
                        var hhmm = valor.match(/(\d{1,2}):(\d{2})/);
                        if (hhmm) salatTimings[k] = hhmm[1] + ':' + hhmm[2];
                    });
                    comprobarSalat();  // comprobar de inmediato tras cargar
                }
            })
            .catch(function () { /* sin conexión: se quedan en "—" */ });
    }

    // Muestra un toast de 30 s (una sola vez por evento/día)
    function notificarSalat(clave, icon, titulo) {
        if (salatNotificados[clave]) return;
        salatNotificados[clave] = true;
        if (typeof Swal === 'undefined') return;
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: icon,
            title: titulo,
            showConfirmButton: false,
            timer: 30000,
            timerProgressBar: true,
            didOpen: function (toast) {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
    }

    // Comprueba si se acerca o llega la hora de alguna salat
    function comprobarSalat() {
        if (!salatTimings) return;
        var now = new Date();
        var p2 = function (n) { return ('0' + n).slice(-2); };
        var fechaKey = now.getFullYear() + '-' + p2(now.getMonth() + 1) + '-' + p2(now.getDate());
        var minsAhora = now.getHours() * 60 + now.getMinutes();
        Object.keys(salatTimings).forEach(function (k) {
            var partes = salatTimings[k].split(':');
            var minsSalat = parseInt(partes[0], 10) * 60 + parseInt(partes[1], 10);
            var diff = minsSalat - minsAhora;
            var nombre = SALAT_LABELS[k] || k;
            if (diff === SALAT_AVISO_MIN) {
                notificarSalat(fechaKey + '|' + k + '|aviso', 'warning',
                    'Se acerca la Salat de ' + nombre + ' (en ' + SALAT_AVISO_MIN + ' min)');
            }
            if (diff === 0) {
                notificarSalat(fechaKey + '|' + k + '|hora', 'info',
                    'Es la hora de la Salat de ' + nombre);
            }
        });
    }
    setInterval(comprobarSalat, 20000);

    var selSalat = document.getElementById('salat-ciudad');
    if (selSalat) {
        var guardado = localStorage.getItem('salat_ciudad') || 'Seville|Spain';
        selSalat.value = guardado;
        selSalat.addEventListener('change', function () {
            localStorage.setItem('salat_ciudad', this.value);
            var p = this.value.split('|');
            cargarSalat(p[0], p[1]);
        });
        var partes = guardado.split('|');
        cargarSalat(partes[0], partes[1]);
    }

    $('.datatable').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
        },
        lengthMenu: [5, 10, 25, 50, 100],
        pageLength: 25,
        responsive: true,
        order: [[0, 'desc']]
    });

    $('.swal-confirm').on('click', function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        var msg = $(this).data('message') || '¿Estás seguro?';
        Swal.fire({
            title: '¿Estás seguro?',
            text: msg,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = href;
            }
        });
    });
});

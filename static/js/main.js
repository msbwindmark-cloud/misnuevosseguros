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

    // Horarios de salat del día vía API de Aladhan (ciudad desde BD)
    var salatCiudades = {};  // { 'ciudad|pais': { metodo: N, nombre: '...' } }
    var salatTimings = {};
    var salatNotificados = {};
    var SALAT_AVISO_MIN = 10;

    function cargarCiudadesSalat() {
        var sel = document.getElementById('salat-ciudad');
        if (!sel) return;
        fetch('/core/api/ciudades-salat/')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                sel.innerHTML = '';
                var grupos = data.grupos || {};
                Object.keys(grupos).forEach(function(grupo) {
                    var og = document.createElement('optgroup');
                    og.label = grupo;
                    grupos[grupo].forEach(function(c) {
                        var opt = document.createElement('option');
                        opt.value = c.ciudad_api + '|' + c.pais_api + '|' + c.metodo;
                        opt.textContent = c.nombre;
                        og.appendChild(opt);
                        salatCiudades[c.ciudad_api + '|' + c.pais_api] = { metodo: c.metodo, nombre: c.nombre };
                    });
                    sel.appendChild(og);
                });
                var guardado = localStorage.getItem('salat_ciudad') || '';
                if (guardado && sel.querySelector('option[value="' + guardado + '"]')) {
                    sel.value = guardado;
                } else if (sel.options.length > 0) {
                    sel.selectedIndex = 0;
                }
                sel.addEventListener('change', function() {
                    localStorage.setItem('salat_ciudad', this.value);
                    var p = this.value.split('|');
                    cargarSalat(p[0], p[1], parseInt(p[2]) || 2);
                });
                if (sel.value) {
                    var partes = sel.value.split('|');
                    cargarSalat(partes[0], partes[1], parseInt(partes[2]) || 2);
                }
            })
            .catch(function() {});
    }

    function cargarSalat(ciudad, pais, method) {
        var nombreEl = document.getElementById('salat-ciudad-nombre');
        var key = ciudad + '|' + pais;
        if (nombreEl) nombreEl.textContent = (salatCiudades[key] || {}).nombre || ciudad;
        var hoy = new Date();
        var y = hoy.getFullYear();
        var m = ('0' + (hoy.getMonth() + 1)).slice(-2);
        var d = ('0' + hoy.getDate()).slice(-2);
        var url = 'https://api.aladhan.com/v1/timingsByCity?city=' + encodeURIComponent(ciudad) +
                  '&country=' + encodeURIComponent(pais) + '&method=' + method + '&date=' + y + '-' + m + '-' + d;
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data && data.data && data.data.timings) {
                    var t = data.data.timings;
                    var map = { Fajr: 'salat-fajr', Dhuhr: 'salat-duhr', Asr: 'salat-asr', Maghrib: 'salat-maghrib', Isha: 'salat-isha' };
                    salatTimings = {};
                    Object.keys(map).forEach(function(k) {
                        var valor = (t[k] || '—').replace(/ \(.+\)/, '').trim();
                        var el = document.getElementById(map[k]);
                        if (el) el.textContent = valor;
                        var hhmm = valor.match(/(\d{1,2}):(\d{2})/);
                        if (hhmm) salatTimings[k] = hhmm[1] + ':' + hhmm[2];
                    });
                    comprobarSalat();
                }
            })
            .catch(function() {});
    }

    function notificarSalat(clave, icon, titulo) {
        if (salatNotificados[clave]) return;
        salatNotificados[clave] = true;
        if (typeof Swal === 'undefined') return;
        Swal.fire({
            toast: true, position: 'top-end', icon: icon, title: titulo,
            showConfirmButton: false, timer: 30000, timerProgressBar: true,
            didOpen: function(toast) {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
    }
    window.notificarSalat = notificarSalat;

    function comprobarSalat() {
        if (!salatTimings || Object.keys(salatTimings).length === 0) return;
        var now = new Date();
        var p2 = function(n) { return ('0' + n).slice(-2); };
        var fechaKey = now.getFullYear() + '-' + p2(now.getMonth() + 1) + '-' + p2(now.getDate());
        var minsAhora = now.getHours() * 60 + now.getMinutes();
        Object.keys(salatTimings).forEach(function(k) {
            var partes = salatTimings[k].split(':');
            var minsSalat = parseInt(partes[0], 10) * 60 + parseInt(partes[1], 10);
            var diff = minsSalat - minsAhora;
            var nombre = k;
            var horaSalat = salatTimings[k];
            var fechaBonita = now.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
            if (diff >= 0 && diff <= SALAT_AVISO_MIN) {
                notificarSalat(fechaKey + '|' + k + '|aviso', 'warning',
                    fechaBonita + ' — Salat ' + nombre + ' a las ' + horaSalat + ' (en ' + diff + ' min)');
            }
            if (diff >= -1 && diff <= 0) {
                notificarSalat(fechaKey + '|' + k + '|hora', 'info',
                    fechaBonita + ' — Es la hora de la Salat ' + nombre + ' (' + horaSalat + ')');
            }
        });
    }
    setInterval(comprobarSalat, 20000);

    cargarCiudadesSalat();

    $('.datatable').DataTable({
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
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

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
        var tempRow = document.getElementById('salat-temp-row');
        var tempEl = document.getElementById('salat-temperature');
        if (tempRow) tempRow.style.display = 'none';
        if (tempEl) tempEl.textContent = '...';
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
                    cargarTemperatura(ciudad, pais);
                }
            })
            .catch(function() {});
    }

    function cargarTemperatura(ciudad, pais) {
        var tempRow = document.getElementById('salat-temp-row');
        var tempEl = document.getElementById('salat-temperature');
        if (!tempRow || !tempEl) return;
        tempEl.textContent = '...';
        tempRow.style.display = '';
        var geoUrl = 'https://geocoding-api.open-meteo.com/v1/search?name=' + encodeURIComponent(ciudad) + '&count=1&language=es&format=json';
        fetch(geoUrl)
            .then(function(r) { return r.json(); })
            .then(function(geo) {
                if (!geo.results || geo.results.length === 0) { tempRow.style.display = 'none'; return; }
                var lat = geo.results[0].latitude;
                var lon = geo.results[0].longitude;
                var weatherUrl = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat + '&longitude=' + lon + '&current=temperature_2m,weather_code&timezone=auto';
                return fetch(weatherUrl);
            })
            .then(function(r) { return r ? r.json() : null; })
            .then(function(data) {
                if (data && data.current) {
                    var temp = data.current.temperature_2m;
                    var code = data.current.weather_code;
                    var icono = temperaturaIcono(code);
                    tempEl.textContent = icono + ' ' + temp + ' \u00B0C';
                    tempRow.style.display = '';
                } else {
                    tempRow.style.display = 'none';
                }
            })
            .catch(function() { tempRow.style.display = 'none'; });
    }

    function temperaturaIcono(code) {
        if (code === 0) return '\u2600\uFE0F';
        if (code <= 3) return '\u26C5';
        if (code <= 49) return '\uD83C\uDF2B\uFE0F';
        if (code <= 69) return '\uD83C\uDF27\uFE0F';
        if (code <= 79) return '\u2744\uFE0F';
        if (code <= 82) return '\uD83C\uDF27\uFE0F';
        if (code <= 99) return '\u26A1';
        return '\uD83C\uDF24\uFE0F';
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

    var adhanAudio = new Audio('/static/audio/adhan.mp3');
    var adhanSonando = false;
    var adhanAudioUnlocked = false;

    function desbloquearAudio() {
        if (adhanAudioUnlocked) return;
        adhanAudioUnlocked = true;
        var ctx = new (window.AudioContext || window.webkitAudioContext)();
        var src = ctx.createBufferSource();
        src.buffer = ctx.createBuffer(1, 1, 22050);
        src.connect(ctx.destination);
        src.start(0);
        if (ctx.state === 'suspended') ctx.resume();
    }
    document.addEventListener('click', desbloquearAudio, { once: true });
    document.addEventListener('touchstart', desbloquearAudio, { once: true });

    function reproducirAdhan() {
        if (adhanSonando) return;
        adhanSonando = true;
        adhanAudio.currentTime = 0;
        var p = adhanAudio.play();
        if (p) {
            p.catch(function() {
                if ('Notification' in window && Notification.permission === 'granted') {
                    new Notification('Adhan', { body: 'Haz clic en la página para escuchar el Adhan' });
                }
            });
        }
        adhanAudio.onended = function() { adhanSonando = false; };
    }
    window.reproducirAdhan = reproducirAdhan;

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
            var ciudadNombre = document.getElementById('salat-ciudad-nombre');
            var ciudadTexto = ciudadNombre ? ' — ' + ciudadNombre.textContent : '';
            if (diff >= 0 && diff <= SALAT_AVISO_MIN) {
                notificarSalat(fechaKey + '|' + k + '|aviso', 'warning',
                    fechaBonita + ' — Salat ' + nombre + ' a las ' + horaSalat + ' (en ' + diff + ' min)' + ciudadTexto);
            }
            if (diff >= -1 && diff <= 0) {
                notificarSalat(fechaKey + '|' + k + '|hora', 'info',
                    fechaBonita + ' — Es la hora de la Salat ' + nombre + ' (' + horaSalat + ')' + ciudadTexto);
                reproducirAdhan();
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
        pageLength: 5,
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

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
                    Object.keys(map).forEach(function (k) {
                        var el = document.getElementById(map[k]);
                        if (el) el.textContent = (t[k] || '—').replace(' (MA)', '').replace(' (EET)', '');
                    });
                }
            })
            .catch(function () { /* sin conexión: se quedan en "—" */ });
    }

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

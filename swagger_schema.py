manual_paths = {
    # ── POLIZAS API ────────────────────────────────────────────
    '/polizas/api/clientes/': {
        'get': {
            'summary': 'Buscar clientes',
            'operationId': 'buscar_clientes',
            'tags': ['Pólizas API'],
            'parameters': [
                {'name': 'q', 'in': 'query', 'schema': {'type': 'string'}, 'description': 'Nombre o código'},
            ],
            'responses': {'200': {'description': 'Lista de clientes'}},
        },
    },
    '/polizas/api/cliente/crear/': {
        'post': {
            'summary': 'Crear cliente AJAX',
            'operationId': 'crear_cliente_ajax',
            'tags': ['Pólizas API'],
            'requestBody': {
                'required': True,
                'content': {'application/json': {
                    'schema': {
                        'type': 'object',
                        'required': ['nom_client'],
                        'properties': {
                            'code_client': {'type': 'string'},
                            'nom_client': {'type': 'string'},
                            'telephone_client': {'type': 'string'},
                            'email_client': {'type': 'string'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Cliente creado'}},
        },
    },
    '/polizas/api/polizas/': {
        'get': {
            'summary': 'Buscar pólizas',
            'operationId': 'buscar_polizas',
            'tags': ['Pólizas API'],
            'parameters': [
                {'name': 'q', 'in': 'query', 'schema': {'type': 'string'}},
            ],
            'responses': {'200': {'description': 'Lista de pólizas'}},
        },
    },
    '/polizas/api/attestations/': {
        'get': {
            'summary': 'Buscar attestations',
            'operationId': 'buscar_attestations',
            'tags': ['Pólizas API'],
            'parameters': [
                {'name': 'q', 'in': 'query', 'schema': {'type': 'string'}},
            ],
            'responses': {'200': {'description': 'Lista de attestations'}},
        },
    },
    '/polizas/api/attestation/creer/': {
        'post': {
            'summary': 'Crear attestation AJAX',
            'operationId': 'crear_attestation_ajax',
            'tags': ['Pólizas API'],
            'requestBody': {
                'required': True,
                'content': {'application/json': {
                    'schema': {
                        'type': 'object',
                        'required': ['attestation'],
                        'properties': {
                            'attestation': {'type': 'string'},
                            'police': {'type': 'string'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Attestation creado'}},
        },
    },
    '/polizas/api/garantia/{pk}/options/': {
        'get': {
            'summary': 'Opciones de garantía',
            'operationId': 'opciones_garantia',
            'tags': ['Pólizas API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID garantía'},
            ],
            'responses': {'200': {'description': 'Lista de opciones'}},
        },
    },
    '/polizas/api/option/{pk}/franchises/': {
        'get': {
            'summary': 'Franquicias de opción',
            'operationId': 'franchises_opcion',
            'tags': ['Pólizas API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID opción'},
            ],
            'responses': {'200': {'description': 'Lista de franquicias'}},
        },
    },
    '/polizas/api/{pk}/garantias/': {
        'get': {
            'summary': 'Garantías de póliza',
            'operationId': 'garantias_poliza',
            'tags': ['Pólizas API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID póliza'},
            ],
            'responses': {'200': {'description': 'Lista de garantías'}},
        },
    },
    '/polizas/api/{pk}/documentos/': {
        'get': {
            'summary': 'Documentos de póliza',
            'operationId': 'documentos_poliza',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID póliza'},
            ],
            'responses': {'200': {'description': 'Lista de documentos'}},
        },
    },
    '/polizas/api/docs-by-police/': {
        'get': {
            'summary': 'Documentos por nº póliza',
            'operationId': 'documentos_por_police',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'police', 'in': 'query', 'schema': {'type': 'string'}, 'description': 'Nº póliza'},
            ],
            'responses': {'200': {'description': 'Lista de documentos'}},
        },
    },

    # ── POLIZAS DELETE ────────────────────────────────────────
    '/core/poliza/delete/': {
        'post': {
            'summary': 'Eliminar póliza(s) — soft delete (archiva en PolizaEliminada)',
            'operationId': 'poliza_delete',
            'tags': ['Pólizas API'],
            'requestBody': {
                'required': True,
                'content': {'application/x-www-form-urlencoded': {
                    'schema': {
                        'type': 'object',
                        'required': ['pk'],
                        'properties': {
                            'pk': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'Lista de IDs de pólizas a eliminar'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Póliza(s) eliminada(s) y archivada(s)'}},
        },
    },

    # ── SINIESTROS DELETE ─────────────────────────────────────
    '/siniestros/api/polizas/': {
        'get': {
            'summary': 'Buscar pólizas (siniestros)',
            'operationId': 'buscar_polizas_siniestros',
            'tags': ['Siniestros API'],
            'parameters': [
                {'name': 'q', 'in': 'query', 'schema': {'type': 'string'}},
            ],
            'responses': {'200': {'description': 'Lista de pólizas'}},
        },
    },
    '/siniestros/api/poliza/{pk}/documentos/': {
        'get': {
            'summary': 'Documentos de póliza (para siniestro)',
            'operationId': 'documentos_poliza_siniestro',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID póliza'},
            ],
            'responses': {'200': {'description': 'Lista de documentos'}},
        },
    },
    '/siniestros/api/{pk}/documentos/': {
        'get': {
            'summary': 'Documentos de siniestro',
            'operationId': 'documentos_siniestro',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID siniestro'},
            ],
            'responses': {'200': {'description': 'Lista de documentos del siniestro'}},
        },
    },
    '/siniestros/{pk}/docs/agregar/': {
        'post': {
            'summary': 'Agregar documentos a siniestro',
            'operationId': 'agregar_docs_siniestro',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID siniestro'},
            ],
            'requestBody': {
                'content': {'multipart/form-data': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'tipo_doc_siniestro[]': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'IDs de tipo de documento'},
                            'archivos_siniestro[]': {'type': 'array', 'items': {'type': 'string', 'format': 'binary'}, 'description': 'Archivos adjuntos'},
                            'docs_reutilizados': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'IDs de documentos reutilizados'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Documentos agregados'}},
        },
    },
    '/siniestros/{pk}/pdf/': {
        'get': {
            'summary': 'PDF de siniestro',
            'operationId': 'pdf_siniestro',
            'tags': ['Siniestros'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID siniestro'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/siniestros/pdf/': {
        'get': {
            'summary': 'PDF lista de siniestros',
            'operationId': 'pdf_lista_siniestros',
            'tags': ['Siniestros'],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/siniestros/excel/': {
        'get': {
            'summary': 'Excel lista de siniestros',
            'operationId': 'excel_lista_siniestros',
            'tags': ['Siniestros'],
            'responses': {'200': {'description': 'Excel file', 'content': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {}}}},
        },
    },

    # ── SINIESTROS DELETE ─────────────────────────────────────
    '/siniestros/{pk}/eliminar/': {
        'post': {
            'summary': 'Eliminar siniestro individual',
            'operationId': 'sinistro_delete',
            'tags': ['Siniestros API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID siniestro'},
            ],
            'responses': {'200': {'description': 'Siniestro eliminado'}},
        },
    },
    '/siniestros/eliminar-multiple/': {
        'post': {
            'summary': 'Eliminar múltiples siniestros',
            'operationId': 'sinistro_bulk_delete',
            'tags': ['Siniestros API'],
            'requestBody': {
                'required': True,
                'content': {'application/x-www-form-urlencoded': {
                    'schema': {
                        'type': 'object',
                        'required': ['pk'],
                        'properties': {
                            'pk': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'Lista de IDs de siniestros a eliminar'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Siniestros eliminados'}},
        },
    },

    # ── CLIENTES DELETE ───────────────────────────────────────
    '/clientes/{pk}/eliminar/': {
        'get': {
            'summary': 'Confirmación eliminar cliente',
            'operationId': 'cliente_delete_confirm',
            'tags': ['Clientes API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID cliente'},
            ],
            'responses': {'200': {'description': 'Página de confirmación'}},
        },
        'post': {
            'summary': 'Eliminar cliente — soft delete (archiva en ClienteEliminado)',
            'operationId': 'cliente_delete',
            'tags': ['Clientes API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID cliente'},
            ],
            'responses': {'200': {'description': 'Cliente eliminado y archivado'}},
        },
    },
    '/clientes/eliminar-multiple/': {
        'post': {
            'summary': 'Eliminar múltiples clientes — soft delete',
            'operationId': 'cliente_bulk_delete',
            'tags': ['Clientes API'],
            'requestBody': {
                'required': True,
                'content': {'application/x-www-form-urlencoded': {
                    'schema': {
                        'type': 'object',
                        'required': ['pk'],
                        'properties': {
                            'pk': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'Lista de IDs de clientes a eliminar'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Clientes eliminados y archivados'}},
        },
    },

    # ── DOCUMENTOS ─────────────────────────────────────────────
    '/documentos/add-docs/{recu}/': {
        'get': {
            'summary': 'Formulario añadir documentos',
            'operationId': 'form_add_docs',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'recu', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'Nº recibo póliza'},
            ],
            'responses': {'200': {'description': 'Formulario HTML'}},
        },
        'post': {
            'summary': 'Subir documentos a póliza',
            'operationId': 'subir_docs_poliza',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'recu', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'Nº recibo póliza'},
            ],
            'requestBody': {
                'content': {'multipart/form-data': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'tipo_doc_modal[]': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'IDs de tipo de documento'},
                            'archivo_modal[]': {'type': 'array', 'items': {'type': 'string', 'format': 'binary'}, 'description': 'Archivos adjuntos'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Documentos subidos'}},
        },
    },

    # ── TIPOS DE DOCUMENTO CRUD ───────────────────────────────
    '/documentos/tipos/': {
        'get': {
            'summary': 'Lista de tipos de documento',
            'operationId': 'tipo_documento_list',
            'tags': ['Documentos API'],
            'responses': {'200': {'description': 'Lista de tipos de documento'}},
        },
    },
    '/documentos/tipos/nuevo/': {
        'get': {
            'summary': 'Formulario crear tipo de documento',
            'operationId': 'tipo_documento_create_form',
            'tags': ['Documentos API'],
            'responses': {'200': {'description': 'Formulario HTML'}},
        },
        'post': {
            'summary': 'Crear tipo de documento',
            'operationId': 'tipo_documento_create',
            'tags': ['Documentos API'],
            'requestBody': {
                'required': True,
                'content': {'application/x-www-form-urlencoded': {
                    'schema': {
                        'type': 'object',
                        'required': ['tipo_documento'],
                        'properties': {
                            'tipo_documento': {'type': 'string', 'description': 'Nombre del tipo de documento'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Tipo de documento creado'}},
        },
    },
    '/documentos/tipos/{pk}/editar/': {
        'get': {
            'summary': 'Formulario editar tipo de documento',
            'operationId': 'tipo_documento_update_form',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID tipo de documento'},
            ],
            'responses': {'200': {'description': 'Formulario HTML con datos actuales'}},
        },
        'put': {
            'summary': 'Actualizar tipo de documento',
            'operationId': 'tipo_documento_update',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID tipo de documento'},
            ],
            'requestBody': {
                'required': True,
                'content': {'application/x-www-form-urlencoded': {
                    'schema': {
                        'type': 'object',
                        'required': ['tipo_documento'],
                        'properties': {
                            'tipo_documento': {'type': 'string', 'description': 'Nombre del tipo de documento'},
                        },
                    },
                }},
            },
            'responses': {'200': {'description': 'Tipo de documento actualizado'}},
        },
    },
    '/documentos/tipos/{pk}/eliminar/': {
        'get': {
            'summary': 'Confirmación eliminar tipo de documento',
            'operationId': 'tipo_documento_delete_confirm',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID tipo de documento'},
            ],
            'responses': {'200': {'description': 'Página de confirmación'}},
        },
        'delete': {
            'summary': 'Eliminar tipo de documento',
            'operationId': 'tipo_documento_delete',
            'tags': ['Documentos API'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID tipo de documento'},
            ],
            'responses': {'200': {'description': 'Tipo de documento eliminado'}},
        },
    },

    # ── CORE API ───────────────────────────────────────────────
    '/core/api/ciudades-salat/': {
        'get': {
            'summary': 'Ciudades de oración',
            'operationId': 'ciudades_salat',
            'tags': ['Core API'],
            'responses': {'200': {'description': 'Ciudades agrupadas por país', 'content': {'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'grupos': {'type': 'object', 'description': 'Países con listas de ciudades'},
                    },
                },
            }}}},
        },
    },
    '/core/check-expiring/': {
        'get': {
            'summary': 'Pólizas por vencer (3 días)',
            'operationId': 'check_expiring',
            'tags': ['Core API'],
            'responses': {'200': {'description': 'Lista de pólizas próximas a vencer', 'content': {'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer'},
                        'polizas': {'type': 'array', 'items': {'type': 'object'}},
                    },
                },
            }}}},
        },
    },

    # ── EXPORTACIONES ──────────────────────────────────────────
    '/core/exportar/polizas/pdf/': {
        'get': {
            'summary': 'Exportar pólizas PDF',
            'operationId': 'export_polizas_pdf',
            'tags': ['Exportaciones'],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/core/exportar/polizas/excel/': {
        'get': {
            'summary': 'Exportar pólizas Excel',
            'operationId': 'export_polizas_excel',
            'tags': ['Exportaciones'],
            'parameters': [
                {'name': 'fecha_desde', 'in': 'query', 'schema': {'type': 'string', 'format': 'date'}},
                {'name': 'fecha_hasta', 'in': 'query', 'schema': {'type': 'string', 'format': 'date'}},
            ],
            'responses': {'200': {'description': 'Excel file', 'content': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {}}}},
        },
    },
    '/core/exportar/clientes/excel/': {
        'get': {
            'summary': 'Exportar clientes Excel',
            'operationId': 'export_clientes_excel',
            'tags': ['Exportaciones'],
            'responses': {'200': {'description': 'Excel file', 'content': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {}}}},
        },
    },
    '/core/exportar/expertos/pdf/': {
        'get': {
            'summary': 'Exportar expertos PDF',
            'operationId': 'export_expertos_pdf',
            'tags': ['Exportaciones'],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/core/poliza/{pk}/pdf/': {
        'get': {
            'summary': 'Recibo PDF de póliza',
            'operationId': 'recibo_pdf_poliza',
            'tags': ['Exportaciones'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID póliza'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/core/exportar/clientes/{pk}/pdf/': {
        'get': {
            'summary': 'Ficha cliente PDF',
            'operationId': 'ficha_cliente_pdf',
            'tags': ['Exportaciones'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID cliente'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },

    # ── FACTURACIÓN ────────────────────────────────────────────
    '/facturacion/factura/recibo/{pk}/': {
        'get': {
            'summary': 'Factura por recibo',
            'operationId': 'factura_por_recibo',
            'tags': ['Facturación'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'Nº recibo'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/facturacion/factura/cliente/{client_id}/': {
        'get': {
            'summary': 'Factura por cliente',
            'operationId': 'factura_por_cliente',
            'tags': ['Facturación'],
            'parameters': [
                {'name': 'client_id', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID cliente'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/facturacion/releve/recibo/{pk}/': {
        'get': {
            'summary': 'Relevé por recibo',
            'operationId': 'releve_por_recibo',
            'tags': ['Facturación'],
            'parameters': [
                {'name': 'pk', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'Nº recibo'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/facturacion/releve/cliente/{client_id}/': {
        'get': {
            'summary': 'Relevé por cliente',
            'operationId': 'releve_por_cliente',
            'tags': ['Facturación'],
            'parameters': [
                {'name': 'client_id', 'in': 'path', 'schema': {'type': 'integer'}, 'description': 'ID cliente'},
            ],
            'responses': {'200': {'description': 'PDF file', 'content': {'application/pdf': {}}}},
        },
    },
    '/facturacion/balance-pendiente/': {
        'get': {
            'summary': 'Balance pendiente',
            'operationId': 'balance_pendiente',
            'tags': ['Facturación'],
            'responses': {'200': {'description': 'Balance de pagos pendientes'}},
        },
    },
    '/facturacion/consulta-vencimiento/': {
        'get': {
            'summary': 'Consulta vencimiento',
            'operationId': 'consulta_vencimiento',
            'tags': ['Facturación'],
            'responses': {'200': {'description': 'Información de vencimiento'}},
        },
    },

    # ── AUDITORÍA ──────────────────────────────────────────────
    '/audit/': {
        'get': {
            'summary': 'Log de auditoría',
            'operationId': 'log_auditoria',
            'tags': ['Auditoría'],
            'parameters': [
                {'name': 'model', 'in': 'query', 'schema': {'type': 'string'}, 'description': 'Filtrar por modelo'},
                {'name': 'action', 'in': 'query', 'schema': {'type': 'string'}, 'description': 'Filtrar por acción'},
            ],
            'responses': {'200': {'description': 'Lista de registros de auditoría'}},
        },
    },
}

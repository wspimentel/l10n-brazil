{
    "name": "Paf Integração",
    "version": "1.0",    
    "author": "Danimar Ribeiro",
    'category': 'Localisation Brasil',
    'license': 'AGPL-3',
    'website': 'http://www.bubblesort.com.br',
    "description": """
      Este módulo utiliza do RabbitMQ para enviar e receber modificações vindas do sistema PAF/ECF
    """,
    'depends': [
        'l10n_br_base',
        'product',
        'l10n_br_fiscal_obligation'
    ],
    "init_xml": [],
    'update_xml': ['l10n_br_paf_integration.xml','res_partner_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
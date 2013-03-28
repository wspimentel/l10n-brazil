{
    "name": "Obrigações fiscais",
    "version": "1.0",
    "depends": ["base"],
    "author": "Danimar Ribeiro",
    'category': 'Localisation Brasil',
    'license': 'AGPL-3',
    'website': 'http://www.openerpbrasil.org',
    "description": """
      Este módulo permite a geração das obrigações fiscais da localização brasileira.
    """,
    'depends': [
        'l10n_br_base',
    ],
    "init_xml": [],
    'update_xml': ['l10n_br_fiscal_obligation.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
{
    "name": "Server manager",
    "version": "1.0",
    "depends": ["base"],
    "author": "Danimar Ribeiro",
    "category": "Tools",
    "description": """
        Este módulo permite configurar os dominios e os bancos de dados automaticamente.
        Necessita da api para o Zerigo DNS:
        https://bitbucket.org/petersanchez/zerigodns
    """,
    "init_xml": [],
    'update_xml': ["server_manager_view.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
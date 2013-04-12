# __openerp__.py
# Danimar Ribeiro
{
    'name': "Customizacao Interface",
    'description': "Customizacao da interface do openerp",
    'author':'Danimar Ribeiro',
    'category': 'Hidden',
    'depends': ['web'],
    'js': ['static/src/js/first_module.js'],
    'css': ['static/src/css/openerp_overrides.css'],
    'active':True,
}
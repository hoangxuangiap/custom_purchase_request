{
    'name': 'Quản lý yêu cầu mua hàng',
    'version': '1.0',
    'summary': 'Module quản lý yêu cầu mua hàng từ các bộ phận',
    'category': 'Purchase Request',
    'author': 'Your Name',
    'depends': ['base', 'purchase', 'hr', 'product', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/purchase_request_rule.xml',
        'data/ir_sequence_data.xml',
        'wizard/reject_reason_wizard_views.xml', # Phải đặt file wizard TRƯỚC views
        'views/purchase_request_views.xml',     # views nằm sau wizard
        'views/purchase_request_line_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
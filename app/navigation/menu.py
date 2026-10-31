"""
Enterprise Navigation Configuration
"""

MENU_ITEMS = [
    {
        "title": "Dashboard",
        "endpoint": "dashboard.index",
        "icon": "bi-speedometer2",
    },
    {
        "title": "Catering",
        "endpoint": "catering.index",
        "icon": "bi-cup-hot",
    },
    {
        "title": "Inventory Management",
        "endpoint": None,
        "icon": "bi-box-seam",
        "hide_if_empty": True,
        "children": [
            {
                "title": "Products",
                "endpoint": "catering.products",
                "permission": "catering.product.read",
            },
            {
                "title": "Product Categories",
                "endpoint": "catering.categories",
                "permission": "catering.product_category.read",
            },
            {
                "title": "Stock Items",
                "endpoint": "catering.stock_items",
                "permission": "catering.stock_item.read",
            },
            {
                "title": "Inventory Locations",
                "endpoint": "catering.locations",
                "permission": "catering.inventory_location.read",
            },
            {
                "title": "Stock Balances",
                "endpoint": "catering.balances",
                "permission": "catering.stock_balance.read",
            },
            {
                "title": "Stock Movements",
                "endpoint": "catering.movements",
                "permission": "catering.stock_movement.read",
            },
            {
                "title": "Stock Transfers",
                "endpoint": "catering.transfers",
                "permission": "catering.stock_transfer.read",
            },
        ],
    },
    {
        "title": "Procurement",
        "endpoint": None,
        "icon": "bi-cart4",
        "children": [
            {
                "title": "Suppliers",
                "endpoint": "procurement.suppliers",
            },
            {
                "title": "Purchase Requirements",
                "endpoint": "procurement.purchase_requirements",
            },
            {
                "title": "Purchase Requests",
                "endpoint": "procurement.purchase_requests",
            },
            {
                "title": "Purchase Orders",
                "endpoint": "procurement.purchase_orders",
            },
        ],
    },
    {
        "title": "Expense Management",
        "endpoint": None,
        "icon": "bi-receipt",
        "children": [
            {
                "title": "Expense Classifications",
                "endpoint": "expense.classifications",
            },
            {
                "title": "Expenses",
                "endpoint": "expense.expenses",
            },
        ],
    },
    {
        "title": "Reports",
        "endpoint": None,
        "icon": "bi-graph-up",
        "hide_if_empty": True,
        "children": [
            {
                "title": "All Reports",
                "endpoint": "reporting.index",
                "permission": "reporting.report.view",
            },
            {
                "title": "Catering Event Profitability",
                "endpoint": "reporting.catering_event_profitability",
                "permission": "reporting.report.execute",
            },
        ],
    },
    {
        "title": "Human Resources",
        "endpoint": None,
        "icon": "bi-people",
    },
    {
        "title": "Finance",
        "endpoint": None,
        "icon": "bi-cash-stack",
    },
    {
        "title": "Assets",
        "endpoint": None,
        "icon": "bi-box-seam",
    },
    {
        "title": "Membership",
        "endpoint": None,
        "icon": "bi-person-badge",
    },
]

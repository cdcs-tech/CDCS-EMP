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
        ],
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

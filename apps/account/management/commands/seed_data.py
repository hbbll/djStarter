# apps/account/seed_data.py

permission_groups = [
    {
        "code": "auth",
        "translations": {
            "uz": "Authentikatsiya ruxsatnomalari",
            "ru": "Разрешения на аутентификацию",
            "en": "Authentication permissions",
        },
        "permissions": [
            {"permission": "view_user", "name": "User list"},
            {"permission": "view_role", "name": "Role list"},
            {
                "permission": "view_permission_group",
                "name": "Permission group list",
            },
            {"permission": "manage_user", "name": "User management"},
            {"permission": "manage_role", "name": "Role management"},
            {
                "permission": "manage_permission_group",
                "name": "Permission group management",
            },
        ],
    }
]

roles = [
    {
        "role": "admin",
        "name": "Administrator",
        "priority": 100,
        "permissions": [
            "view_user",
            "view_role",
            "view_permission_group",
            "manage_user",
            "manage_role",
            "manage_permission_group",
        ],
    },
    {
        "role": "user",
        "name": "Regular User",
        "priority": 40,
        "permissions": [
            "view_user",
            "view_role",
            "view_permission_group",
        ],
    },
    {
        "role": "guest",
        "name": "Guest User",
        "priority": 10,
        "permissions": [],
    },
]

user_roles = [
    {"email": "admin@example.com", "roles": ["admin", "user"]},
    {"email": "user@example.com", "roles": ["user"]},
    {"email": "guest@example.com", "roles": ["guest"]},
]


users = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": True,
        "is_staff": True,
        "locale": "en",
        "role": "admin",
        "is_superuser": True,
    },
    {
        "email": "user@example.com",
        "password": "user123",
        "first_name": "Regular",
        "last_name": "User",
        "is_active": True,
        "is_staff": True,
        "locale": "en",
        "role": "admin",
        "is_superuser": False,
    },
    {
        "email": "guest@example.com",
        "password": "guest123",
        "first_name": "Guest",
        "last_name": "User",
        "is_active": True,
        "is_staff": False,
        "locale": "en",
        "role": "guest",
        "is_superuser": False,
    },
]

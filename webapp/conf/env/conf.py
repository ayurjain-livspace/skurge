CONFIG = {
    "ENV": "local",
    "DJANGO_LOG_LEVEL": "INFO",
    "DEBUG": True,
    "DATABASE": {
        "HOST": "localhost",
        "USERNAME": "",
        "PASSWORD": "",
        "DB_NAME": "skurge",
        "PORT": "5432",
    },
    "ALLOWED_HOSTS": ["*"]
}

GATEWAY = {  # API Gateway config
    "HOST": "",
    "HEADERS": {
        "Authorization": "",
        "Content-Type": "application/json"
    }
}

EXTERNAL_SERVICES = {
    "GRAPHQL_SERVER": {  # Graphql server configs
        "HOST": "",
        "HEADERS": {
            "Content-Type": "application/json"
        },
        "GATEWAY": {  # API Gateway configs
            "ENABLED": False,
            "PATH": ''
        }
    },
    "EVENT_SERVICE": {  # RabbitMQ server configs
        "url": "",
        "exchange": ""
    }
}

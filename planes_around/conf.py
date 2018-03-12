# -*- coding: utf-8 -*-

# Rest API url of OpenSky service: https://opensky-network.org/apidoc/rest.html
API_URL = 'https://opensky-network.org/api/states/all'

# service for getting your location by external IP address
LOCATION_API_URL = 'http://ipinfo.io/json'

# service for getting location by it's name
BY_NAME_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={}'

# Logging settings
LOGGING = {
    "version": 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'standard': {
            'format': '[%(levelname)s] [%(asctime)s] %(filename)s:%(funcName)s:%(lineno)s : %(message)s',
        },
        'simple': {
            'format': '> %(message)s'
        },
    },

    'handlers': {
        'logfile': {
            'level': 'WARNING',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'filename': 'planes-around.log'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },

    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',

        },
        'utils': {
            'handlers': ['console', 'logfile'],
            'propagate': False,
            'level': 'WARNING'
        },
    }
}

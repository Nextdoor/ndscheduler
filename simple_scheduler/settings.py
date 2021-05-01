"""Settings to override default settings."""

import logging

#
# Override settings
#
DEBUG = True

HTTP_PORT = 8888
HTTP_ADDRESS = "0.0.0.0"

#
# Set logging level
#
logging.getLogger().setLevel(logging.DEBUG)

JOB_CLASS_PACKAGES = ["simple_scheduler.jobs"]

# Secure Cookie Hash
# SECURE_COOKIE = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
# Secure cookie age in days (decimals are supported)
# COOKIE_MAX_AGE = 1

# User authentication
#
# To enable user authentication, modify the dict below
# e.g. AUTH_CREDENTIALS = {'username': 'password'}
# The pasword must be hashed using bcrypt (e.g. htpasswd -nbB userName userPassword)
AUTH_CREDENTIALS = {
    # "user": "$2y$11$MCw3cm9Tp.8zF/hmPILW3.1hGMtP0UV8kUevfaxrzM7JzXdoyFi6.",  # Very$ecret
}

# ADMIN_USER = "user"

from split_settings.tools import include

include(
    'common.py',
    'local.py',

    scope=locals()
)
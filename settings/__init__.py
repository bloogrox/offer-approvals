try:
    from .local import *  # NOQA
    print("Using LOCAL settings")
except ImportError:
    from .prod import *  # NOQA
    print("Using PROD settings")

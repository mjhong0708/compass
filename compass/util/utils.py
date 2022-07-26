def check_installed(module):
    try:
        __import__(module)
    except ImportError:
        print("{} not found. Please install {}.".format(module, module))
        raise

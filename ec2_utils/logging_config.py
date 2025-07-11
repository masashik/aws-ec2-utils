import logging


def setup_logging(log_file=None, verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers[:]:
            root.removeHandler(handler)

    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

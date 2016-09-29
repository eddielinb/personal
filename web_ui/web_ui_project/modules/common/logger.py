import logging

LOG_FORMAT = '%(asctime)s %(name)s:%(process)d:%(levelname)s:%(message)s:%(filename)s:%(lineno)d'


def setup_logger(logger_name, log_file, log_level=logging.INFO, log_format=LOG_FORMAT, verbose=False):
    # logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)

    # handler
    if verbose:
        sh = logging.StreamHandler()
        sh.setLevel(log_level)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    fh = logging.FileHandler(
        log_file,
        "a"
    )
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

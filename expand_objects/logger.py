import os, logging
from logging.config import fileConfig

loggers = {}

class Logger():
    """
    General logger setup
    """
    def __init__(
        self,
        logging_file_name = 'logging.conf',
        logger_name = 'base_logger',
        log_file_name = 'base'):
        # Always try to fall back to console logging on errors
        logger_name = logger_name or 'root'
        try:
            logging_dir = os.path.join(
                os.environ.get('ENERGYPLUS_EXPANDOBJECTS_ROOT_DIR'),
                'logs'
            )
        except:
            logging_dir = None
        if not os.path.isdir(logging_dir) or\
        not logging_dir or\
        not logging_file_name:
            import sys
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            root.addHandler(handler)
            self.logger = root
            self.logger.warning("Error reading logging setup parameters.  "
                "Actions will only be printed to console.")
            return
        log_file_location = os.path.join(
            logging_dir,
            '{}.log'.format(log_file_name)
        )
        if not os.path.isfile(log_file_location):
            with open(log_file_location, 'w'):
                pass
        fileConfig(
            os.path.join(
                logging_dir,
                logging_file_name
            ),
            defaults = {
                "logfilename":log_file_location
            }
        )
        # prevent re-calling same logger handlers once initialized
        # also prevent bad logger name from being called
        global loggers
        try:
            if not loggers.get(logger_name):
                if logger_name in logging.root.manager.loggerDict.keys():
                    self.logger = logging.getLogger(logger_name)
                else:
                    self.logger = logging.getLogger('root')
                    self.logger.warning(
                        'Bad logger name passed (%s), continuing with only console logging',
                        logger_name
                    )
        except Exception as e:
            self.logger = logging.getLogger('root')
            self.logger.warning(
                'Logger failed to start %s, continuing with only console logging',
                logger_name
            )
            import traceback
            self.logger.warning('logger error ouput: %s', traceback.print_exc())
        return

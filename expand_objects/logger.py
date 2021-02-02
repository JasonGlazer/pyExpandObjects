import logging
import os
from pathlib import Path
from logging.config import fileConfig

loggers = {}

this_script_dir = Path(__file__).resolve()


class Logger:
    """
    General logger setup
    """

    def __init__(
            self,
            logging_file_name='logging.conf',
            logger_name=None,
            log_file_name='base'):
        # prevent re-calling same logger handlers once initialized
        # also prevent bad logger name from being called
        global loggers
        # Always try to fall back to console logging on errors
        logger_name = logger_name or 'console_logger'
        # noinspection PyBroadException
        try:
            logging_dir = str(this_script_dir.parent.parent / 'logs')
        except:  # noqa: E722
            logging_dir = None
        if not logging_dir or \
                not os.path.isdir(logging_dir) or \
                not logging_file_name:
            # If files are not set up, use console output and give warning.
            logger_name = 'console_logger'
            if not loggers.get(logger_name):
                import sys
                root = logging.getLogger()
                root.setLevel(logging.DEBUG)
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                root.addHandler(handler)
                self.logger = root
                self.logger.warning("Log file location has not been set up.  "
                                    "Actions will only be printed to console.  Create the directory"
                                    "(ENERGYPLUS_EXPANDOBJECTS_ROOT_DIR\logs) "
                                    "if you wish to have logs recorded.")
                loggers.update({logger_name : self.logger})
            else:
                self.logger = loggers[logger_name]
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
            defaults={
                "logfilename": log_file_location
            }
        )
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
                loggers.update({logger_name: self.logger})
            else:
                self.logger = loggers[logger_name]
        except Exception as e:
            self.logger = logging.getLogger('root')
            loggers.update({logger_name: self.logger})
            self.logger.warning(
                'Logger failed to start %s, continuing with only console logging, error message: %s',
                logger_name, str(e)
            )
            import traceback
            self.logger.warning('logger error ouput: %s', traceback.print_exc())
        return

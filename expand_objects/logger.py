import logging
import os
import re
from pathlib import Path
from logging.config import fileConfig

loggers = {}

this_script_path = Path(__file__).resolve()


class Logger:
    """
    General logger setup
    """

    def __init__(
            self,
            logging_file_name='logging.conf',
            logger_name='expand_objects_logger',
            log_file_name='base'):
        # prevent re-calling same logger handlers once initialized
        # also prevent bad logger name from being called
        global loggers
        # noinspection PyBroadException
        # Use a different file for testing logger
        logging_dir = str(this_script_path.parent.parent / 'logs')
        log_file_location = os.path.join(
            logging_dir,
            '{}.log'.format(log_file_name)
        )
        testing_log_file_location = os.path.join(
            logging_dir,
            '{}.log'.format('test')
        )
        for log_file in [log_file_location, testing_log_file_location]:
            if not os.path.isfile(log_file):
                with open(log_file, 'w') as f:
                    if re.match(r'.*test.log$', log_file):
                        f.write("TimeStamp, DocText, FileName, FunctionName, FunctionStatus\n")
                    else:
                        pass
        fileConfig(
            os.path.join(
                logging_dir,
                logging_file_name
            ),
            defaults={
                "base_logfilename": log_file_location,
                "testing_logfilename": testing_log_file_location
            }
        )
        # if the code fails, fall back to root logger
        try:
            # if the logger exists, use it instead of creating a new one
            if not loggers.get(logger_name):
                # if logger_name is not in the config file, default to root
                if logger_name in logging.root.manager.loggerDict.keys():
                    self.logger = logging.getLogger(logger_name)
                else:
                    self.logger = logging.getLogger('root')
                    self.logger.warning(
                        'Bad logger name passed (%s), continuing with only console logging',
                        logger_name
                    )
                # save logger to global dictionary
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
        return
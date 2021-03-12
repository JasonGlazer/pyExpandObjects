import os
import inspect
from functools import wraps

from expand_objects.logger import Logger


class BaseTest(object):

    @classmethod
    def _test_logger(cls, doc_text="General"):
        """
        Wrapper that sets class variables for csv output
        :param doc_text: section for documentation file

        :return: class variable status indicators
            doc_text: section for documentation file
            func_name: name of function called
            func_status: boolean of function return
        """
        def _test_logger_wrapper(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                func_name = func.__name__
                func_status = True
                # change func_status to false if an assertion was raised
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    self.assertEqual(e, e)
                    func_status = False
                finally:
                    self.write_logger(
                        doc_text=doc_text,
                        file_name=os.path.basename(inspect.getfile(func)),
                        func_name=func_name,
                        func_status=func_status)
                    return func(self, *args, **kwargs)
            # make output the called function for unittest to work
            _test_logger_wrapper.__wrapped__ = func
            return wrapper
        return _test_logger_wrapper

    @staticmethod
    def write_logger(doc_text, file_name, func_name, func_status, testing_logger=Logger(logger_name='testing_logger').logger):
        try:
            testing_logger.info(
                '%s,%s,%s,%s',
                doc_text,
                file_name,
                func_name,
                func_status)
        except AttributeError:
            pass

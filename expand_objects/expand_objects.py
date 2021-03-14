from expand_objects.logger import Logger


class InvalidTemplateException(Exception):
    pass


class ExpandObjects(Logger):
    """
    General class for expanding template objects.

    Attributes:
    templates: epJSON dictionary containing HVACTemplates to expand
    """

    def verify_templates(self, templates, template_type):
        if not isinstance(templates, dict):
            msg = 'Template must be a dictionary: {}'.format(templates)
            self.logger.error(msg)
            raise TypeError(msg)
        if templates and templates.get(template_type):
            templates = templates
        else:
            msg = 'An Invalid object {} was passed to {}'.format(templates, self.__class__.__name__)
            self.logger.error(msg)
            raise InvalidTemplateException(msg)
        return templates


class ExpandThermostats(ExpandObjects):
    """
    Thermostat expansion operations
    """

    def __init__(self, templates):
        super().__init__()
        self.templates = self.verify_templates(templates, template_type='HVACTemplate:Thermostat')

import abc


class AutoStorage:
    __counter = 0

    def __init__(self):
        cls = self.__class__
        prefix = cls.__name__
        index = cls.__counter
        self.storage_name = '_{}#{}'.format(prefix, index)
        cls.__counter += 1

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)


class Validate(abc.ABC, AutoStorage):
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.name = self.__class__.__name__
        super().__init__()

    def __set__(self, instance, value):
        if value is None and self.nullable:
            super().__set__(instance, value)
        else:
            if self.required and not value:
                raise ValueError('{} cannot be empty or blank in class {}'.format(
                    self.name, instance.__class__.__name__)
                )
            value = self.validate(instance, value)
            super().__set__(instance, value)

    @abc.abstractmethod
    def validate(self, instance, value):
        """Проверяет корректность значения поля в противном случае выбрасывает исключение ValueError"""


class BooleanField(Validate):
    def validate(self, instance, value):
        if not isinstance(value, bool):
            raise ValueError('{} must be a boolean in class {}'.format(self.name, instance.__class__.__name__))
        return value


class CharField(Validate):
    def validate(self, instance, value):
        if not isinstance(value, (str, bytes)):
            raise ValueError('{} must be a string in class {}'.format(self.name, instance.__class__.__name__))
        return value


class ComboField(Validate):
    def __init__(self, required=False, fields=None):
        super().__init__(required)
        self._fields = fields

    def validate(self, instance, value):
        errors = 0
        for field in self._fields:
            if not isinstance(field, Validate):
                raise ValueError('Field {} in {} class must be instance of Validate class'.format(
                    field.__class__.__name__, instance.__class__.__name__
                ))
            try:
                field.validate(instance, value)
            except ValueError:
                errors += 1
        if errors == len(self._fields):
            raise ValueError('{} has unsupported type {} in class {}'.format(
                self.name, type(value), instance.__class__.__name__
            ))
        return value


class IntegerField(Validate):
    def validate(self, instance, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError('{} must be an integer in class {}'.format(self.name, instance.__class__.__name__))
        return value


class DictionaryField(Validate):
    def validate(self, instance, value):
        if not isinstance(value, dict):
            raise ValueError('{} must be a dictionary in class {}'.format(self.name, instance.__class__.__name__))
        return value

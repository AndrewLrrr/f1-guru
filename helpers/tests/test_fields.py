import unittest

from helpers import fields


class FakeClass:
    int_field = fields.IntegerField(required=False)
    char_field = fields.CharField(required=False)
    dict_field = fields.DictionaryField(required=False)
    bool_field = fields.BooleanField(required=False)
    combo_field = fields.ComboField(required=False, fields=[fields.CharField(), fields.IntegerField()])
    req_int_field = fields.IntegerField(required=True)
    req_char_field = fields.CharField(required=True)
    req_dict_field = fields.DictionaryField(required=True)
    req_bool_field = fields.BooleanField(required=True)
    null_dict_field = fields.DictionaryField(nullable=True)

    def set_int_field(self, val):
        self.int_field = val

    def set_char_field(self, val):
        self.char_field = val

    def set_dict_field(self, val):
        self.dict_field = val

    def set_bool_field(self, val):
        self.bool_field = val

    def set_combo_field(self, val):
        self.combo_field = val

    def set_req_int_field(self, val):
        self.req_int_field = val

    def set_req_char_field(self, val):
        self.req_char_field = val

    def set_req_dict_field(self, val):
        self.req_dict_field = val

    def set_req_bool_field(self, val):
        self.req_bool_field = val

    def set_nullable_dict_field(self, val):
        self.null_dict_field = val


class TestFields(unittest.TestCase):
    fc = FakeClass()

    def test_integer_field(self):
        self.fc.set_int_field(1)
        self.assertEqual(1, self.fc.int_field)

        with self.assertRaises(ValueError) as context:
            self.fc.set_int_field('str')
        self.assertEqual('IntegerField must be an integer in class FakeClass', str(context.exception))

    def test_char_field(self):
        self.fc.set_char_field('test')
        self.assertEqual('test', self.fc.char_field)

        with self.assertRaises(ValueError) as context:
            self.fc.set_char_field(1)
        self.assertEqual('CharField must be a string in class FakeClass', str(context.exception))

    def test_dictionary_field(self):
        self.fc.set_dict_field({'key': 'val'})
        self.assertEqual({'key': 'val'}, self.fc.dict_field)

        with self.assertRaises(ValueError) as context:
            self.fc.set_dict_field(None)
        self.assertEqual('DictionaryField must be a dictionary in class FakeClass', str(context.exception))

    def test_boolean_field(self):
        self.fc.set_bool_field(True)
        self.assertEqual(True, self.fc.bool_field)

        with self.assertRaises(ValueError) as context:
            self.fc.set_bool_field(None)
        self.assertEqual('BooleanField must be a boolean in class FakeClass', str(context.exception))

    def test_combo_field(self):
        self.fc.set_combo_field(1)
        self.assertEqual(1, self.fc.bool_field)

        with self.assertRaises(ValueError) as context:
            self.fc.set_combo_field(True)
        self.assertEqual('ComboField has unsupported type <class \'bool\'> in class FakeClass', str(context.exception))

    def test_dictionary_empty_field(self):
        self.fc.set_dict_field({})
        self.assertEqual({}, self.fc.dict_field)

    def test_boolean_empty_field(self):
        self.fc.set_bool_field(False)
        self.assertEqual(False, self.fc.bool_field)

    def test_nullable_field(self):
        self.fc.set_nullable_dict_field(None)
        self.assertIsNone(self.fc.null_dict_field)

        self.fc.set_nullable_dict_field({'key2': 'val2'})
        self.assertEqual({'key2': 'val2'}, self.fc.null_dict_field)

    def test_raise_exception_if_int_value_is_required(self):
        with self.assertRaises(ValueError) as context:
            self.fc.set_req_int_field(0)
        self.assertEqual('IntegerField cannot be empty or blank in class FakeClass', str(context.exception))

    def test_raise_exception_if_char_value_is_required(self):
        with self.assertRaises(ValueError) as context:
            self.fc.set_req_char_field('')
        self.assertEqual('CharField cannot be empty or blank in class FakeClass', str(context.exception))

    def test_raise_exception_if_dict_value_is_required(self):
        with self.assertRaises(ValueError) as context:
            self.fc.set_req_dict_field({})
        self.assertEqual('DictionaryField cannot be empty or blank in class FakeClass', str(context.exception))

    def test_raise_exception_if_boolean_value_is_required(self):
        with self.assertRaises(ValueError) as context:
            self.fc.set_req_bool_field(False)
        self.assertEqual('BooleanField cannot be empty or blank in class FakeClass', str(context.exception))

    def test_can_correctly_set_more_than_one_same_type_fields(self):
        self.fc.set_char_field('test1')
        self.fc.set_req_char_field('test2')
        self.assertEqual('test1', self.fc.char_field)
        self.assertEqual('test2', self.fc.req_char_field)


if __name__ == '__main__':
    unittest.main()

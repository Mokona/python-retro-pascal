import unittest

from reinterpreted.code import Code


class Labels:
    def __init__(self, max_labels):
        self.labels = [(-1, 'ENTERED') for _ in range(max_labels + 1)]

    def add_reference(self, label_id, pc):
        value, status = self.labels[label_id]

        if status == 'ENTERED':
            # The lookup of referenced by undefined labels create a chain using
            # the code 'q' parameters. The chain will be updated when the label
            # is declared.
            self.labels[label_id] = (pc, status)

        return value

    def declare(self, label_id, label_value, code):
        chained_address, status = self.labels[label_id]
        if status == 'DEFINED':
            raise RuntimeError("Duplicated label")

        while chained_address != -1:  # Forward reference
            c = code[chained_address]
            chained_address = c.q
            c.q = label_value

        self.labels[label_id] = (label_value, 'DEFINED')


class TestLabels(unittest.TestCase):
    def test_when_first_lookup_up_undefined_label_has_address_minus_1(self):
        labels = Labels(5)
        pc = 10
        q = labels.add_reference(5, pc)
        self.assertEqual(-1, q)

    def test_the_second_lookup_up_of_undefined_label_has_previous_pc_has_address(self):
        labels = Labels(5)
        pc = 10
        q = labels.add_reference(5, pc)
        q = labels.add_reference(5, 0)
        self.assertEqual(pc, q)

    def test_lookup_of_defined_reference_gives_its_value(self):
        labels = Labels(5)
        code = [Code() for _ in range(25)]
        code[10].q = labels.add_reference(5, 10)
        labels.declare(5, 200, code)
        code[20].q = labels.add_reference(5, 20)
        self.assertEqual(200, code[20].q)

    def test_cannot_declare_a_label_twice(self):
        labels = Labels(5)
        code = [Code() for _ in range(25)]
        labels.declare(5, 200, code)
        self.assertRaises(RuntimeError, labels.declare, 5, 300, code)

    def test_defining_the_label_gives_a_list_of_code_address_to_update(self):
        labels = Labels(5)
        code = [Code() for _ in range(25)]
        code[10].q = labels.add_reference(5, 10)
        code[15].q = labels.add_reference(5, 15)
        code[20].q = labels.add_reference(5, 20)
        labels.declare(5, 100, code)
        self.assertEqual(100, code[10].q)
        self.assertEqual(100, code[15].q)
        self.assertEqual(100, code[20].q)

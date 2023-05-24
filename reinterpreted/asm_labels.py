import unittest

from reinterpreted.code import Code
from translation import string_buffer


class Labels:
    def __init__(self, max_labels):
        self.labeltab = [(-1, 'ENTERED') for _ in range(max_labels + 1)]

    def __lookup(self, pc, label_id):
        value, status = self.labeltab[label_id]

        vq = -1

        if status == 'ENTERED':
            if value == -1:
                self.labeltab[label_id] = (pc, status)
                vq = -1
            else:
                vq = value
                self.labeltab[label_id] = (pc, status)
        elif status == 'DEFINED':
            vq = value

        return vq

    def add_reference(self, line, pc):
        l_index = line.index('L')
        line = line[l_index + 1:]
        x, _ = string_buffer.parse_integer(line)

        return self.__lookup(pc, x)

    def declare(self, label_id, label_value, code):
        value, status = self.labeltab[label_id]
        if status == 'DEFINED':
            print("Duplicated label")
        else:
            if value != -1:  # Forward reference
                current, _ = self.labeltab[label_id]
                end_list = False
                while not end_list:
                    c = code[current]
                    successor = c.q
                    c.q = label_value
                    if successor == -1:
                        end_list = True
                    else:
                        current = successor

            self.labeltab[label_id] = (label_value, 'DEFINED')


class TestLabels(unittest.TestCase):
    def test_when_first_lookup_up_undefined_label_has_address_minus_1(self):
        labels = Labels(5)
        pc = 10
        q = labels.add_reference("L   5", pc)
        self.assertEqual(-1, q)

    def test_the_second_lookup_up_of_undefined_label_has_previous_pc_has_address(self):
        labels = Labels(5)
        pc = 10
        q = labels.add_reference("L   5", pc)
        q = labels.add_reference("L   5", 0)
        self.assertEqual(pc, q)

    def test_defining_the_label_gives_a_list_of_code_address_to_update(self):
        labels = Labels(5)
        code = [Code() for _ in range(25)]
        code[10].q = labels.add_reference("L   5", 10)
        code[15].q = labels.add_reference("L   5", 15)
        code[20].q = labels.add_reference("L   5", 20)
        labels.declare(5, 100, code)
        self.assertEqual(100, code[10].q)
        self.assertEqual(100, code[15].q)
        self.assertEqual(100, code[20].q)

import unittest

from translation import string_buffer

MAX_LABELS = 1550


class Labels:
    def __init__(self):
        self.labeltab = [(-1, 'ENTERED') for _ in range(MAX_LABELS + 1)]

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

    def label_search(self, pc, line):
        l_index = line.index('L')
        line = line[l_index + 1:]
        x, _ = string_buffer.parse_integer(line)

        return self.__lookup(pc, x)

    def update(self, label_id, label_value, code):
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
    def test_(self):
        pass

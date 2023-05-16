import io
import sys
import unittest
import io
import re
from io import SEEK_END, SEEK_SET

re_number = re.compile(r"\s*\d+(?:\.\d+)?")


class InputStream:
    def __init__(self, file_id, stream: io.IOBase):
        self.file_id = file_id
        self.stream = stream
        if self.stream.seekable():
            self.stream.seek(0, SEEK_END)
            self.size = self.stream.tell()
            self.stream.seek(0, SEEK_SET)
        else:
            self.size = -1
        self.index_in_line = 0
        self.current_line = ""
        self.read_line()

    def get_id(self):
        return self.file_id

    def read(self):
        if not self.eof():
            if not self.eol():
                c = self.current_line[self.index_in_line]
                self.index_in_line += 1
            else:
                c = 0
            return c
        else:
            return 0

    def eol(self):
        return self.index_in_line == len(self.current_line)

    def read_line(self):
        self.current_line = self.stream.readline().rstrip('\n\r')
        self.index_in_line = 0

    def eof(self):
        if self.stream.seekable():
            return self.stream.tell() == self.size and self.index_in_line >= len(self.current_line)
        else:
            return self.stream.closed and self.index_in_line >= len(self.current_line)

    def read_next_number(self):
        m = re_number.match(self.current_line, self.index_in_line)
        if m:
            result = m.group(0)
            self.index_in_line += len(result)
            return float(result)
        return 0


input_data = """Hello,
This is a text!
"""

input_numbers = """1 4.5 15478"""


class TestFiles(unittest.TestCase):
    def test_creates_a_file_with_an_id(self):
        stream = io.StringIO(input_data)
        f = InputStream(4, stream)
        self.assertEqual(4, f.get_id())

    def test_creates_a_file_with_an_underlying_stream_allows_reader(self):
        stream = io.StringIO(input_data)
        f = InputStream(4, stream)
        c = f.read()
        self.assertEqual(input_data[0], c)

    def test_can_detect_end_of_line(self):
        stream = io.StringIO(input_data)

        f = InputStream(6, stream)
        self.assertFalse(f.eol())
        for _ in range(6):
            f.read()
        self.assertTrue(f.eol())

    def test_can_read_until_end_of_line(self):
        stream = io.StringIO(input_data)

        f = InputStream(2, stream)
        f.read_line()
        c = f.read()
        self.assertEqual('T', c)

    def test_can_detect_end_of_file(self):
        stream = io.StringIO(input_data)

        f = InputStream(2, stream)
        self.assertFalse(f.eof())
        f.read_line()
        f.read_line()
        self.assertTrue(f.eof())

    def test_can_read_numbers(self):
        stream = io.StringIO(input_numbers)

        f = InputStream(2, stream)
        number_1 = f.read_next_number()
        self.assertEqual(1, number_1)


def main():
    f = InputStream(1, sys.stdin)
    while not f.eof():
        print(f.current_line)
        f.read_line()


if __name__ == '__main__':
    main()

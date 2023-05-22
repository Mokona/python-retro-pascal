import unittest


def parse_integer(input_string):
    stripped_string = input_string.lstrip()
    if stripped_string and stripped_string[0].isdigit():
        i = 0
        while i < len(stripped_string) and stripped_string[i].isdigit():
            i += 1
        integer = int(stripped_string[:i])
        return integer, stripped_string[i:]
    else:
        return None, input_string


def parse_real(input_string):
    i, line = parse_integer(input_string)
    if len(line) > 0 and line[0] == '.':
        d, line = parse_integer(line[1:])
        return float(f"{i}.{d}"), line
    return i, line


def parse_char(input_string):
    stripped_string = input_string.lstrip()
    if stripped_string:
        return stripped_string[0], stripped_string[1:]
    else:
        return None, input_string


class TestParsingFunctions(unittest.TestCase):
    def test_parse_integer(self):
        self.assertEqual(parse_integer("123 one two"), (123, " one two"))
        self.assertEqual(parse_integer("  456   "), (456, "   "))
        self.assertEqual(parse_integer("  789"), (789, ""))
        self.assertEqual(parse_integer("baz three"), (None, "baz three"))
        self.assertEqual(parse_integer(""), (None, ""))

    def test_parse_real(self):
        self.assertEqual(parse_real("2.3 one two"), (2.3, " one two"))
        self.assertEqual(parse_real("2 one two"), (2, " one two"))

    def test_parse_non_blank_char(self):
        self.assertEqual(parse_char("  a   bc"), ('a', "   bc"))
        self.assertEqual(parse_char("   \t \n  x  "), ('x', "  "))
        self.assertEqual(parse_char("  \t \n  "), (None, "  \t \n  "))
        self.assertEqual(parse_char(""), (None, ""))

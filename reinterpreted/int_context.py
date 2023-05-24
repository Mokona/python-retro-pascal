import unittest

from reinterpreted.store import Store, TestStore


class Context:
    def __init__(self, input_stream, output_stream, input_file, output_file, store):
        self.pc = 0
        self.mp = 0  # Beginning of Data segment
        self.sp = -1  # Top of Stack
        self.np = store.stack_size + 1  # Start of the dynamically allocated area (going down)

        self.files = [input_stream, output_stream, input_file, output_file]
        self.store = store

        self.running = True

    def push(self, value):
        self.sp += 1
        if self.sp > self.np:
            raise RuntimeError("Store Overflow")
        self.store[self.sp] = value

    def pop(self) -> (str, any):
        value = self.store[self.sp]
        self.sp -= 1
        return value


class TestContext(unittest.TestCase):
    def test_can_push_value_to_context(self):
        store = Store(TestStore.MockStoreConfiguration())
        context = Context(None, None, None, None, store)
        typed_value = 'INT', 123
        context.push(typed_value)

        self.assertEqual(typed_value, store[0])

    def test_can_push_and_pop_values_to_context(self):
        store = Store(TestStore.MockStoreConfiguration())
        context = Context(None, None, None, None, store)
        typed_value_1 = 'INT', 123
        typed_value_2 = 'INT', 321
        context.push(typed_value_1)
        context.push(typed_value_2)
        context.push(typed_value_1)

        self.assertEqual(typed_value_1, context.pop())
        self.assertEqual(typed_value_2, context.pop())
        self.assertEqual(typed_value_1, context.pop())

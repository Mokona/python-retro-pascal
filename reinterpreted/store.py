""" The Store, as per P2 naming, is the data memory space. """
import unittest

"""The Store Layout from the lowest addresses:
- 0..MAXSTK is the Stack
- MAXSTK+1..OVERI is the Integer Constant Table, pointed by ICP
- MAXSTK+1..OVERI is the Integer Constant Table, pointed by ICP
"""


class StoreConfiguration:
    maximum_stack_size = 20_000
    integer_const_table_size = 5
    real_const_table_size = 5
    set_const_table_size = 70
    boundary_const_table_size = 4
    multiple_const_table_size = 1300


class Pointers:
    def __init__(self, configuration: StoreConfiguration):
        self.integer_const_table_address = configuration.maximum_stack_size + 1
        self.real_const_table_address = self.integer_const_table_address + configuration.integer_const_table_size
        self.set_const_table_address = self.real_const_table_address + configuration.real_const_table_size
        self.boundary_const_table_address = self.set_const_table_address + configuration.set_const_table_size
        self.multiple_const_table_address = self.boundary_const_table_address + configuration.boundary_const_table_size
        self.highest_address = self.multiple_const_table_address + self.multiple_const_table_address + 1

        self.integer_table_range = (self.integer_const_table_address, self.real_const_table_address)
        self.real_table_range = (self.real_const_table_address, self.set_const_table_address)
        self.set_table_range = (self.set_const_table_address, self.boundary_const_table_address)
        self.boundary_table_range = (self.boundary_const_table_address, self.multiple_const_table_address)
        self.multiple_table_range = (self.multiple_const_table_address, self.highest_address)

        self.int_const_ptr: int = self.integer_const_table_address
        self.real_const_ptr: int = self.real_const_table_address
        self.set_const_ptr: int = self.set_const_table_address
        self.boundary_const_ptr: int = self.boundary_const_table_address
        self.multiple_const_ptr: int = self.multiple_const_table_address


class Store:
    def __init__(self, configuration: StoreConfiguration):
        # The store consists of tuples of (Type, Value)

        self.pointers = Pointers(configuration)
        self.store: list[tuple] = [('UNDEF', None) for _ in range(self.pointers.highest_address)]

        for i in range(*self.pointers.integer_table_range):
            self.store[i] = ('INT', 0)
        for i in range(*self.pointers.real_table_range):
            self.store[i] = ('REEL', 0.0)
        for i in range(*self.pointers.set_table_range):
            self.store[i] = ('SETT', set())
        for i in range(*self.pointers.boundary_table_range):
            self.store[i] = ('INT', 0)
        for i in range(*self.pointers.multiple_table_range):
            self.store[i] = ('INT', 0)

    def __setitem__(self, pc, instruction):
        self.store[pc] = instruction

    def __getitem__(self, pc):
        return self.store[pc]

    # Pointer and store_ramge are related. Could make a type out of it
    def __add_value_in_range(self, typed_value, pointer, store_range):
        self.store[pointer] = typed_value

        range_begin, range_end = store_range
        index = self.store[range_begin:range_end].index(typed_value)
        address = index + range_begin
        if address == pointer:
            pointer += 1
            if pointer == range_end:
                raise MemoryError()
        return address, pointer

    def add_int_constant(self, int_value) -> int:
        try:
            address, pointer = self.__add_value_in_range(('INT', int_value),
                                                         self.pointers.int_const_ptr,
                                                         self.pointers.integer_table_range)
        except MemoryError:
            raise RuntimeError("Integer table overflow")
        self.pointers.int_const_ptr = pointer
        return address

    def add_real_constant(self, real_value) -> int:
        try:
            address, pointer = self.__add_value_in_range(('REEL', real_value),
                                                         self.pointers.real_const_ptr,
                                                         self.pointers.real_table_range)
        except MemoryError:
            raise RuntimeError("Real table overflow")
        self.pointers.real_const_ptr = pointer
        return address


class TestStore(unittest.TestCase):
    class MockStoreConfiguration(StoreConfiguration):
        maximum_stack_size = 100
        integer_const_table_size = 3
        real_const_table_size = 3
        set_const_table_size = 10
        boundary_const_table_size = 4
        multiple_const_table_size = 100

    def test_a_typed_value_can_be_added_at_an_address(self):
        store = Store(self.MockStoreConfiguration())
        store[0] = 'INT', 4

        self.assertEqual(('INT', 4), store[0])

    def test_store_constant_tables_are_initialized_to_their_types(self):
        store = Store(self.MockStoreConfiguration())
        self.assertEqual('INT', store[store.pointers.integer_const_table_address][0])
        self.assertEqual('REEL', store[store.pointers.real_const_table_address][0])
        self.assertEqual('SETT', store[store.pointers.set_const_table_address][0])
        self.assertEqual('INT', store[store.pointers.boundary_const_table_address][0])
        self.assertEqual('INT', store[store.pointers.multiple_const_table_address][0])

    def test_a_integer_constant_can_be_added_to_store(self):
        store = Store(self.MockStoreConfiguration())
        q = store.add_int_constant(10)

        constant_address = store.pointers.integer_const_table_address
        self.assertEqual(10, store[constant_address][1])
        self.assertEqual(constant_address, q)

    def test_raises_if_too_many_int_const_added(self):
        mock_configuration = self.MockStoreConfiguration()
        store = Store(mock_configuration)
        for i in range(mock_configuration.integer_const_table_size - 1):
            store.add_int_constant(10 + i)
        self.assertRaises(RuntimeError, store.add_int_constant, 5)

    def test_a_real_constant_can_be_added_to_store(self):
        store = Store(self.MockStoreConfiguration())
        q = store.add_real_constant(10.0)

        constant_address = store.pointers.real_const_table_address
        self.assertEqual(10.0, store[constant_address][1])
        self.assertEqual(constant_address, q)

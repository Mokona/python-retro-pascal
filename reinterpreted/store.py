""" The Store, as per P2 naming, is the data memory space. """
import unittest


class StoreConfiguration:
    maximum_stack_size = 20_000
    integer_const_table_size = 5
    real_const_table_size = 5
    set_const_table_size = 70
    boundary_const_table_size = 4
    multiple_const_table_size = 1300


class RangedPointer:
    def __init__(self, begin, end):
        self.pointer = begin
        self.begin = begin
        self.end = end

    def increment_or_fail(self):
        self.pointer += 1
        if self.pointer == self.end:
            raise MemoryError()

    def get_range(self):
        return range(self.begin, self.end)


class Pointers:
    def __init__(self, configuration: StoreConfiguration):
        integer_const_table_address = configuration.maximum_stack_size + 1
        real_const_table_address = integer_const_table_address + configuration.integer_const_table_size
        set_const_table_address = real_const_table_address + configuration.real_const_table_size
        boundary_const_table_address = set_const_table_address + configuration.set_const_table_size
        multiple_const_table_address = boundary_const_table_address + configuration.boundary_const_table_size

        self.highest_address = multiple_const_table_address + multiple_const_table_address + 1

        self.int_ranged_ptr = RangedPointer(integer_const_table_address, real_const_table_address)
        self.real_ranged_ptr = RangedPointer(real_const_table_address, set_const_table_address)
        self.set_ranged_ptr = RangedPointer(set_const_table_address, boundary_const_table_address)
        self.boundary_ranged_ptr = RangedPointer(boundary_const_table_address, multiple_const_table_address)
        self.multiple_ranged_ptr = RangedPointer(multiple_const_table_address, self.highest_address)


class Store:
    def __init__(self, configuration: StoreConfiguration):
        # The store consists of tuples of (Type, Value)
        # Types are : INT (VI), REEL (VR), BOOL (VB), SETT (VS), ADR (VA), MARK (VM), UNDEF

        self.pointers = Pointers(configuration)
        self.store: list[tuple] = [('UNDEF', None) for _ in range(self.pointers.highest_address)]
        self.stack_size = configuration.maximum_stack_size
        self.highest_address = self.pointers.highest_address

        for i in self.pointers.int_ranged_ptr.get_range():
            self.store[i] = ('INT', 0)
        for i in self.pointers.real_ranged_ptr.get_range():
            self.store[i] = ('REEL', 0.0)
        for i in self.pointers.set_ranged_ptr.get_range():
            self.store[i] = ('SETT', set())
        for i in self.pointers.boundary_ranged_ptr.get_range():
            self.store[i] = ('INT', 0)
        for i in self.pointers.multiple_ranged_ptr.get_range():
            self.store[i] = ('INT', 0)

    def __setitem__(self, address, instruction):
        self.store[address] = instruction

    def __getitem__(self, address):
        return self.store[address]

    def get_value(self, address):
        return self.__getitem__(address)[1]

    def get_type(self, address):
        return self.__getitem__(address)[0]

    def __add_value_in_range(self, typed_value, ranged_ptr: RangedPointer):
        self.store[ranged_ptr.pointer] = typed_value

        index = self.store[ranged_ptr.begin:ranged_ptr.end].index(typed_value)

        address = index + ranged_ptr.begin
        if address == ranged_ptr.pointer:
            ranged_ptr.increment_or_fail()
        return address

    def add_int_constant(self, int_value) -> int:
        try:
            return self.__add_value_in_range(('INT', int_value), self.pointers.int_ranged_ptr)
        except MemoryError:
            raise RuntimeError("Integer table overflow")

    def add_real_constant(self, real_value) -> int:
        try:
            return self.__add_value_in_range(('REEL', real_value), self.pointers.real_ranged_ptr)
        except MemoryError:
            raise RuntimeError("Real table overflow")

    def add_set_constant(self, set_value) -> int:
        try:
            return self.__add_value_in_range(('SET', set_value), self.pointers.set_ranged_ptr)
        except MemoryError:
            raise RuntimeError("Set table overflow")

    def add_boundary_constant(self, boundary_value: tuple[int, int]) -> int:
        lower_bound, upper_bound = boundary_value
        typed_lower_bound = ('INT', lower_bound)
        typed_upper_bound = ('INT', upper_bound)

        ranged_ptr = self.pointers.boundary_ranged_ptr
        self.store[ranged_ptr.pointer] = typed_lower_bound
        self.store[ranged_ptr.pointer + 1] = typed_upper_bound

        address = None
        for ptr in range(ranged_ptr.begin, ranged_ptr.end):
            if self.store[ptr] == typed_lower_bound and self.store[ptr + 1] == typed_upper_bound:
                address = ptr
                break
        assert (address is not None)

        if address == ranged_ptr.pointer:
            try:
                ranged_ptr.increment_or_fail()
                ranged_ptr.increment_or_fail()  # Boundary takes two places
            except MemoryError:
                raise RuntimeError("Boundary table overflow")
        return address + 1  # The pointed address is on the upper bound

    def add_multiple_constant(self, value_list: list) -> int:
        ranged_ptr = self.pointers.multiple_ranged_ptr

        address = ranged_ptr.pointer
        if address + len(value_list) >= ranged_ptr.end:
            raise RuntimeError("Multiple table overflow")

        for ptr, value in zip(range(ranged_ptr.pointer, ranged_ptr.end), value_list):
            self.store[ptr] = 'INT', value

        ranged_ptr.pointer += len(value_list)

        return address


class TestStore(unittest.TestCase):
    class MockStoreConfiguration(StoreConfiguration):
        maximum_stack_size = 100
        integer_const_table_size = 3
        real_const_table_size = 3
        set_const_table_size = 10
        boundary_const_table_size = 4
        multiple_const_table_size = 10

    def test_a_typed_value_can_be_added_at_an_address(self):
        store = Store(self.MockStoreConfiguration())
        store[0] = 'INT', 4

        self.assertEqual(('INT', 4), store[0])
        self.assertEqual(4, store.get_value(0))
        self.assertEqual('INT', store.get_type(0))

    def test_store_constant_tables_are_initialized_to_their_types(self):
        store = Store(self.MockStoreConfiguration())
        self.assertEqual('INT', store[store.pointers.int_ranged_ptr.begin][0])
        self.assertEqual('REEL', store[store.pointers.real_ranged_ptr.begin][0])
        self.assertEqual('SETT', store[store.pointers.set_ranged_ptr.begin][0])
        self.assertEqual('INT', store[store.pointers.boundary_ranged_ptr.begin][0])
        self.assertEqual('INT', store[store.pointers.multiple_ranged_ptr.begin][0])

    def test_a_integer_constant_can_be_added_to_store(self):
        store = Store(self.MockStoreConfiguration())
        q = store.add_int_constant(10)

        constant_address = store.pointers.int_ranged_ptr.begin
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

        constant_address = store.pointers.real_ranged_ptr.begin
        self.assertEqual(10.0, store[constant_address][1])
        self.assertEqual(constant_address, q)

    def test_a_set_constant_can_be_added_to_store(self):
        store = Store(self.MockStoreConfiguration())
        q = store.add_set_constant({1, 2, 3})

        constant_address = store.pointers.set_ranged_ptr.begin
        self.assertEqual({1, 2, 3}, store[constant_address][1])
        self.assertEqual(constant_address, q)

    def test_a_boundary_constant_can_be_added_to_store(self):
        store = Store(self.MockStoreConfiguration())
        q = store.add_boundary_constant((1, 5))

        constant_address = store.pointers.boundary_ranged_ptr.begin
        self.assertEqual(1, store[constant_address][1])
        self.assertEqual(5, store[constant_address + 1][1])
        self.assertEqual(constant_address + 1, q)  # The pointed address is the upper bound

    def test_a_multiple_constant_can_be_added_to_store(self):
        store = Store(self.MockStoreConfiguration())
        q = store.add_multiple_constant([10, 20, 30])

        constant_address = store.pointers.multiple_ranged_ptr.begin
        self.assertEqual(10, store[constant_address][1])
        self.assertEqual(20, store[constant_address + 1][1])
        self.assertEqual(30, store[constant_address + 2][1])
        self.assertEqual(constant_address, q)

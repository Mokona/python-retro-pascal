class Context:
    def __init__(self, input_stream, output_stream, input_file, output_file, store):
        self.pc = 0
        self.mp = 0  # Beginning of Data segment
        self.sp = -1  # Top of Stack
        self.np = store.stack_size + 1  # Start of the dynamically allocated area (going down)

        self.files = [input_stream, output_stream, input_file, output_file]
        self.store = store

        self.running = True

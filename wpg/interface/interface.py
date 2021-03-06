import os

from wpg.engine.engine import Engine
from wpg.interface.color import Color
from wpg.interface.menu import Menu


class Interface:
    def __init__(self, initial_file=None, used_keys_path=None):

        self.engine = Engine()
        self.show_instructions = True
        self.current_menu = None

        # Declare Menus.
        self.menu_main = None
        self.menu_editor = None
        self.menu_generator = None
        self.menu_data = None

        # Initialize Commands.
        self.all_commands = []
        self.initialize_commands()

        if initial_file is not None:
            self.cmd_load_db([initial_file])

        if used_keys_path is not None:
            self.engine.load_used_keys(used_keys_path)

    # ==================================================================================================================
    # Initialize
    # ==================================================================================================================

    def initialize_commands(self):
        self.initialize_main_menu()
        self.initialize_data_menu()
        self.initialize_editor_menu()
        self.initialize_generator_menu()

        self.all_commands = []
        all_menus = [self.menu_main, self.menu_editor, self.menu_data, self.menu_generator]
        for menu in all_menus:
            for command in menu.commands:
                self.all_commands.append(command)
        self.current_menu = self.menu_main

    def initialize_main_menu(self):
        self.menu_main = Menu("Main Menu", "Word Engine Main Menu.")
        self.menu_main.add_command(
            key="data",
            desc_text="Load, save and import databases.",
            action=self.cmd_go_to_data
        )
        self.menu_main.add_command(
            key="editor",
            desc_text="Add, remove, and verify words in the database.",
            action=self.cmd_go_to_editor
        )
        self.menu_main.add_command(
            key="generator",
            desc_text="Go to the generator mode, where you can create new puzzles.",
            action=self.cmd_go_to_generator
        )
        self.menu_main.add_command(
            key="exit",
            desc_text="Exit this program.",
            action=self.cmd_exit
        )

    def initialize_data_menu(self):
        self.menu_data = Menu("Data Menu", "Import, save, and export word databases.")
        self.menu_data.add_command(
            key="load_db",
            desc_text="Load a database for editing.",
            usage_text="$ [file_path]",
            action=self.cmd_load_db
        )
        self.menu_data.add_command(
            key="load_txt",
            desc_text="Create a new database from a text file.",
            usage_text="$ [file_path] [min_letters] [max_letters] [strict (1 or 0)]",
            action=self.cmd_load_txt
        )
        self.menu_data.add_command(
            key="merge_txt",
            desc_text="Merges the words in a text file to this database. Strict mode will exclude any words that "
                      "start with an uppercase, or contains non alphabetical characters.",
            usage_text="$ [file_path] [min_letters] [max_letters] [strict (1 or 0)]",
            action=self.cmd_merge_txt
        )
        self.menu_data.add_command(
            key="split",
            desc_text="Splits the given dictionary (txt) file into multiple smaller files.",
            usage_text="$ [min_letters] [max_letters]",
            action=self.cmd_split_txt
        )
        self.menu_data.add_command(
            key="info",
            desc_text="Get the stats and information about the currently loaded database.",
            action=self.cmd_info
        )
        self.menu_data.add_command(
            key="save",
            desc_text="Save the database.",
            action=self.cmd_save
        )
        self.menu_data.add_command(
            key="back",
            desc_text="Return to the main menu.",
            action=self.cmd_go_to_main_menu
        )

    def initialize_editor_menu(self):
        self.menu_editor = Menu("Editor Menu", "Edit, add, remove, verify words.")
        self.menu_editor.add_command(
            key="add",
            desc_text="Add the word(s) to the database.",
            usage_text="$ [word]",
            action=self.cmd_add,
        )
        self.menu_editor.add_command(
            key="remove",
            desc_text="Remove the word(s) from the database.",
            usage_text="$ [word]",
            action=self.cmd_remove
        )
        self.menu_editor.add_command(
            key="hide",
            desc_text="Add the word(s) to the database, and set them to hidden.",
            usage_text="$ [word]",
            action=self.cmd_hide
        )
        self.menu_editor.add_command(
            key="verify",
            desc_text="Enter the verification mode.",
            action=self.cmd_verify
        )
        self.menu_editor.add_command(
            key="back",
            desc_text="Return to the main menu.",
            action=self.cmd_go_to_main_menu
        )
        self.menu_editor.add_command(
            key="batch",
            desc_text="Enter the batch verification mode.",
            action=self.cmd_batch_verify
        )

    def initialize_generator_menu(self):
        self.menu_generator = Menu("Generator Menu", "Generate and test word puzzles.")
        self.menu_generator.add_command(
            key="generate",
            desc_text="Generate a set of puzzles into an output folder.",
            action=self.cmd_generate
        )
        self.menu_generator.add_command(
            key="single",
            desc_text="Generate a single puzzle for the given letters.",
            action=self.cmd_single,
            usage_text="$ [num_of_letters] [num_of_puzzles]"
        )
        self.menu_generator.add_command(
            key="inspect",
            desc_text="Inspect a word for anagrams.",
            action=self.cmd_inspect,
            usage_text="$ [word]"
        )
        self.menu_generator.add_command(
            key="back",
            desc_text="Return to the main menu.",
            action=self.cmd_go_to_main_menu
        )

    # ==================================================================================================================
    # Virtual Machine Loop
    # ==================================================================================================================

    def run(self):
        while True:
            self.run_select_mode()

    def show_header(self):
        print("Word Puzzle Engine {}".format(Color.set_green(str(self.engine.version))))
        print("Loaded Database: {}".format(Color.set_green(str(self.engine.db_path))))
        print("Current Mode: {}".format(Color.set_green(self.current_menu.name)))
        print("--------------------------------------")
        print

    @staticmethod
    def clear_terminal():
        os.system("clear || cls")

    @staticmethod
    def show_command(command):
        print(Color.set_yellow(command.usage_text.replace("$", command.key)))
        print(command.desc_text)
        print

    def show_menu(self, menu):
        for command in menu.commands:
            self.show_command(command)

    def run_select_mode(self):
        print
        if self.show_instructions:
            self.clear_terminal()
            self.show_header()
            self.show_menu(self.current_menu)
            self.show_instructions = False

        code = raw_input(Color.set_green("Enter Command: "))
        print

        key, args = self.read_input_string(code)
        self.execute_input_command(key, args)

    @staticmethod
    def read_input_string(input_string):
        input_array = input_string.split(" ")
        input_key = input_array[0].lower()
        if len(input_array) > 1:
            input_args = input_array[1:]
            return input_key, input_args
        else:
            return input_key, None

    def execute_input_command(self, key, args):
        command_found = False
        for command in self.all_commands:
            if key == command.key:
                # Valid action found.
                command_found = True
                self.execute_command_with_args(command, args)

        # No action found
        if not command_found:
            print("Invalid command: '{}' not recognized.".format(key))

    @staticmethod
    def execute_command_with_args(command, args):
        if command.action is None:
            print("Command has no action.")
            return

        if command.has_args:
            if args is None:
                print("You must supply some input arguments.")
                print(command.usage_text)
            else:
                command.action(args)
        else:
            command.action()

    # ==================================================================================================================
    # Menu Commands
    # ==================================================================================================================

    def _go_to_menu(self, menu):
        self.current_menu = menu
        self.show_instructions = True

    def cmd_go_to_data(self):
        self._go_to_menu(self.menu_data)

    def cmd_go_to_editor(self):
        self._go_to_menu(self.menu_editor)

    def cmd_go_to_generator(self):
        self._go_to_menu(self.menu_generator)

    def cmd_go_to_main_menu(self):
        self._go_to_menu(self.menu_main)

    def cmd_exit(self):
        self.cmd_save()
        self.clear_terminal()
        exit(1)

    # ==================================================================================================================
    # Data Commands
    # ==================================================================================================================

    def cmd_load_db(self, args):
        file_path = args[0]
        self.engine.load_db(file_path)
        self.show_instructions = True

    def cmd_load_txt(self, args):
        file_name, min_letters, max_letters, strict = self._get_txt_load_arguments(args)
        self.engine.load_txt(file_name, strict=strict, min_count=min_letters, max_count=max_letters)
        self.show_instructions = True

    def cmd_merge_txt(self, args):
        file_name, min_letters, max_letters, strict = self._get_txt_load_arguments(args)
        self.engine.merge_txt(file_name, strict=strict, min_count=min_letters, max_count=max_letters)

    def cmd_split_txt(self, args):
        file_name, max_units, min_letters, max_letters = self._get_txt_split_arguments(args)
        self.engine.split_txt(file_name, max_units=max_units, min_count=min_letters, max_count=max_letters)

    def cmd_save(self):
        self.engine.save()

    def cmd_info(self):
        self.engine.print_info()

    @staticmethod
    def _get_txt_load_arguments(args):

        min_letters = 0
        max_letters = 8
        strict = True
        file_name = args[0]

        if len(args) > 1:
            min_letters = int(args[1])

        if len(args) > 2:
            max_letters = int(args[2])

        if len(args) > 3:
            strict = bool(int(args[3]))

        print("Loading File: {}".format(file_name))
        print("Min Letters: {}".format(min_letters))
        print("Max Letters: {}".format(max_letters))
        print("Strict Mode: {}".format(strict))
        print("")

        return file_name, min_letters, max_letters, strict

    @staticmethod
    def _get_txt_split_arguments(args):

        max_units = 2000
        min_letters = 2
        max_letters = 8
        file_name = args[0]

        if len(args) > 1:
            min_letters = int(args[1])

        if len(args) > 2:
            max_letters = int(args[2])

        print("Splitting File: {}".format(file_name))
        print("Units Per: {}".format(max_units))
        print("Min Letters: {}".format(min_letters))
        print("Max Letters: {}".format(max_letters))
        print("")

        return file_name, max_units, min_letters, max_letters

    # ==================================================================================================================
    # Editor Commands
    # ==================================================================================================================

    def cmd_add(self, args):
        self.engine.add(args)

    def cmd_remove(self, args):
        self.engine.remove(args)

    def cmd_hide(self, args):
        self.engine.hide(args)

    def cmd_verify(self):
        self.clear_terminal()
        self.engine.verify()
        self.clear_terminal()
        self.show_instructions = True

    def cmd_batch_verify(self):
        self.clear_terminal()
        self.engine.verify(True)
        self.clear_terminal()
        self.show_instructions = True

    # ==================================================================================================================
    # Generator Commands
    # ==================================================================================================================

    def cmd_single(self, args):
        n = int(args[0])
        t = 1
        if len(args) > 1:
            t = int(args[1])

        for i in range(t):
            self.engine.generate_single(n)

    def cmd_inspect(self, args):
        word = args[0]
        self.engine.inspect(word)

    def cmd_generate(self):
        self.engine.generate()

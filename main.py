from datetime import datetime, timedelta
import pickle
import sys
from collections import UserDict


class Iterrable:
    def __init__(self, some_object, per_page):
        self.some_object = some_object
        self.current = 0
        self.per_page = per_page
        self.keys = list(self.some_object.keys())
        self.acc = []

    def __next__(self):
        if self.current < len(self.some_object):
            while True:
                res = self.some_object[self.keys[self.current]]
                self.acc.append(res)
                self.current += 1

                if self.current % self.per_page == 0 or self.current >= len(
                    self.some_object
                ):
                    res = self.acc
                    self.acc = []
                    return res

        raise StopIteration


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass
    # реалізація класу


class Phone(Field):
    # реалізація класу
    def __init__(self, phone):
        if len(str(phone)) != 10 or not phone.isdigit():
            raise ValueError(f"{phone} not correct format")
        super().__init__(str(phone))


class Birthday(Field):
    def __init__(self, birthday=None):
        super().__init__(birthday)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу
    def find_phone(self, phone, strict=False):
        for phone_el in self.phones:
            if phone in phone_el.value:
                return phone_el
        return None
        # raise ValueError(f"{phone} not found")

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for_remove = self.find_phone(phone)
        if for_remove:
            self.phones.remove(for_remove)

    def edit_phone(self, phone, new_phone):
        phone_el = self.find_phone(phone)
        if not phone_el:
            raise ValueError(f"{phone} not found")
        phone_el.value = new_phone

    # @birthday.setter
    def set_birthday(self, birthday):
        if not birthday:
            self.birthday = Birthday(birthday)
            return

        try:
            datetime.strptime(birthday, "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Birthday {birthday} invalid format")
            raise ValueError(e)
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            cur_date = datetime.now().date()
            delta_date = (self.birthday.replace(year=cur_date.year) - cur_date).days
            if delta_date < 0:
                delta_date = (
                    self.birthday.replace(year=cur_date.year + 1) - cur_date
                ).days
            return delta_date

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    # реалізація класу

    def __init__(self, filename="address_book.bin"):
        UserDict.__init__(self)
        self.filename = filename
        try:
            self.load()
        except BaseException as e:
            print(f"!!!!! not file, Error: {e}")

    def find(self, string, strict=False):
        res = {}
        for key, value in self.data.items():
            string = string if strict else string.lower()
            name_value = value.name.value if strict else value.name.value.lower()

            if strict and (string == name_value or value.find_phone(string, True)):
                return value

            if not strict and (string in name_value or value.find_phone(string)):
                res[key] = value

        if strict:
            return ""
        return res

    def add_record(self, record):
        print(f"add_record: {record}")
        self.data[record.name.value] = record

    def delete(self, name):
        for el in self.data.values():
            if el.name.value == name:
                self.data.__delitem__(name)
                break

    def save(self):
        with open(self.filename, "wb") as fh:
            pickle.dump(self.data, fh)
        return self.data

    def load(self):
        try:
            with open(self.filename, "rb") as fh:
                res = pickle.load(fh)
                self.data = res
                return res
        except BaseException as e:
            print("load Error")

    def __iter__(self):
        return Iterrable(self.data, 3)

    def __str__(self):
        res = ""
        for e in self.data.values():
            res += f"{e}\n"
        return res


book = AddressBook()


# DECORATOR input_error
def input_error(func):
    # two params - name, phone
    # You didn't provide a phone number
    # You did not enter your name and phone number

    one_params = ["find", "del", "birthday"]

    def wraper(*args):
        result = None
        try:
            is_need_one_params = func.__name__ in one_params
            len_args = len(args[0])

            if is_need_one_params and len_args < 1:
                raise ValueError("Give me name please")
            elif not is_need_one_params and len_args < 2:
                raise ValueError("Give me name and phone please")

            result = func(*args)

        except ValueError as e:
            print(f"------- ValueError: {e}")

        except KeyError as e:
            print(f"------- keyerror: {e}")

        except IndexError as e:
            print(f"------- IndexError: {e}")

        except Exception as e:
            print("------ EXCEPTION - Exception {e}")
            # tb = sys.exc_info()

        return result

    return wraper


def handler_find(string):
    find_string, *tail = string
    print(f"find_string: {find_string}")
    return book.find(find_string)


def handler_hello(*args):
    print("How can I help you?")
    return


@input_error
def handler_add(*args):
    name, phone = args[0]
    new_contact = Record(name)  # .add_phone(phone)
    new_contact.add_phone(phone)
    find_contact = book.find(name)
    if len(find_contact) > 0:
        raise ValueError(f"Name: {name} already exists.")
    book.add_record(new_contact)
    return new_contact


def handler_del(*args):
    name, *any = args[0]
    book.delete(name)


@input_error
def handler_add_phone(*args):
    print(f"args: {args}")
    name, phone, *any = args[0]

    find_name = book.find(name, True)
    if find_name == "":
        raise ValueError(f"Name: {name} there is no such.")

    find_name.add_phone(phone)


@input_error
def handler_edit_phone(*args):
    name, phone, new_phone = args[0]

    find_name = book.find(name, True)
    if find_name == "":
        raise ValueError(f"Name: {name} there is no such.")

    find_name.edit_phone(phone, new_phone)

    return f"{name} {phone}"


@input_error
def handler_remove_phone(*args):
    name, phone, *any = args[0]

    find_name = book.find(name, True)
    if find_name == "":
        raise ValueError(f"Name: {name} there is no such.")

    find_name.remove_phone(phone)


@input_error
def handler_set_birthday(*args):
    name, birthday, *any = args[0]

    find_record = book.find(name, True)
    find_record.set_birthday(birthday)


# @input_error
def handler_show_all(*args):
    return book


def handler_save(*args):
    return book.save()


def handler_load(*args):
    return book.load()


# @input_error
def handler_end_program(*args):
    print("Good bye!")
    sys.exit()


command_list = {
    "hello": handler_hello,
    "add": handler_add,  # add new contact: Name Phone
    "del": handler_del,  # del contact: Name
    "add phone": handler_add_phone,  # added phone to contact: Name phone
    "edit phone": handler_edit_phone,  # change phone: Name OldPhone NewPhone
    "remove phone": handler_remove_phone,  # del phone in contact: Name phone
    "birthday": handler_set_birthday,  # set birthday to contact: Name date_birthday
    "show all": handler_show_all,
    "find": handler_find,  # find name or phone
    "save": handler_save,  # save Addressbook
    "load": handler_load,  # load Addressbook
    "good bye": handler_end_program,
    "close": handler_end_program,
    "exit": handler_end_program,
    "quit": handler_end_program,
}


def command_parse(string):
    string_lower = string.lower().strip()
    f_list = string_lower.split()
    f_list1 = f_list[0]
    f_list2 = " ".join(f_list[0:2])

    command_find = list(
        filter(
            lambda key: string_lower.startswith(key)
            and (f_list1 == key or f_list2 == key),
            command_list.keys(),
        )
    )

    if len(command_find) == 0:
        print("command not found")
        return

    command_current = command_list[command_find[0]]
    command_parameters = string.replace(command_find[0], "").strip().split()
    res = command_current(command_parameters)
    return res


while True:
    command_input = input("Input command: ")

    if command_input == "":
        continue
    res = command_parse(command_input)
    print(res)

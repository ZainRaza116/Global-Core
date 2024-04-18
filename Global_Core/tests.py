class ListOperations:
    def __init__(self):
        self.list_data = []

    def insert(self, item):
        self.list_data.append(item)
        print("Item inserted successfully.")

    def delete(self, item):
        try:
            self.list_data.remove(item)
            print("Item deleted successfully.")
        except ValueError:
            print("Item not found in the list.")

    def search(self, item):
        if item in self.list_data:
            print("Item found in the list.")
        else:
            print("Item not found in the list.")

    def update(self, old_item, new_item):
        try:
            index = self.list_data.index(old_item)
            self.list_data[index] = new_item
            print("Item updated successfully.")
        except ValueError:
            print("Item not found in the list.")

    def find_max_min(self):
        if self.list_data:
            max_item = max(self.list_data)
            min_item = min(self.list_data)
            print("Maximum element:", max_item)
            print("Minimum element:", min_item)
        else:
            print("List is empty.")

    def reverse_list(self):
        self.list_data.reverse()
        print("List reversed successfully.")

    def sort_list(self):
        self.list_data.sort()
        print("List sorted successfully.")

    def display(self):
        print("Current state of the list:", self.list_data)


class TupleManipulation:
    def __init__(self):
        self.tuple_data = ()

    def create_tuple(self, *args):
        self.tuple_data = args
        print("Tuple created successfully.")

    def access_element(self, index):
        try:
            return self.tuple_data[index]
        except IndexError:
            print("Index out of range.")

    def concatenate_tuples(self, tuple2):
        return self.tuple_data + tuple2

    def repeat_tuple(self, n):
        return self.tuple_data * n

    def iterate_through(self):
        for item in self.tuple_data:
            print(item)

    def display(self):
        print("Current state of the tuple:", self.tuple_data)


class DictionaryFunctions:
    def __init__(self):
        self.dictionary_data = {}

    def create_dictionary(self, data):
        self.dictionary_data = data
        print("Dictionary created successfully.")

    def read_value(self, key):
        try:
            print("Value corresponding to key", key, ":", self.dictionary_data[key])
        except KeyError:
            print("Key not found in the dictionary.")

    def update_value(self, key, value):
        self.dictionary_data[key] = value
        print("Value updated successfully.")

    def delete_key(self, key):
        try:
            del self.dictionary_data[key]
            print("Key deleted successfully.")
        except KeyError:
            print("Key not found in the dictionary.")

    def merge_dictionaries(self, dict2):
        self.dictionary_data.update(dict2)
        print("Dictionaries merged successfully.")

    def display(self):
        print("Current state of the dictionary:", self.dictionary_data)


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def insert_beginning(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        print("Element inserted at the beginning.")

    def insert_end(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node
        print("Element inserted at the end.")

    def insert_at_position(self, position, data):
        if position < 0:
            print("Invalid position.")
            return
        if position == 0:
            self.insert_beginning(data)
            return
        new_node = Node(data)
        current_node = self.head
        for _ in range(position - 1):
            if current_node.next:
                current_node = current_node.next
            else:
                print("Invalid position.")
                return
        new_node.next = current_node.next
        current_node.next = new_node
        print("Element inserted at position", position)

    def display(self):
        current_node = self.head
        while current_node:
            print(current_node.data, end=" -> ")
            current_node = current_node.next
        print("None")


class SetOperations:
    def __init__(self):
        self.set_data = set()

    def create_set(self, data):
        self.set_data = set(data)
        print("Set created successfully.")

    def union(self, set2):
        return self.set_data.union(set2)

    def intersection(self, set2):
        return self.set_data.intersection(set2)

    def difference(self, set2):
        return self.set_data.difference(set2)

    def symmetric_difference(self, set2):
        return self.set_data.symmetric_difference(set2)

    def is_subset(self, set2):
        return self.set_data.issubset(set2)

    def is_superset(self, set2):
        return self.set_data.issuperset(set2)

    def add_element(self, element):
        self.set_data.add(element)
        print("Element added to the set.")

    def remove_element(self, element):
        try:
            self.set_data.remove(element)
            print("Element removed from the set.")
        except KeyError:
            print("Element not found in the set.")

    def display(self):
        print("Current state of the set:", self.set_data)


# Example usage:
def main():
    while True:
        print("\nMenu:")
        print("1. List Operations")
        print("2. Tuple Manipulation")
        print("3. Dictionary Functions")
        print("4. Linked List Implementation")
        print("5. Set Operations")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            # List Operations
            list_ops = ListOperations()
            while True:
                print("\nList Operations Menu:")
                print("1. Insert")
                print("2. Delete")
                print("3. Search")
                print("4. Update")
                print("5. Find Max and Min")
                print("6. Reverse List")
                print("7. Sort List")
                print("8. Display")
                print("9. Go back to main menu")

                list_choice = input("Enter your choice: ")

                if list_choice == '1':
                    try:
                        item = int(input("Enter item to insert: "))
                        list_ops.insert(item)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif list_choice == '2':
                    try:
                        item = int(input("Enter item to delete: "))
                        list_ops.delete(item)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif list_choice == '3':
                    try:
                        item = int(input("Enter item to search: "))
                        list_ops.search(item)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif list_choice == '4':
                    try:
                        old_item = int(input("Enter item to update: "))
                        new_item = int(input("Enter new item: "))
                        list_ops.update(old_item, new_item)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif list_choice == '5':
                    list_ops.find_max_min()
                elif list_choice == '6':
                    list_ops.reverse_list()
                elif list_choice == '7':
                    list_ops.sort_list()
                elif list_choice == '8':
                    list_ops.display()
                elif list_choice == '9':
                    break
                else:
                    print("Invalid choice. Please try again.")

        elif choice == '2':
            # Tuple Manipulation
            tuple_ops = TupleManipulation()
            while True:
                print("\nTuple Manipulation Menu:")
                print("1. Create Tuple")
                print("2. Access Element")
                print("3. Concatenate Tuples")
                print("4. Repeat Tuple")
                print("5. Iterate Through")
                print("6. Display")
                print("7. Go back to main menu")

                tuple_choice = input("Enter your choice: ")

                if tuple_choice == '1':
                    try:
                        items = input("Enter items separated by commas: ").split(',')
                        tuple_ops.create_tuple(*items)
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif tuple_choice == '2':
                    try:
                        index = int(input("Enter index to access: "))
                        print("Element at index:", tuple_ops.access_element(index))
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif tuple_choice == '3':
                    try:
                        tuple2 = tuple(input("Enter tuple elements separated by commas: ").split(','))
                        print("Concatenated tuple:", tuple_ops.concatenate_tuples(tuple2))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif tuple_choice == '4':
                    try:
                        n = int(input("Enter repetition count: "))
                        print("Repeated tuple:", tuple_ops.repeat_tuple(n))
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif tuple_choice == '5':
                    tuple_ops.iterate_through()
                elif tuple_choice == '6':
                    tuple_ops.display()
                elif tuple_choice == '7':
                    break
                else:
                    print("Invalid choice. Please try again.")

        elif choice == '3':
            # Dictionary Functions
            dict_ops = DictionaryFunctions()
            while True:
                print("\nDictionary Functions Menu:")
                print("1. Create Dictionary")
                print("2. Read Value")
                print("3. Update Value")
                print("4. Delete Key")
                print("5. Merge Dictionaries")
                print("6. Display")
                print("7. Go back to main menu")

                dict_choice = input("Enter your choice: ")

                if dict_choice == '1':
                    try:
                        num_items = int(input("Enter the number of key-value pairs: "))
                        data = {}
                        for _ in range(num_items):
                            key, value = input("Enter key-value pair separated by a colon (key:value): ").split(':')
                            data[key] = int(value)
                        dict_ops.create_dictionary(data)
                    except ValueError:
                        print("Invalid input format. Please enter a valid integer.")
                elif dict_choice == '2':
                    key = input("Enter key to read: ")
                    dict_ops.read_value(key)

                elif dict_choice == '3':
                    try:
                        key = input("Enter key to update: ")
                        value = int(input("Enter new value: "))
                        dict_ops.update_value(key, value)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif dict_choice == '4':
                    key = input("Enter key to delete: ")
                    dict_ops.delete_key(key)

                elif dict_choice == '5':
                    try:
                        num_items = int(input("Enter the number of key-value pairs to merge: "))
                        dict2 = {}
                        for _ in range(num_items):
                            key, value = input("Enter key-value pair separated by a colon (key:value): ").split(':')
                            dict2[key] = int(value)
                        dict_ops.merge_dictionaries(dict2)
                    except ValueError:
                        print("Invalid input format. Please enter a valid integer.")
                elif dict_choice == '6':
                    dict_ops.display()
                elif dict_choice == '7':
                    break
                else:
                    print("Invalid choice. Please try again.")

        elif choice == '4':
            # Linked List Implementation
            linked_list = LinkedList()
            while True:
                print("\nLinked List Implementation Menu:")
                print("1. Insert at Beginning")
                print("2. Insert at End")
                print("3. Insert at Position")
                print("6. Display")
                print("7. Go back to main menu")

                ll_choice = input("Enter your choice: ")

                if ll_choice == '1':
                    try:
                        data = int(input("Enter data to insert at the beginning: "))
                        linked_list.insert_beginning(data)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif ll_choice == '2':
                    try:
                        data = int(input("Enter data to insert at the end: "))
                        linked_list.insert_end(data)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif ll_choice == '3':
                    try:
                        position = int(input("Enter position to insert: "))
                        data = int(input("Enter data to insert: "))
                        linked_list.insert_at_position(position, data)
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
                elif ll_choice == '6':
                    linked_list.display()
                elif ll_choice == '7':
                    break
                else:
                    print("Invalid choice. Please try again.")

        elif choice == '5':
            # Set Operations
            set_ops = SetOperations()
            while True:
                print("\nSet Operations Menu:")
                print("1. Create Set")
                print("2. Union")
                print("3. Intersection")
                print("4. Difference")
                print("5. Symmetric Difference")
                print("6. Is Subset")
                print("7. Is Superset")
                print("8. Add Element")
                print("9. Remove Element")
                print("10. Display")
                print("11. Go back to main menu")

                set_choice = input("Enter your choice: ")

                if set_choice == '1':
                    try:
                        elements = input("Enter elements separated by commas: ").split(',')
                        set_ops.create_set(elements)
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '2':
                    try:
                        elements = input("Enter elements of second set separated by commas: ").split(',')
                        print("Union:", set_ops.union(set(elements)))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '3':
                    try:
                        elements = input("Enter elements of second set separated by commas: ").split(',')
                        print("Intersection:", set_ops.intersection(set(elements)))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '4':
                    try:
                        elements = input("Enter elements of second set separated by commas: ").split(',')
                        print("Difference:", set_ops.difference(set(elements)))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '5':
                    try:
                        elements = input("Enter elements of second set separated by commas: ").split(',')
                        print("Symmetric Difference:", set_ops.symmetric_difference(set(elements)))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '6':
                    try:
                        elements = input("Enter elements of second set separated by commas: ").split(',')
                        print("Is Subset:", set_ops.is_subset(set(elements)))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '7':
                    try:
                        elements = input("Enter elements of second set separated by commas: ").split(',')
                        print("Is Superset:", set_ops.is_superset(set(elements)))
                    except ValueError:
                        print("Invalid input. Please enter valid elements.")
                elif set_choice == '8':
                    element = input("Enter element to add: ")
                    set_ops.add_element(element)
                elif set_choice == '9':
                    element = input("Enter element to remove: ")
                    set_ops.remove_element(element)
                elif set_choice == '10':
                    set_ops.display()
                elif set_choice == '11':
                    break
                else:
                    print("Invalid choice. Please try again.")

        elif choice == '6':
            print("Exiting the program...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
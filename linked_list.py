class Node:
    def __init__(self, data=None, next_node=None):
        self.data = data
        self.next_node = next_node

class LinkedList:
    def __init__(self):
        self.head = None
        self.last_node = None

    def to_list(self):
        lst = []
        if self.head is None:
            return lst

        node = self.head
        while node:
            lst.append(node.data)
            node = node.next_node
        return lst

    def print_linked_list(self):
        """
        Visual representation of linked list
        """
        linked_list_string = ""
        node = self.head
        if node is None:
            print(None)
        while node:
            linked_list_string += f" {str(node.data)} ->"
            node = node.next_node

        linked_list_string += " None"
        print(linked_list_string)

    def insert_beginning(self, data):
        if self.head is None:
            self.head = Node(data, None)
            self.last_node  = self.head
    
        new_node = Node(data, self.head)
        self.head = new_node

    def insert_at_end(self, data):
        if self.head is None:
            self.insert_beginning(data)

        self.last_node.next_node = Node(data, None)
        self.last_node = self.last_node.next_node

    def get_user_by_id(self, user_id):
        node = self.head
        while node:
            if node.data["id"] is int(user_id):
                return node.data
            node = node.next_node
        return None

        




# ll = LinkedList()
# ll.insert_beginning("initial node")
# ll.insert_beginning("new beginning")
# ll.insert_beginning("very new beginning")
# ll.insert_at_end("end")
# ll.print_linked_list()
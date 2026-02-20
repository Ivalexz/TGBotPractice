class UsersTask:
    def __init__(self, name, description, status):
        self.name=name
        self.description=description
        self.status=status

    def show_task(self):
        print(f"Назва: {self.name}")
        print(f"Опис: {self.description}")
        print(f"Статус: {self.status}")
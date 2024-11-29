class Student:
    def __init__(self, id, name, class_id, date_joined, phone, parent_phone):
        self.id = id
        self.name = name
        self.class_id = class_id
        self.date_joined = date_joined
        self.phone = phone
        self.parent_phone = parent_phone

    def to_dict(self):
        """Converts the student object to a dictionary for rendering in HTML."""
        return {
            'id': self.id,
            'name': self.name,
            'class_id': self.class_id,
            'date_joined': self.date_joined,
            'phone': self.phone,
            'parent_phone': self.parent_phone,
        }

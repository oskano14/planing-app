class course:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.ects = data["ects"]
        self.type = data["type"]
        self.weekly_hours = data["weekly_hours"]
        self.expected_students = data["expected_students"]
        self.semester = data["semester"]
        self.required_equipment = data["required_equipment"]
        self.prerequisites = data["prerequisites"]
        self.incompatible_courses = data["incompatible_courses"]


class teacher:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.specialties = data["specialties"]
        self.can_teach = data["can_teach"]
        self.max_hours = data["max_hours_per_week"]
        self.unavailable_slots = data["unavailable_slots"]
        self.preferred_slots = data["preferred_slots"]


class room:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.capacity = data["capacity"]
        self.type = data["type"]
        self.equipment = data["equipment"]
        self.building = data["building"]
        self.floor = data["floor"]


class timeslot:
    def __init__(self, data):
        self.id = data["id"]
        self.day = data["day"]
        self.start = data["start"]
        self.end = data["end"]
        self.duration = data["duration"]
        self.category = data["category"]


class group:
    def __init__(self, data):
        self.id = data["id"]
        self.size = data["size"]
        self.semester = data["semester"]
        self.courses = data["courses"]
        self.preferences = data["preferences"]

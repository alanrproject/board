class Project:
    def __init__(self, id, name, code, fecha_inicio, retie_status, or_status):
        self.id = id
        self.name = name
        self.code = code
        self.fecha_inicio = fecha_inicio
        self.retie_status = retie_status
        self.or_status = or_status

class ProjectTask:
    def __init__(self, project_id, project_name, start_date, end_date, notes):
        self.project_id = project_id
        self.project_name = project_name
        self.start_date = start_date
        self.end_date = end_date
        self.notes = notes


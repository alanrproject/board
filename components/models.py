class Project:
    def __init__(self, id, nombre, estado, fecha_inicio, fecha_fin):
        self.id = id
        self.nombre = nombre
        self.estado = estado
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

class ProjectTask:
    def __init__(self, project_id, project_name, start_date, end_date, notes):
        self.project_id = project_id
        self.project_name = project_name
        self.start_date = start_date
        self.end_date = end_date
        self.notes = notes


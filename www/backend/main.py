from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import os, dotenv

dotenv.load_dotenv()
app = Flask(__name__)
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Materia(db.Model):
    __tablename__ = 'materias'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    creditos = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    matricula = db.Column(db.String(9), unique=True, nullable=False)
    carrera = db.Column(db.String(100), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)

    @property
    def email(self):
        return f"A{self.matricula}@my.uvm.edu.mx"

class Calificacion(db.Model):
    __tablename__ = 'calificaciones'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id', ondelete='CASCADE'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)
    calificacion = db.Column(db.Numeric(4,2), nullable=True)

    __table_args__ = (
        UniqueConstraint('estudiante_id', 'materia_id', 'semestre', name='uq_est_materia_sem'),
    )

class Horario(db.Model):
    __tablename__ = 'horario'
    id = db.Column(db.Integer, primary_key=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)
    grupo = db.Column(db.String(20))
    dia = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    aula = db.Column(db.String(50))

def resp_ok(data=None, message="", code=200):
    return jsonify({
        "code": code,
        "status": "success" if 200 <= code < 300 else "fail",
        "data": data or {},
        "message": message
    }), code

def resp_fail(message, code=400):
    status = "fail" if 400 <= code < 500 else "error"
    return jsonify({
        "code": code,
        "status": status,
        "data": {},
        "message": message
    }), code

# Endpoint de autenticación
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    matricula = data.get('matricula')
    if not matricula:
        return resp_fail("Se requiere 'matricula' en el cuerpo", 400)
    estudiante = Estudiante.query.filter_by(matricula=matricula).first()
    if not estudiante:
        return resp_fail("Matrícula no encontrada", 401)
    estudiante_data = {
        "id": estudiante.id,
        "nombre": estudiante.nombre,
        "matricula": estudiante.matricula,
        "carrera": estudiante.carrera,
        "semestre": estudiante.semestre,
        "email": estudiante.email
    }
    return resp_ok(data=estudiante_data, message="Inicio de sesión correcto", code=200)

@app.route('/estudiantes', methods=['GET'])
def listar_estudiantes():
    estudiantes = Estudiante.query.all()
    data = []
    for e in estudiantes:
        data.append({
            "id": e.id,
            "nombre": e.nombre,
            "matricula": e.matricula,
            "carrera": e.carrera,
            "semestre": e.semestre,
            "email": e.email
        })
    return resp_ok(data=data)

@app.route('/estudiantes/<int:id>', methods=['GET'])
def obtener_estudiante(id):
    e = Estudiante.query.get(id)
    if not e:
        return resp_fail("Estudiante no encontrado", 404)
    data = {
        "id": e.id,
        "nombre": e.nombre,
        "matricula": e.matricula,
        "carrera": e.carrera,
        "semestre": e.semestre,
        "email": e.email
    }
    return resp_ok(data=data)

@app.route('/estudiantes', methods=['POST'])
def crear_estudiante():
    payload = request.get_json() or {}
    nombre = payload.get('nombre')
    matricula = payload.get('matricula')
    carrera = payload.get('carrera')
    semestre = payload.get('semestre')
    if not all([nombre, matricula, carrera, semestre]):
        return resp_fail("Faltan campos obligatorios: nombre, matricula, carrera, semestre", 400)
    import re
    if not re.match(r'^660[0-9]{6}$', matricula):
        return resp_fail("Matrícula inválida. Debe empezar por 660 y tener 9 dígitos.", 400)
    try:
        estudiante = Estudiante(nombre=nombre, matricula=matricula, carrera=carrera, semestre=int(semestre))
        db.session.add(estudiante)
        db.session.commit()
        data = {
            "id": estudiante.id,
            "nombre": estudiante.nombre,
            "matricula": estudiante.matricula,
            "carrera": estudiante.carrera,
            "semestre": estudiante.semestre,
            "email": estudiante.email
        }
        return resp_ok(data=data, message="Estudiante creado", code=201)
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al crear estudiante: {str(ex)}", 500)

@app.route('/estudiantes/<int:id>', methods=['PUT'])
def actualizar_estudiante(id):
    e = Estudiante.query.get(id)
    if not e:
        return resp_fail("Estudiante no encontrado", 404)
    payload = request.get_json() or {}
    e.nombre = payload.get('nombre', e.nombre)
    if 'matricula' in payload:
        import re
        if not re.match(r'^660[0-9]{6}$', payload['matricula']):
            return resp_fail("Matrícula inválida", 400)
        e.matricula = payload['matricula']
    e.carrera = payload.get('carrera', e.carrera)
    if 'semestre' in payload:
        e.semestre = int(payload['semestre'])
    try:
        db.session.commit()
        return resp_ok(data={
            "id": e.id,
            "nombre": e.nombre,
            "matricula": e.matricula,
            "carrera": e.carrera,
            "semestre": e.semestre,
            "email": e.email
        }, message="Estudiante actualizado")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al actualizar estudiante: {str(ex)}", 500)

@app.route('/estudiantes/<int:id>', methods=['DELETE'])
def borrar_estudiante(id):
    e = Estudiante.query.get(id)
    if not e:
        return resp_fail("Estudiante no encontrado", 404)
    try:
        db.session.delete(e)
        db.session.commit()
        return resp_ok(message="Estudiante eliminado")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al eliminar: {str(ex)}", 500)

@app.route('/materias', methods=['GET'])
def listar_materias():
    materias = Materia.query.all()
    data = [{"id": m.id, "codigo": m.codigo, "nombre": m.nombre, "creditos": m.creditos, "descripcion": m.descripcion} for m in materias]
    return resp_ok(data=data)

@app.route('/materias/<int:id>', methods=['GET'])
def obtener_materia(id):
    m = Materia.query.get(id)
    if not m:
        return resp_fail("Materia no encontrada", 404)
    data = {"id": m.id, "codigo": m.codigo, "nombre": m.nombre, "creditos": m.creditos, "descripcion": m.descripcion}
    return resp_ok(data=data)

@app.route('/materias', methods=['POST'])
def crear_materia():
    payload = request.get_json() or {}
    if not payload.get('codigo') or not payload.get('nombre') or payload.get('creditos') is None:
        return resp_fail("Faltan campos: codigo, nombre, creditos", 400)
    try:
        m = Materia(codigo=payload['codigo'], nombre=payload['nombre'], creditos=int(payload['creditos']), descripcion=payload.get('descripcion'))
        db.session.add(m)
        db.session.commit()
        return resp_ok(data={"id": m.id, "codigo": m.codigo, "nombre": m.nombre}, message="Materia creada", code=201)
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al crear materia: {str(ex)}", 500)

@app.route('/materias/<int:id>', methods=['PUT'])
def actualizar_materia(id):
    m = Materia.query.get(id)
    if not m:
        return resp_fail("Materia no encontrada", 404)
    p = request.get_json() or {}
    m.codigo = p.get('codigo', m.codigo)
    m.nombre = p.get('nombre', m.nombre)
    if 'creditos' in p:
        m.creditos = int(p['creditos'])
    m.descripcion = p.get('descripcion', m.descripcion)
    try:
        db.session.commit()
        return resp_ok(data={"id": m.id, "codigo": m.codigo, "nombre": m.nombre}, message="Materia actualizada")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al actualizar materia: {str(ex)}", 500)

@app.route('/materias/<int:id>', methods=['DELETE'])
def borrar_materia(id):
    m = Materia.query.get(id)
    if not m:
        return resp_fail("Materia no encontrada", 404)
    try:
        db.session.delete(m)
        db.session.commit()
        return resp_ok(message="Materia eliminada")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al eliminar materia: {str(ex)}", 500)

@app.route('/calificaciones', methods=['GET'])
def listar_calificaciones():
    q = Calificacion.query
    estudiante_id = request.args.get('estudiante_id')
    materia_id = request.args.get('materia_id')
    semestre = request.args.get('semestre')
    if estudiante_id:
        q = q.filter_by(estudiante_id=int(estudiante_id))
    if materia_id:
        q = q.filter_by(materia_id=int(materia_id))
    if semestre:
        q = q.filter_by(semestre=semestre)
    items = q.all()
    data = []
    for it in items:
        data.append({
            "id": it.id,
            "estudiante_id": it.estudiante_id,
            "materia_id": it.materia_id,
            "semestre": it.semestre,
            "calificacion": float(it.calificacion) if it.calificacion is not None else None
        })
    return resp_ok(data=data)

@app.route('/calificaciones/<int:id>', methods=['GET'])
def obtener_calificacion(id):
    it = Calificacion.query.get(id)
    if not it:
        return resp_fail("Registro no encontrado", 404)
    data = {
        "id": it.id,
        "estudiante_id": it.estudiante_id,
        "materia_id": it.materia_id,
        "semestre": it.semestre,
        "calificacion": float(it.calificacion) if it.calificacion is not None else None
    }
    return resp_ok(data=data)

@app.route('/calificaciones', methods=['POST'])
def crear_calificacion():
    p = request.get_json() or {}
    try:
        estudiante_id = int(p['estudiante_id'])
        materia_id = int(p['materia_id'])
        semestre = p['semestre']
    except Exception:
        return resp_fail("Campos obligatorios: estudiante_id, materia_id, semestre", 400)
    cal = p.get('calificacion')
    try:
        new = Calificacion(estudiante_id=estudiante_id, materia_id=materia_id, semestre=semestre,
                           calificacion=(float(cal) if cal is not None else None))
        db.session.add(new)
        db.session.commit()
        return resp_ok(data={"id": new.id}, message="Registro creado", code=201)
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al crear registro: {str(ex)}", 500)

@app.route('/calificaciones/<int:id>', methods=['PUT'])
def actualizar_calificacion(id):
    it = Calificacion.query.get(id)
    if not it:
        return resp_fail("Registro no encontrado", 404)
    p = request.get_json() or {}
    if 'calificacion' in p:
        it.calificacion = float(p['calificacion']) if p['calificacion'] is not None else None
    if 'semestre' in p:
        it.semestre = p['semestre']
    try:
        db.session.commit()
        return resp_ok(message="Registro actualizado")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al actualizar: {str(ex)}", 500)

@app.route('/calificaciones/<int:id>', methods=['DELETE'])
def borrar_calificacion(id):
    it = Calificacion.query.get(id)
    if not it:
        return resp_fail("Registro no encontrado", 404)
    try:
        db.session.delete(it)
        db.session.commit()
        return resp_ok(message="Registro eliminado")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al eliminar: {str(ex)}", 500)


@app.route('/horario', methods=['GET'])
def listar_horario():
    q = Horario.query
    materia_id = request.args.get('materia_id')
    semestre = request.args.get('semestre')
    estudiante_id = request.args.get('estudiante_id')
    # si pasan estudiante_id, devolvemos horario de las materias en las que está inscrito en el semestre dado
    if estudiante_id:
        # obtener materias inscritas para el semestre (si se pasa)
        semestre_filter = request.args.get('semestre')
        cal_q = Calificacion.query.filter_by(estudiante_id=int(estudiante_id))
        if semestre_filter:
            cal_q = cal_q.filter_by(semestre=semestre_filter)
        materia_ids = [c.materia_id for c in cal_q.all()]
        q = q.filter(Horario.materia_id.in_(materia_ids))
        if semestre_filter:
            q = q.filter_by(semestre=semestre_filter)
    if materia_id:
        q = q.filter_by(materia_id=int(materia_id))
    if semestre:
        q = q.filter_by(semestre=semestre)
    items = q.all()
    data = []
    for h in items:
        data.append({
            "id": h.id,
            "materia_id": h.materia_id,
            "semestre": h.semestre,
            "grupo": h.grupo,
            "dia": h.dia,
            "hora_inicio": h.hora_inicio.strftime('%H:%M:%S'),
            "hora_fin": h.hora_fin.strftime('%H:%M:%S'),
            "aula": h.aula
        })
    return resp_ok(data=data)

@app.route('/horario/<int:id>', methods=['GET'])
def obtener_horario(id):
    h = Horario.query.get(id)
    if not h:
        return resp_fail("Registro de horario no encontrado", 404)
    data = {
        "id": h.id,
        "materia_id": h.materia_id,
        "semestre": h.semestre,
        "grupo": h.grupo,
        "dia": h.dia,
        "hora_inicio": h.hora_inicio.strftime('%H:%M:%S'),
        "hora_fin": h.hora_fin.strftime('%H:%M:%S'),
        "aula": h.aula
    }
    return resp_ok(data=data)

@app.route('/horario', methods=['POST'])
def crear_horario():
    p = request.get_json() or {}
    required = ['materia_id','semestre','dia','hora_inicio','hora_fin']
    if not all(k in p for k in required):
        return resp_fail(f"Faltan campos. Requeridos: {required}", 400)
    try:
        h = Horario(
            materia_id=int(p['materia_id']),
            semestre=p['semestre'],
            grupo=p.get('grupo'),
            dia=p['dia'],
            hora_inicio=p['hora_inicio'],
            hora_fin=p['hora_fin'],
            aula=p.get('aula')
        )
        db.session.add(h)
        db.session.commit()
        return resp_ok(data={"id": h.id}, message="Horario creado", code=201)
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al crear horario: {str(ex)}", 500)

@app.route('/horario/<int:id>', methods=['PUT'])
def actualizar_horario(id):
    h = Horario.query.get(id)
    if not h:
        return resp_fail("Registro de horario no encontrado", 404)
    p = request.get_json() or {}
    if 'materia_id' in p:
        h.materia_id = int(p['materia_id'])
    h.semestre = p.get('semestre', h.semestre)
    h.grupo = p.get('grupo', h.grupo)
    h.dia = p.get('dia', h.dia)
    if 'hora_inicio' in p:
        h.hora_inicio = p['hora_inicio']
    if 'hora_fin' in p:
        h.hora_fin = p['hora_fin']
    h.aula = p.get('aula', h.aula)
    try:
        db.session.commit()
        return resp_ok(message="Horario actualizado")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al actualizar horario: {str(ex)}", 500)

@app.route('/horario/<int:id>', methods=['DELETE'])
def borrar_horario(id):
    h = Horario.query.get(id)
    if not h:
        return resp_fail("Registro no encontrado", 404)
    try:
        db.session.delete(h)
        db.session.commit()
        return resp_ok(message="Horario eliminado")
    except Exception as ex:
        db.session.rollback()
        return resp_fail(f"Error al eliminar horario: {str(ex)}", 500)

# ---------- Endpoint util: ver materias y horario por alumno ----------
@app.route('/estudiantes/<int:estudiante_id>/materias', methods=['GET'])
def materias_por_estudiante(estudiante_id):
    semestre = request.args.get('semestre')  # opcional
    q = Calificacion.query.filter_by(estudiante_id=estudiante_id)
    if semestre:
        q = q.filter_by(semestre=semestre)
    inscripciones = q.all()
    data = []
    for ins in inscripciones:
        m = Materia.query.get(ins.materia_id)
        # buscar horario para esa materia y semestre (si se pasa)
        horarios_q = Horario.query.filter_by(materia_id=m.id)
        if semestre:
            horarios_q = horarios_q.filter_by(semestre=semestre)
        horarios = [{
            "dia": h.dia,
            "hora_inicio": h.hora_inicio.strftime('%H:%M:%S'),
            "hora_fin": h.hora_fin.strftime('%H:%M:%S'),
            "aula": h.aula,
            "grupo": h.grupo,
            "semestre": h.semestre
        } for h in horarios_q.all()]
        data.append({
            "materia": {"id": m.id, "codigo": m.codigo, "nombre": m.nombre, "creditos": m.creditos},
            "semestre": ins.semestre,
            "calificacion": float(ins.calificacion) if ins.calificacion is not None else None,
            "horarios": horarios
        })
    return resp_ok(data=data)

# ---------- Inicialización ----------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

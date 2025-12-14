# Database Tables — gestion_estudiantes

This file summarizes all database tables defined in `backend/bd.sql` (schema: `gestion_estudiantes`). It lists columns, types, nullability, constraints and foreign keys.

---

## Table: materias
- Purpose: Catalog of subjects/courses.
- Engine: InnoDB

Columns:
- `id` — INT, AUTO_INCREMENT, PRIMARY KEY
- `codigo` — VARCHAR(10), NOT NULL, UNIQUE
- `nombre` — VARCHAR(150), NOT NULL
- `creditos` — TINYINT, NOT NULL
- `descripcion` — TEXT, NULLABLE
- `created_at` — TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

Constraints / Indexes:
- UNIQUE (`codigo`)

Sample seed rows (from `bd.sql`):
- ('MATE101', 'Calculo I', 6)
- ('FISI101', 'Fisica I', 6)
- ('PROG101', 'Programacion I', 8)

---

## Table: estudiantes
- Purpose: Student records.
- Engine: InnoDB

Columns:
- `id` — INT, AUTO_INCREMENT, PRIMARY KEY
- `nombre` — VARCHAR(150), NOT NULL
- `matricula` — CHAR(9), NOT NULL, UNIQUE
- `carrera` — VARCHAR(100), NOT NULL
- `semestre` — TINYINT, NOT NULL
- `email` — VARCHAR(100), GENERATED COLUMN AS (CONCAT('A', matricula, '@my.uvm.edu.mx')) STORED
- `created_at` — TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

Constraints / Indexes:
- UNIQUE (`matricula`)
- CHECK `chk_matricula_format`: `matricula` REGEXP '^660[0-9]{6}$'

Sample seed rows (from `bd.sql`):
- ('Maria Gonzalez', '660123456', 'Ingenieria en Sistemas', 1)
- ('Jorge Ramirez', '660234567', 'Ingenieria Industrial', 3)
- ('Ana Lopez', '660345678', 'Arquitectura', 2)

---

## Table: calificaciones
- Purpose: Student enrollments and grades.
- Engine: InnoDB

Columns:
- `id` — INT, AUTO_INCREMENT, PRIMARY KEY
- `estudiante_id` — INT, NOT NULL — FK -> `estudiantes(id)` ON DELETE CASCADE
- `materia_id` — INT, NOT NULL — FK -> `materias(id)` ON DELETE CASCADE
- `semestre` — VARCHAR(10), NOT NULL
- `calificacion` — DECIMAL(4,2), NULLABLE
- `fecha_registro` — TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

Constraints / Indexes:
- FOREIGN KEY (`estudiante_id`) REFERENCES `estudiantes`(`id`) ON DELETE CASCADE
- FOREIGN KEY (`materia_id`) REFERENCES `materias`(`id`) ON DELETE CASCADE
- UNIQUE KEY `uq_est_materia_sem` (`estudiante_id`, `materia_id`, `semestre`)

Sample seed rows (examples from `bd.sql`):
- (estudiante: '660123456', materia: 'MATE101', semestre: '2025-1', calificacion: NULL)
- (estudiante: '660123456', materia: 'PROG101', semestre: '2024-2', calificacion: 9.20)

---

## Table: horario
- Purpose: Course schedule entries.
- Engine: InnoDB

Columns:
- `id` — INT, AUTO_INCREMENT, PRIMARY KEY
- `materia_id` — INT, NOT NULL — FK -> `materias(id)` ON DELETE CASCADE
- `semestre` — VARCHAR(10), NOT NULL
- `grupo` — VARCHAR(20), NULLABLE
- `dia` — ENUM('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado'), NOT NULL
- `hora_inicio` — TIME, NOT NULL
- `hora_fin` — TIME, NOT NULL
- `aula` — VARCHAR(50), NULLABLE
- `created_at` — TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

Constraints / Indexes:
- FOREIGN KEY (`materia_id`) REFERENCES `materias`(`id`) ON DELETE CASCADE

Sample seed rows (from `bd.sql`):
- materia 'MATE101', semestre '2025-1', grupo 'A', dia 'Lunes', 08:00-10:00, 'Aula 101'
- materia 'PROG101', semestre '2025-1', grupo 'A', dia 'Jueves', 14:00-17:00, 'Lab Computo 1'

---

## Notes
- The SQL file `backend/bd.sql` contains the full CREATE TABLE statements and seed INSERTs used to populate example data. This markdown is a concise extraction of that schema.
- The application code (`backend/main.py`) maps these tables to SQLAlchemy models (`Materia`, `Estudiante`, `Calificacion`, `Horario`) and implements CRUD endpoints.


DROP DATABASE IF EXISTS gestion_estudiantes;
CREATE DATABASE gestion_estudiantes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gestion_estudiantes;

CREATE TABLE materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    creditos TINYINT NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    matricula CHAR(9) NOT NULL UNIQUE,
    carrera VARCHAR(100) NOT NULL,
    semestre TINYINT NOT NULL,
    email VARCHAR(100) AS (CONCAT('A', matricula, '@my.uvm.edu.mx')) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_matricula_format CHECK (matricula REGEXP '^660[0-9]{6}$')
) ENGINE=InnoDB;

CREATE TABLE calificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT NOT NULL,
    materia_id INT NOT NULL,
    semestre VARCHAR(10) NOT NULL,
    calificacion DECIMAL(4,2) NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE,
    UNIQUE KEY uq_est_materia_sem (estudiante_id, materia_id, semestre)
) ENGINE=InnoDB;

CREATE TABLE horario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    materia_id INT NOT NULL,
    semestre VARCHAR(10) NOT NULL,
    grupo VARCHAR(20),
    dia ENUM('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    aula VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO materias (codigo, nombre, creditos, descripcion) VALUES
('MATE101', 'Calculo I', 6, 'Introduccion al calculo diferencial e integral.'),
('FISI101', 'Fisica I', 6, 'Mecanica y ondas.'),
('PROG101', 'Programacion I', 8, 'Fundamentos de programacion en Python/C.'),
('MATE201', 'Algebra Lineal', 5, 'Vectores, matrices y sistemas.'),
('SIST101', 'Sistemas Digitales', 6, 'Logica combinacional y secuencial.');

INSERT INTO estudiantes (nombre, matricula, carrera, semestre) VALUES
('Maria Gonzalez', '660123456', 'Ingenieria en Sistemas', 1),
('Jorge Ramirez', '660234567', 'Ingenieria Industrial', 3),
('Ana Lopez', '660345678', 'Arquitectura', 2),
('Carlos Perez', '660456789', 'Ingenieria en Sistemas', 5),
('Sofia Martinez', '660567890', 'Negocios Internacionales', 4);

INSERT INTO horario (materia_id, semestre, grupo, dia, hora_inicio, hora_fin, aula) VALUES
((SELECT id FROM materias WHERE codigo='MATE101'), '2025-1', 'A', 'Lunes', '08:00:00', '10:00:00', 'Aula 101'),
((SELECT id FROM materias WHERE codigo='MATE101'), '2025-1', 'A', 'Miercoles', '08:00:00', '10:00:00', 'Aula 101'),
((SELECT id FROM materias WHERE codigo='FISI101'), '2025-1', 'B', 'Martes', '10:00:00', '12:00:00', 'Lab Fisica'),
((SELECT id FROM materias WHERE codigo='PROG101'), '2025-1', 'A', 'Jueves', '14:00:00', '17:00:00', 'Lab Computo 1'),
((SELECT id FROM materias WHERE codigo='MATE201'), '2025-1', 'C', 'Viernes', '09:00:00', '11:00:00', 'Aula 203'),
((SELECT id FROM materias WHERE codigo='SIST101'), '2025-1', 'A', 'Lunes', '11:00:00', '13:00:00', 'Aula 105');

-- Si tiene NULL es porque recien se inscribió y aún no tiene ninguna calificación.
INSERT INTO calificaciones (estudiante_id, materia_id, semestre, calificacion)
VALUES
((SELECT id FROM estudiantes WHERE matricula='660123456'), (SELECT id FROM materias WHERE codigo='MATE101'), '2025-1', NULL),
((SELECT id FROM estudiantes WHERE matricula='660123456'), (SELECT id FROM materias WHERE codigo='PROG101'), '2024-2', 9.20);

INSERT INTO calificaciones (estudiante_id, materia_id, semestre, calificacion)
VALUES
((SELECT id FROM estudiantes WHERE matricula='660234567'), (SELECT id FROM materias WHERE codigo='FISI101'), '2025-1', 8.50),
((SELECT id FROM estudiantes WHERE matricula='660234567'), (SELECT id FROM materias WHERE codigo='MATE201'), '2024-2', 7.75);

INSERT INTO calificaciones (estudiante_id, materia_id, semestre, calificacion)
VALUES
((SELECT id FROM estudiantes WHERE matricula='660345678'), (SELECT id FROM materias WHERE codigo='MATE101'), '2025-1', NULL),
((SELECT id FROM estudiantes WHERE matricula='660345678'), (SELECT id FROM materias WHERE codigo='SIST101'), '2024-2', 8.00);

INSERT INTO calificaciones (estudiante_id, materia_id, semestre, calificacion)
VALUES
((SELECT id FROM estudiantes WHERE matricula='660456789'), (SELECT id FROM materias WHERE codigo='PROG101'), '2025-1', NULL),
((SELECT id FROM estudiantes WHERE matricula='660456789'), (SELECT id FROM materias WHERE codigo='MATE201'), '2024-2', 6.50);

INSERT INTO calificaciones (estudiante_id, materia_id, semestre, calificacion)
VALUES
((SELECT id FROM estudiantes WHERE matricula='660567890'), (SELECT id FROM materias WHERE codigo='SIST101'), '2025-1', 9.00),
((SELECT id FROM estudiantes WHERE matricula='660567890'), (SELECT id FROM materias WHERE codigo='FISI101'), '2024-2', 8.25);

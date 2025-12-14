const API_URL = "https://uvm.autumn64.xyz";

let currentStudent = null; // contendrá { id, nombre, matricula, carrera, semestre, email }

async function login() {
    const matricula = document.getElementById("matricula").value.trim();

    if (!matricula) {
        return Swal.fire("Error", "Ingresa tu matrícula", "error");
    }

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ matricula })
        });

        const json = await res.json();

        if (!res.ok || json.status !== "success") {
            return Swal.fire("Error", json.message || "Matrícula inválida", "error");
        }

        // respuesta esperada: json.data con los datos del estudiante (incluye id)
        currentStudent = json.data;

        // Mostrar dashboard
        document.getElementById("login-screen").classList.add("hidden");
        document.getElementById("dashboard").classList.remove("hidden");

        document.getElementById("student-name").textContent =
            `${currentStudent.nombre} – Semestre ${currentStudent.semestre}`;

        // perfil
        fillProfile();

        // cargar datos dependientes del id del estudiante
        await Promise.all([loadMaterias(), loadHorario(), loadCalificaciones()]);

    } catch (error) {
        console.error(error);
        Swal.fire("Error", "No se pudo conectar al servidor", "error");
    }
}

// ---------------- LOGOUT ----------------
function logout() {
    currentStudent = null;
    document.getElementById("dashboard").classList.add("hidden");
    document.getElementById("login-screen").classList.remove("hidden");
    Swal.fire("Sesión cerrada", "", "success");
}

// ---------------- TABS ----------------
function showTab(tab, ev) {
    if (ev && ev.preventDefault) ev.preventDefault();
    document.querySelectorAll(".tab-content").forEach(t => t.classList.add("hidden"));
    const el = document.getElementById(tab);
    if (el) el.classList.remove("hidden");

    document.querySelectorAll(".tabs button").forEach(btn => btn.classList.remove("active"));
    // event can be undefined if called programmatically
    if (ev && ev.currentTarget) ev.currentTarget.classList.add("active");
}

const buttons = document.querySelectorAll(".tabs button");

buttons.forEach(btn => {
  btn.addEventListener("click", () => {
    buttons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});


// ---------------- PERFIL ----------------
function fillProfile() {
    if (!currentStudent) return;
    document.getElementById("perfil-nombre").textContent = currentStudent.nombre;
    document.getElementById("perfil-matricula").textContent = currentStudent.matricula;
    document.getElementById("perfil-carrera").textContent = currentStudent.carrera;
    document.getElementById("perfil-semestre").textContent = currentStudent.semestre;
    // el backend expone email como "email" o "correo" dependiendo; usamos email por convención
    document.getElementById("perfil-correo").textContent = currentStudent.email || currentStudent.correo || "";
}

// ---------------- DATA FETCHERS (usar id donde el backend lo espera) ----------------

async function loadMaterias() {
    if (!currentStudent) return;
    try {
        const res = await fetch(`${API_URL}/estudiantes/${currentStudent.id}/materias`);
        const json = await res.json();
        if (!res.ok || json.status !== "success") {
            console.warn("Carga materias falló:", json.message);
            document.getElementById("materias-list").innerHTML = `<li>No se pudieron cargar las materias.</li>`;
            return;
        }
        const list = document.getElementById("materias-list");
        list.innerHTML = "";

        if (!json.data || json.data.length === 0) {
            list.innerHTML = "<li>No hay materias inscritas.</li>";
            return;
        }

        json.data.forEach(item => {
            // item.materia contiene info según el backend que entregué previamente
            const mat = item.materia || item;
            const nombre = mat.nombre || mat.nombre_materia || "Materia";
            const codigo = mat.codigo || mat.clave || "";
            const semestre = item.semestre || mat.semestre || "";
            const cal = (item.calificacion !== undefined && item.calificacion !== null) ? item.calificacion : "—";
            const horarios = (item.horarios && item.horarios.length)
                ? item.horarios.map(h => `${h.dia} ${h.hora_inicio}-${h.hora_fin}`).join(' • ')
                : "";

            const li = document.createElement("li");
            li.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <strong>${nombre}</strong><br><small>${codigo} · Sem: ${semestre}</small>
                        <div style="font-size:.9rem;color:#666">${horarios}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-weight:bold">${cal}</div>
                        <div style="font-size:.8rem;color:#999">Calificación</div>
                    </div>
                </div>
            `;
            list.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Error cargando materias", "error");
    }
}

async function loadHorario() {
    if (!currentStudent) return;
    try {
        // puedes agregar &semestre=... si quieres filtrar
        const res = await fetch(`${API_URL}/horario?estudiante_id=${currentStudent.id}`);
        const json = await res.json();
        if (!res.ok || json.status !== "success") {
            document.getElementById("horario-list").innerHTML = `<li>No se pudo cargar el horario.</li>`;
            return;
        }
        const list = document.getElementById("horario-list");
        list.innerHTML = "";

        if (!json.data || json.data.length === 0) {
            list.innerHTML = "<li>No hay horarios registrados.</li>";
            return;
        }

        json.data.forEach(h => {
            const li = document.createElement("li");
            li.innerHTML = `
                <strong>${h.materia || ("Materia " + h.materia_id)}</strong><br>
                <small>${h.dia} · ${h.hora_inicio} - ${h.hora_fin} · ${h.aula || ""}</small>
            `;
            list.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Error cargando horario", "error");
    }
}

async function loadCalificaciones() {
    if (!currentStudent) return;
    try {
        const res = await fetch(`${API_URL}/calificaciones?estudiante_id=${currentStudent.id}`);
        const json = await res.json();
        if (!res.ok || json.status !== "success") {
            document.getElementById("calificaciones-list").innerHTML = `<li>No se pudieron cargar las calificaciones.</li>`;
            return;
        }
        const list = document.getElementById("calificaciones-list");
        list.innerHTML = "";

        if (!json.data || json.data.length === 0) {
            list.innerHTML = "<li>No hay calificaciones registradas.</li>";
            return;
        }

        // Mostrar agrupadas por semestre
        const bySem = {};
        json.data.forEach(it => {
            const sem = it.semestre || "N/A";
            if (!bySem[sem]) bySem[sem] = [];
            bySem[sem].push(it);
        });

        for (const sem of Object.keys(bySem).sort().reverse()) {
            const liSem = document.createElement("li");
            liSem.className = "card";
            liSem.innerHTML = `<strong>Semestre: ${sem}</strong>`;
            const ul = document.createElement("ul");
            ul.style.marginTop = "8px";
            ul.style.padding = "0";
            ul.style.listStyle = "none";

            bySem[sem].forEach(it => {
                const materiaName = it.materia || ("ID " + it.materia_id);
                const cal = (it.calificacion !== null && it.calificacion !== undefined) ? it.calificacion : "—";
                const li = document.createElement("li");
                li.style.padding = "8px 0";
                li.innerHTML = `<div style="display:flex;justify-content:space-between"><span>${materiaName}</span><strong>${cal}</strong></div>`;
                ul.appendChild(li);
            });

            liSem.appendChild(ul);
            list.appendChild(liSem);
        }

    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Error cargando calificaciones", "error");
    }
}

// ---------------- ADMIN PANEL (CRUD) ----------------

function loginAdmin() {
    const pass = prompt("Clave admin:");
    if (pass === "admin123") {
        document.getElementById("login-screen").classList.add("hidden");
        document.getElementById("admin-panel").classList.remove("hidden");
        loadAdminStudents();
    } else {
        Swal.fire("Acceso denegado", "Clave incorrecta", "error");
    }
}

async function loadAdminStudents() {
    try {
        const res = await fetch(`${API_URL}/estudiantes`);
        const json = await res.json();
        if (!res.ok || json.status !== "success") {
            return Swal.fire("Error", json.message || "No se pudo obtener la lista", "error");
        }

        const tbody = document.querySelector("#admin-students-table tbody");
        tbody.innerHTML = "";

        json.data.forEach(st => {
            // cada 'st' debe tener id y matricula
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${st.matricula}</td>
                <td>${st.nombre}</td>
                <td>${st.carrera}</td>
                <td>${st.semestre}</td>
                <td>
                    <button class="btn-edit" onclick="openAdminEdit(${st.id})"><i class="fa-solid fa-pen-to-square"></i> Editar</button>
                    <button class="btn-delete" onclick="deleteStudent(${st.id})"><i class="fa-solid fa-trash"></i> Borrar</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        Swal.fire("Error", "No se pudo cargar la lista de estudiantes", "error");
    }
}

function openAdminCreate() {
    Swal.fire({
        title: "Agregar Estudiante",
        html: `
            <input id="new-nombre" class="swal2-input" placeholder="Nombre">
            <input id="new-matricula" class="swal2-input" placeholder="660123456">
            <input id="new-carrera" class="swal2-input" placeholder="Carrera">
            <input id="new-semestre" class="swal2-input" placeholder="Semestre">
        `,
        confirmButtonText: "Guardar",
        showCancelButton: true,
        preConfirm: () => {
            return {
                nombre: document.getElementById("new-nombre").value,
                matricula: document.getElementById("new-matricula").value,
                carrera: document.getElementById("new-carrera").value,
                semestre: document.getElementById("new-semestre").value,
            };
        }
    }).then(async result => {
        if (!result.isConfirmed) return;
        const payload = result.value;
        try {
            const res = await fetch(`${API_URL}/estudiantes`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (!res.ok || json.status !== "success") {
                return Swal.fire("Error", json.message || "No se pudo crear", "error");
            }
            Swal.fire("Creado", "Estudiante agregado", "success");
            loadAdminStudents();
        } catch (err) {
            console.error(err);
            Swal.fire("Error", "Fallo al crear estudiante", "error");
        }
    });
}

async function openAdminEdit(id) {
    try {
        const resGet = await fetch(`${API_URL}/estudiantes/${id}`);
        const jsonGet = await resGet.json();
        if (!resGet.ok || jsonGet.status !== "success") {
            return Swal.fire("Error", jsonGet.message || "No se encontró el estudiante", "error");
        }
        const estudiante = jsonGet.data;

        Swal.fire({
            title: "Editar Estudiante",
            html: `
                <input id="edit-nombre" class="swal2-input" value="${escapeHtml(estudiante.nombre)}" placeholder="Nombre">
                <input id="edit-carrera" class="swal2-input" value="${escapeHtml(estudiante.carrera)}" placeholder="Carrera">
                <input id="edit-semestre" class="swal2-input" value="${escapeHtml(estudiante.semestre)}" placeholder="Semestre">
            `,
            confirmButtonText: "Actualizar",
            showCancelButton: true,
            preConfirm: () => ({
                nombre: document.getElementById("edit-nombre").value,
                carrera: document.getElementById("edit-carrera").value,
                semestre: document.getElementById("edit-semestre").value,
            })
        }).then(async r => {
            if (!r.isConfirmed) return;
            try {
                const resPut = await fetch(`${API_URL}/estudiantes/${id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(r.value)
                });
                const jsonPut = await resPut.json();
                if (!resPut.ok || jsonPut.status !== "success") {
                    return Swal.fire("Error", jsonPut.message || "No se pudo actualizar", "error");
                }
                Swal.fire("Actualizado", "", "success");
                loadAdminStudents();
            } catch (err) {
                console.error(err);
                Swal.fire("Error", "Fallo al actualizar", "error");
            }
        });

    } catch (err) {
        console.error(err);
        Swal.fire("Error", "Fallo al solicitar datos", "error");
    }
}

function deleteStudent(id) {
    Swal.fire({
        title: "¿Eliminar estudiante?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Eliminar"
    }).then(async r => {
        if (!r.isConfirmed) return;
        try {
            const res = await fetch(`${API_URL}/estudiantes/${id}`, { method: "DELETE" });
            const json = await res.json();
            if (!res.ok || json.status !== "success") {
                return Swal.fire("Error", json.message || "No se pudo eliminar", "error");
            }
            Swal.fire("Eliminado", "", "success");
            loadAdminStudents();
        } catch (err) {
            console.error(err);
            Swal.fire("Error", "Fallo al eliminar", "error");
        }
    });
}

// ---------------- Utilidades ----------------
function escapeHtml(unsafe) {
    if (!unsafe && unsafe !== 0) return "";
    return String(unsafe)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
}

function adminLogin() {
    Swal.fire({
        title: "Acceso Administrativo",
        input: "password",
        inputLabel: "Ingresa la clave de administrador",
        inputPlaceholder: "Contraseña",
        showCancelButton: true,
        confirmButtonText: "Entrar",
    }).then(result => {
        if (result.isConfirmed) {
            const clave = result.value;

            // Clave fija por ahora (puedo ayudarte a hacer login real con JWT si luego lo deseas)
            if (clave === "admin123") {
                document.getElementById("login-screen").classList.add("hidden");
                document.getElementById("dashboard").classList.add("hidden");
                document.getElementById("admin-panel").classList.remove("hidden");

                loadAdminStudents();

                Swal.fire("Bienvenido", "Modo administrador activado", "success");
            } else {
                Swal.fire("Error", "Contraseña incorrecta", "error");
            }
        }
    });
}

function logoutAdmin() {
    document.getElementById("admin-panel").classList.add("hidden");
    document.getElementById("login-screen").classList.remove("hidden");
    Swal.fire("Sesión cerrada", "", "success");
}

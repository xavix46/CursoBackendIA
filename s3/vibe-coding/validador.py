import re

def validar_contrasena(password: str) -> dict:
    """
    Valida una contraseña según criterios estándar de seguridad:
    - No debe estar vacía.
    - Mínimo 8 caracteres.
    - Al menos una letra mayúscula.
    - Al menos una letra minúscula.
    - Al menos un número.
    - Al menos un carácter especial (!@#$%^&* etc.).
    """
    errores = []

    if not password:
        return {
            "valida": False,
            "errores": ["La contraseña no puede estar vacía."]
        }

    if len(password) < 8:
        errores.append("Debe tener al menos 8 caracteres.")

    if not re.search(r"[A-Z]", password):
        errores.append("Debe contener al menos una letra mayúscula.")

    if not re.search(r"[a-z]", password):
        errores.append("Debe contener al menos una letra minúscula.")

    if not re.search(r"\d", password):
        errores.append("Debe contener al menos un número.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errores.append("Debe contener al menos un carácter especial.")

    return {
        "valida": len(errores) == 0,
        "errores": errores
    }


def validar_email(email: str) -> dict:
    """
    Valida que un email cumpla con un formato estándar (usuario@dominio.extension).
    """
    errores = []

    if not email:
        return {
            "valida": False,
            "errores": ["El email no puede estar vacío."]
        }

    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(patron, email):
        errores.append("El formato del email no es válido.")

    return {
        "valida": len(errores) == 0,
        "errores": errores
    }


class GestorUsuarios:
    """
    Gestiona una lista de usuarios en memoria, validando email y contraseña.
    La validación de contraseña es opcional para administradores.
    """
    def __init__(self):
        self.usuarios = []

    def agregar_usuario(self, email: str, password: str = "", es_admin: bool = False) -> dict:
        val_email = validar_email(email)
        errores = list(val_email["errores"])

        # Validación de contraseña omitida para administradores
        if not es_admin:
            val_pass = validar_contrasena(password)
            errores.extend(val_pass["errores"])

        # Verificar si el email ya existe
        if any(u["email"] == email for u in self.usuarios):
            errores.append("El correo electrónico ya está registrado.")

        if errores:
            return {
                "exito": False,
                "email": email,
                "password": password,
                "es_admin": es_admin,
                "errores": errores
            }

        nuevo_usuario = {
            "id": len(self.usuarios) + 1,
            "email": email,
            "password": password,
            "es_admin": es_admin
        }
        self.usuarios.append(nuevo_usuario)
        return {
            "exito": True,
            "usuario": nuevo_usuario,
            "mensaje": "Usuario agregado exitosamente."
        }

    def obtener_usuarios(self) -> list:
        return self.usuarios


if __name__ == "__main__":
    gestor = GestorUsuarios()

    casos_de_prueba = [
        # 1. Usuarios válidos (estándar)
        {
            "categoria": "1. Usuario Estándar Válido",
            "email": "usuario.valido@correo.com",
            "password": "Password123!",
            "es_admin": False
        },
        # 2. Usuarios con errores (estándar)
        {
            "categoria": "2. Usuario Estándar - Contraseña Errónea / Débil",
            "email": "usuario.mal.pass@correo.com",
            "password": "123",
            "es_admin": False
        },
        {
            "categoria": "2. Usuario Estándar - Email Erróneo",
            "email": "usuario.sin.dominio@",
            "password": "Password123!",
            "es_admin": False
        },
        # 3. Administrador válido
        {
            "categoria": "3. Administrador Válido (con contraseña segura)",
            "email": "admin.valido@correo.com",
            "password": "AdminPassword123!",
            "es_admin": True
        },
        # 4. Administrador con contraseña errónea / débil / vacía
        {
            "categoria": "4. Administrador con Contraseña Errónea/Débil ('123')",
            "email": "admin.debil@correo.com",
            "password": "123",
            "es_admin": True
        },
        {
            "categoria": "4. Administrador con Contraseña Vacía ('')",
            "email": "admin.vacio@correo.com",
            "password": "",
            "es_admin": True
        },
        {
            "categoria": "4. Administrador con Email Erróneo (comprobación adicional)",
            "email": "admin.mal.email@",
            "password": "123",
            "es_admin": True
        }
    ]

    print("=" * 65)
    print("           EJECUCIÓN DE PRUEBAS DE REGISTRO")
    print("=" * 65)

    for caso in casos_de_prueba:
        print(f"\n>> Caso: {caso['categoria']}")
        print(f"   Email: '{caso['email']}' | Password: '{caso['password']}' | Admin: {caso['es_admin']}")
        res = gestor.agregar_usuario(
            email=caso["email"],
            password=caso["password"],
            es_admin=caso["es_admin"]
        )
        if res["exito"]:
            print(f"   [RESULTADO]: REGISTRADO CON ÉXITO (ID: {res['usuario']['id']})")
        else:
            print("   [RESULTADO]: RECHAZADO")
            for err in res["errores"]:
                print(f"     * {err}")

    print("\n" + "=" * 65)
    print("      LISTA FINAL DE USUARIOS EN LA BASE DE DATOS / MEMORIA")
    print("=" * 65)
    for u in gestor.obtener_usuarios():
        rol = "ADMIN" if u["es_admin"] else "USER "
        print(f"ID: {u['id']} | [{rol}] | Email: {u['email']:<28} | Password: '{u['password']}'")

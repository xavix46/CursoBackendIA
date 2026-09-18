from app.repositories import usuarios as usuarios_repository
from app.security import hash_password, verify_password


class EmailYaRegistradoError(Exception):
    pass


class CredencialesInvalidasError(Exception):
    pass


def registrar_usuario(db, email: str, password: str, repo=usuarios_repository):
    if repo.obtener_por_email(db, email):
        raise EmailYaRegistradoError(f"El email {email} ya está registrado")

    hashed = hash_password(password)
    return repo.guardar(db, email, hashed)


def autenticar_usuario(db, email: str, password: str, repo=usuarios_repository):
    usuario = repo.obtener_por_email(db, email)
    if not usuario or not verify_password(password, usuario.hashed_password):
        raise CredencialesInvalidasError("Email o contraseña incorrectos")
    return usuario

"""Excepciones personalizadas del sistema."""


class VINNotFoundError(Exception):
    """El bastidor (VIN) no existe en la base de datos."""

    def __init__(self, vin: str) -> None:
        self.vin = vin
        super().__init__(f"VIN no encontrado: {vin}")


class SessionNotFoundError(Exception):
    """La sesión solicitada no existe."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Sesión no encontrada: {session_id}")


class MaxVINAttemptsError(Exception):
    """Se superó el número máximo de intentos de VIN."""

    def __init__(self, max_attempts: int) -> None:
        self.max_attempts = max_attempts
        super().__init__(f"Máximo de intentos de VIN alcanzado ({max_attempts})")


class TreeNodeNotFoundError(Exception):
    """Nodo del árbol de diagnóstico no encontrado."""

    def __init__(self, node_id: str, tree_id: str) -> None:
        self.node_id = node_id
        self.tree_id = tree_id
        super().__init__(f"Nodo '{node_id}' no encontrado en árbol '{tree_id}'")


class GroqAPIError(Exception):
    """Error al comunicarse con la API de Groq."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Error Groq API: {message}")

from models.health import HealthResponse


class HealthService:
    def __init__(self, service_name: str) -> None:
        self.service_name = service_name

    def status(self) -> HealthResponse:
        return HealthResponse(status="ok", service=self.service_name)

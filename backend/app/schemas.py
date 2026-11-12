from pydantic import BaseModel, ConfigDict, Field


class ConsultaRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    pregunta: str = Field(min_length=1, max_length=1000)


class Fuente(BaseModel):
    documento: str
    fragmento: str


class ConsultaResponse(BaseModel):
    respuesta: str
    fuentes: list[Fuente]
    advertencia: str


class SaludResponse(BaseModel):
    estado: str

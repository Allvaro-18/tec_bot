from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "TEC Bot API"
    cors_origins: str = "http://localhost:5173"
    corpus_dir: str = str(RAIZ_PROYECTO / "documentos-demo")

    # ChromaDB (Día 3). El índice se genera con: python scripts/indexar.py
    chroma_dir: str = str(RAIZ_PROYECTO / "chroma_db")
    coleccion: str = "documentos_academicos"
    n_resultados: int = 4
    # Distancia coseno máxima para considerar que un fragmento es evidencia.
    # Calíbrala con: python scripts/consultar.py --evaluar
    umbral_distancia: float = 0.5

    # Ollama (Día 3 · Paso 4): redacta la respuesta a partir de los fragmentos.
    usar_ollama: bool = True
    ollama_model: str = "llama3.2:3b"
    ollama_host: str = "http://localhost:11434"
    # Segundos máximos de espera; si se excede, se responde con el resumen del fragmento.
    ollama_timeout: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TECBOT_",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def corpus_path(self) -> Path:
        return Path(self.corpus_dir).resolve()

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_dir).resolve()


settings = Settings()

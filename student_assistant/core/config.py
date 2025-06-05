from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    OPENAI_API_KEY: str

    CHROMA_PATH: str = "chroma_db"
    DB_PATH: str = "sqlite/student_assistant.db"
    MODEL_NAME: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    DATA_DIR_PATH: str = "data"

    LOGGING_ENABLED: bool = True


load_dotenv()
settings = Settings()
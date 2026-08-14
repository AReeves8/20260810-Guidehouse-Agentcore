
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings) :
    """
    BaseSettings gives you Pydantic checks, but for CONFIGURATION rather than data
    Maps env vars to class properties. 
        EX: SUPPORT_API_DATA_PATH -> data_path
            property names need to match

    SettingsConfigDict
        env_file - the exact name of your .env file to look in
            could also be a list of file names
        env_prefix - the prefix for all the env vars to look for
        extra - decides how to handle if the env file contains vars that you don't have mappings for in the class
    """
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SUPPORT_API_", extra="ignore")

    # giving defualt values means this class can still be instantiated without an .env file
    data_path: Path = Path("data/backupTickets.json")
    default_page_size: int = 5
    log_level: str = "DEBUG"
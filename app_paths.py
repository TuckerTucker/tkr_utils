from pathlib import Path
from dotenv import load_dotenv
from tkr_utils.decorators import logs_and_exceptions
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)

class AppPaths:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOCAL_DATA: Path = BASE_DIR / "_local_data"
    DOCS_DIR: Path = LOCAL_DATA / "_documents"
    LOG_DIR: Path = LOCAL_DATA / "_logs"
    CHAT_LOGS: Path = LOG_DIR / "chat"
    LAST_CHAT_FILE: Path = CHAT_LOGS / "last_chat.txt"
    STORES_DIR: Path = LOCAL_DATA / "_stores"

    _added_directories: list = []

    @staticmethod
    @logs_and_exceptions(logger)
    def add(name: str, storage: bool = False, test: bool = False, project_directory: Path = None) -> None:
        """
        Add a new path to the AppPaths class. If storage is True, create a storage directory.
        If test is True, create a test directory structure under the provided project directory.

        Args:
            name (str): The name of the new path.
            storage (bool): Whether to create a storage directory.
            test (bool): Whether to create a test directory.
            project_directory (Path): The project directory where tests will be run.
        """
        logger.info(f"Adding new path: {name} with storage: {storage} and test: {test}")

        if storage and test:
            raise ValueError("Cannot set both storage and test to True.")
        
        if storage:
            store_name = f"{name.upper()}_STORE"
            db_path_name = f"{name.upper()}_DB_PATH"
            store_path = AppPaths.STORES_DIR / name.lower()
            db_path = store_path / f"{name.lower()}.db"
            
            setattr(AppPaths, store_name, store_path)
            setattr(AppPaths, db_path_name, db_path)
            
            AppPaths._added_directories.append(store_path)
            AppPaths._check_directory(store_path)
        
        elif test and project_directory:
            test_dir = project_directory / name.lower()
            setattr(AppPaths, f"{name.upper()}_TEST_DIR", test_dir)
            
            AppPaths._added_directories.append(test_dir)
            AppPaths._check_directory(test_dir)
        
        else:
            dir_path = AppPaths.LOCAL_DATA / name.lower()
            setattr(AppPaths, name.upper() + "_DIR", dir_path)
            AppPaths._added_directories.append(dir_path)
            AppPaths._check_directory(dir_path)

    @staticmethod
    @logs_and_exceptions(logger)
    def check_directories() -> None:
        """
        Ensure all directories exist, create them if they don't.
        """
        logger.info("Checking all directories.")
        directories = [
            AppPaths.LOG_DIR,
            AppPaths.DOCS_DIR,
            AppPaths.CHAT_LOGS,
            *AppPaths._added_directories
        ]
        for directory in directories:
            AppPaths._check_directory(directory)

    @staticmethod
    @logs_and_exceptions(logger)
    def _check_directory(directory: Path) -> None:
        """
        Check if a directory exists, create it if it doesn't.

        Args:
            directory (Path): The directory to check and create if necessary.
        """
        if not directory.exists():
            logger.info(f"Creating directory: {directory}")
            directory.mkdir(parents=True, exist_ok=True)

AppPaths.check_directories()

__all__ = ['AppPaths']

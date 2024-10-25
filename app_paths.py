from pathlib import Path
from dotenv import load_dotenv
from tkr_utils.decorators import logs_and_exceptions

## Logging is can't use tkr_utils.setup_logging'because of circular imports
# todo: create a logging_config.yaml for both app_paths and setup_logging to use
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)

load_dotenv()

class AppPaths:
    # Create Default directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOCAL_DATA: Path = BASE_DIR / "_local_data"
    LOG_DIR: Path = LOCAL_DATA / "_logs"

    # Instantiate an empty array for the diectories added by other modules/packages
    _added_directories: list = []

    # The method to add utility directories to _local_data
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
        logger.debug(f"Adding new path: {name} with storage: {storage} and test: {test}")

        # Check if the Storage or Test arguments are used
        # These are used by tkr_stores and tkr_tests to ensure the proper diectory structure is maintained
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
        logger.debug("Checking all directories.")
        directories = [
            AppPaths.LOG_DIR,
            *AppPaths._added_directories
        ]
        for directory in directories:
            AppPaths._check_directory(directory)

    # Check if the diectories exist. If not, create them.
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

# When imported check the directories
AppPaths.check_directories()

__all__ = ['AppPaths']

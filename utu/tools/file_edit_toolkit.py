"""
by @ianxxu
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

from ..config import ToolkitConfig
from ..utils import get_logger
from .base import AsyncBaseToolkit, register_tool

logger = get_logger(__name__)


class FileEditToolkit(AsyncBaseToolkit):
    def __init__(self, config: ToolkitConfig = None) -> None:
        super().__init__(config)
        self.work_dir = Path(self.config.config.get("work_dir", "./")).resolve()
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.default_encoding = self.config.config.get("default_encoding", "utf-8")
        self.backup_enabled = self.config.config.get("backup_enabled", True)
        logger.info(
            f"FileEditToolkit initialized with output directory: {self.work_dir}, encoding: {self.default_encoding}"
        )

    def _sanitize_filename(self, filename: str) -> str:
        r"""Sanitize a filename by replacing any character that is not
        alphanumeric, a dot (.), hyphen (-), or underscore (_) with an
        underscore (_).

        Args:
            filename (str): The original filename which may contain spaces or
                special characters.

        Returns:
            str: The sanitized filename with disallowed characters replaced by
                underscores.
        """
        safe = re.sub(r"[^\w\-.]", "_", filename)
        return safe

    def _resolve_filepath(self, file_path: str) -> Path:
        r"""Convert the given string path to a Path object.

        If the provided path is not absolute, it is made relative to the
        default output directory. The filename part is sanitized to replace
        spaces and special characters with underscores, ensuring safe usage
        in downstream processing.

        Args:
            file_path (str): The file path to resolve.

        Returns:
            Path: A fully resolved (absolute) and sanitized Path object.
        """
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            path_obj = self.work_dir / path_obj

        sanitized_filename = self._sanitize_filename(path_obj.name)
        path_obj = path_obj.parent / sanitized_filename
        return path_obj.resolve()

    def _create_backup(self, file_path: Path) -> None:
        r"""Create a backup of the file if it exists and backup is enabled.

        Args:
            file_path (Path): Path to the file to backup.
        """
        if not self.backup_enabled or not file_path.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.name}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup at {backup_path}")

    @register_tool
    async def edit_file(self, file_name: str, diff: str) -> None:  # TODO: return edit result!
        r"""Edit a file by applying the provided diff.

        Args:
            file_name (str): The name of the file to edit.
            diff (str): (required) One or more SEARCH/REPLACE blocks following this exact format:
                ```
                <<<<<<< SEARCH
                [exact content to find]
                =======
                [new content to replace with]
                >>>>>>> REPLACE
                ```
        """
        resolved_path = self._resolve_filepath(file_name)
        self._create_backup(resolved_path)

        try:
            with open(resolved_path, encoding=self.default_encoding) as f:
                content = f.read()
            modified_content = content
            pattern = r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE"
            # Use re.DOTALL to make '.' match newlines as well
            matches = re.findall(pattern, diff, re.DOTALL)

            if not matches:
                logger.warning("No valid diff blocks found in the provided diff")
                return

            # Apply each search/replace pair
            for search_text, replace_text in matches:
                if search_text in modified_content:
                    modified_content = modified_content.replace(search_text, replace_text)
                else:
                    logger.warning(f"Search text not found in file: {search_text[:50]}...")

            with open(resolved_path, "w", encoding=self.default_encoding) as f:
                f.write(modified_content)
            logger.info(f"Successfully edited file: {resolved_path}")
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error editing file {resolved_path}: {str(e)}")

from .audio_toolkit import AudioToolkit
from .bash_toolkit import BashToolkit
from .codesnip_toolkit import CodesnipToolkit
from .document_toolkit import DocumentToolkit
from .file_edit_toolkit import FileEditToolkit
from .github_toolkit import GitHubToolkit
from .image_toolkit import ImageToolkit
from .memory_toolkit import SimpleMemoryToolkit
from .python_executor_toolkit import PythonExecutorToolkit
from .enhanced_python_executor_toolkit import EnhancedPythonExecutorToolkit
from .search_toolkit import SearchToolkit
from .serper_toolkit import SerperToolkit
from .tabular_data_toolkit import TabularDataToolkit
from .user_interaction_toolkit import UserInteractionToolkit as UserInteractionToolkit
from .video_toolkit import VideoToolkit
from .wikipedia_toolkit import WikipediaSearchTool

from ..config import ConfigLoader
from .base import AsyncBaseToolkit

TOOLKIT_MAP = {
    "search": SearchToolkit,
    "document": DocumentToolkit,
    "image": ImageToolkit,
    "file_edit": FileEditToolkit,
    "github": GitHubToolkit,
    "wikipedia": WikipediaSearchTool,
    "codesnip": CodesnipToolkit,
    "bash": BashToolkit,
    "python_executor": PythonExecutorToolkit,
    "enhanced_python_executor": EnhancedPythonExecutorToolkit,
    "video": VideoToolkit,
    "audio": AudioToolkit,
    "serper": SerperToolkit,
    "tabular": TabularDataToolkit,
    "memory_simple": SimpleMemoryToolkit,
}


def get_toolkits_map(names: list[str] | None = None) -> dict[str, AsyncBaseToolkit]:
    toolkits = {}
    if names is None:
        names = list(TOOLKIT_MAP.keys())
    else:
        assert all(name in TOOLKIT_MAP for name in names), f"Error config tools: {names}"
    for name in names:
        config = ConfigLoader.load_toolkit_config(name)
        toolkits[name] = TOOLKIT_MAP[name](config=config)
    return toolkits
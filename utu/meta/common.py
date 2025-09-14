from dataclasses import dataclass, field

from ..agents.common import DataClassWithStreamEvents


@dataclass
class GeneratorTaskRecorder(DataClassWithStreamEvents):
    requirements: str = field(default=None)
    selected_tools: dict[str, list[str]] = field(default=None)
    instructions: str = field(default=None)
    name: str = field(default=None)

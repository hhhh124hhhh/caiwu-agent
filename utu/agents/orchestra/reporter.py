import pathlib

from ...config import AgentConfig
from ...utils import FileUtils, SimplifiedAsyncOpenAI
from .common import AnalysisResult, OrchestraTaskRecorder


class ReporterAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = SimplifiedAsyncOpenAI(**self.config.reporter_model.model_provider.model_dump())
        self.template = self._get_template()

    @property
    def name(self) -> str:
        return self.config.reporter_config.get("name", "reporter")

    def _get_template(self):
        template_path = self.config.reporter_config.get("template_path", None)
        if template_path and pathlib.Path(template_path).exists():
            template_path = pathlib.Path(template_path)
        else:
            template_path = "agents/orchestra/reporter_sp.j2"
        return FileUtils.get_jinja_template(template_path)

    async def build(self):
        pass

    async def report(self, task_recorder: OrchestraTaskRecorder) -> AnalysisResult:
        """analyze the result of a subtask, return a report"""
        query = self.template.render(question=task_recorder.task, trajectory=task_recorder.get_trajectory_str())
        response = await self.llm.query_one(messages=query, **self.config.reporter_model.model_params.model_dump())
        return AnalysisResult(output=response)

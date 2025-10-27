# ruff: noqa
try:
    from agents.run import set_default_agent_runner
except ImportError:
    # Fallback if agents module is not available
    set_default_agent_runner = None

from .utils import EnvUtils, setup_logging
from .patch.runner import UTUAgentRunner
from .tracing import setup_tracing

EnvUtils.assert_env(["UTU_LLM_TYPE", "UTU_LLM_MODEL", "UTU_LLM_BASE_URL", "UTU_LLM_API_KEY"])
setup_logging(EnvUtils.get_env("UTU_LOG_LEVEL", "WARNING"))
setup_tracing()
# patched runner
if set_default_agent_runner is not None:
    set_default_agent_runner(UTUAgentRunner())

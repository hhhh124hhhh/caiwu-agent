import re
from collections.abc import Callable

from agents.function_schema import FuncSchema, function_schema


class ContentFilter:
    def __init__(self, banned_sites: list[str] = None):
        if banned_sites:
            self.RE_MATCHED_SITES = re.compile(r"^(" + "|".join(banned_sites) + r")")
        else:
            self.RE_MATCHED_SITES = None

    def filter_results(self, results: list[dict], limit: int, key: str = "link") -> list[dict]:
        # can also use search operator `-site:huggingface.co`
        # ret: {title, link, snippet, position, | sitelinks}
        res = []
        for result in results:
            if self.RE_MATCHED_SITES is None or not self.RE_MATCHED_SITES.match(result[key]):
                res.append(result)
            if len(res) >= limit:
                break
        return res


def get_tools_map(cls: type) -> dict[str, Callable]:
    """Get tools map from a class, without instance the class."""
    tools_map = {}
    # Iterate through all methods of the class and register @tool
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and getattr(attr, "_is_tool", False):
            tools_map[attr._tool_name] = attr
    return tools_map


def get_tools_schema(cls: type) -> dict[str, FuncSchema]:
    """Get tools schema from a class, without instance the class."""
    tools_map = {}
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and getattr(attr, "_is_tool", False):
            tools_map[attr._tool_name] = function_schema(attr)
    return tools_map

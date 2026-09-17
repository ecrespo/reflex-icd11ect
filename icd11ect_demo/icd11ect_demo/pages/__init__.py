"""Pages of the demo app."""

from icd11ect_demo.pages.api import api_page
from icd11ect_demo.pages.browser import browser_page
from icd11ect_demo.pages.coding_tool import coding_tool_page
from icd11ect_demo.pages.custom import custom_page
from icd11ect_demo.pages.multi import multi_page
from icd11ect_demo.pages.servers import servers_page

__all__ = [
    "api_page",
    "browser_page",
    "coding_tool_page",
    "custom_page",
    "multi_page",
    "servers_page",
]

import re
from context_definitions import get_context_info

class FilterBuilder:

    def __init__(self, context_key: str):
        self.context = get_context_info(context_key)
        if not self.context:
            raise ValueError("Invalid context")

        self.table = self.context["table_name"]
        self.columns = self.context["columns"]

    def build(self, query: str):
        q = query.lower()

        #MAX
        if "max" in q or "maximum" in q:
            col = self._find_column(q)
            return self._max(col)

        # MIN
        if "min" in q or "minimum" in q:
            col = self._find_column(q)
            return self._min(col)

        # GREATER / LESS
        if "greater" in q or "more than" in q:
            return self._compare(q, ">")

        if "less" in q or "below" in q:
            return self._compare(q, "<")

        # COUNT
        if "count" in q or "how many" in q:
            return {"sql": f"SELECT COUNT(*) FROM {self.table}"}

        return {"error": "Unable to generate SQL filter"}

    def _find_column(self, q):
        for col in self.columns:
            if col in q:
                return col
        return None

    def _max(self, col):
        if not col:
            return {"error": "Column not found"}
        return {"sql": f"SELECT * FROM {self.table} ORDER BY {col} DESC LIMIT 1"}

    def _min(self, col):
        if not col:
            return {"error": "Column not found"}
        return {"sql": f"SELECT * FROM {self.table} ORDER BY {col} ASC LIMIT 1"}

    def _compare(self, q, op):
        col = self._find_column(q)
        nums = re.findall(r'\d+', q)
        if not col or not nums:
            return {"error": "Invalid comparison"}
        return {"sql": f"SELECT * FROM {self.table} WHERE {col} {op} {nums[0]}"}


def build_filter(context: str, query: str):
    builder = FilterBuilder(context)
    return builder.build(query)

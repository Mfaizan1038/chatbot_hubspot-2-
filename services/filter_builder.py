import re
from typing import Dict, Optional
from context_definitions import get_context_info


class FilterBuilder:
    """Build Supabase SELECT and UPDATE queries from natural language"""

    def __init__(self, context_key: str):
        self.context_key = context_key.upper()
        self.context_info = get_context_info(self.context_key)

        if not self.context_info:
            raise ValueError(f"Context '{context_key}' not found")

        self.table_name = self.context_info["table_name"]
        self.columns = self.context_info["columns"]

    def parse_query(self, query: str) -> Dict:
        query = query.lower().strip()

        # ---------- UPDATE DETECTION ----------
        if any(w in query for w in ["update", "set", "change", "modify"]):
            return self._handle_update(query)

        base = f'supabase.table("{self.table_name}").select("*")'

        if any(w in query for w in ["maximum", "max", "highest", "largest"]):
            return self._handle_max_query(query, base)

        elif any(w in query for w in ["minimum", "min", "lowest", "smallest"]):
            return self._handle_min_query(query, base)

        elif any(w in query for w in ["average", "avg", "mean"]):
            return self._handle_avg_query(query)

        elif any(w in query for w in ["count", "number of", "how many"]):
            return self._handle_count_query(query)

        elif any(w in query for w in ["greater than", "more than", "above", ">"]):
            return self._handle_comparison(query, "gt", base)

        elif any(w in query for w in ["less than", "below", "under", "<"]):
            return self._handle_comparison(query, "lt", base)

        elif any(w in query for w in ["equal to", "equals", "is", "="]):
            return self._handle_comparison(query, "eq", base)

        elif "between" in query:
            return self._handle_between(query, base)

        elif any(w in query for w in ["like", "contains", "includes"]):
            return self._handle_like(query, base)

        elif any(w in query for w in ["sort", "order", "arrange"]):
            return self._handle_order(query, base)

        elif any(w in query for w in ["status", "active", "inactive", "pending", "completed"]):
            return self._handle_status_filter(query, base)

        return {"supabase_query": base}

    # ---------------- UPDATE HANDLER ---------------- #

    def _handle_update(self, query: str) -> Dict:
        updates = self._extract_update_values(query)
        conditions = self._extract_conditions(query)

        if not updates:
            return {"supabase_query": ""}

        update_dict = "{ " + ", ".join(
            f'"{k}": "{v}"' if self.columns[k]["type"] == "STRING" else f'"{k}": {v}'
            for k, v in updates.items()
        ) + " }"

        base = f'supabase.table("{self.table_name}").update({update_dict})'

        for col, val in conditions.items():
            if self.columns[col]["type"] == "STRING":
                base += f'.eq("{col}", "{val}")'
            else:
                base += f'.eq("{col}", {val})'

        return {"supabase_query": base}

    # ---------------- SELECT HANDLERS ---------------- #

    def _handle_max_query(self, query: str, base: str) -> Dict:
        column = self._extract_column(query)
        return {"supabase_query": f'{base}.order("{column}", desc=True).limit(1)'} if column else {"supabase_query": base}

    def _handle_min_query(self, query: str, base: str) -> Dict:
        column = self._extract_column(query)
        return {"supabase_query": f'{base}.order("{column}").limit(1)'} if column else {"supabase_query": base}

    def _handle_avg_query(self, query: str) -> Dict:
        column = self._extract_column(query)
        return {"supabase_query": f'supabase.table("{self.table_name}").select("avg({column})")'} if column else {"supabase_query": ""}

    def _handle_count_query(self, query: str) -> Dict:
        return {"supabase_query": f'supabase.table("{self.table_name}").select("*", count="exact")'}

    def _handle_comparison(self, query: str, operator: str, base: str) -> Dict:
        column = self._extract_column(query)
        value = self._extract_value(query, column)

        if not column or value is None:
            return {"supabase_query": base}

        if self.columns[column]["type"] == "STRING":
            return {"supabase_query": f'{base}.{operator}("{column}", "{value}")'}

        return {"supabase_query": f'{base}.{operator}("{column}", {int(value)})'}

    def _handle_between(self, query: str, base: str) -> Dict:
        column = self._extract_column(query)
        nums = re.findall(r'\d+', query)
        if not column or len(nums) < 2:
            return {"supabase_query": base}
        return {"supabase_query": f'{base}.gte("{column}", {nums[0]}).lte("{column}", {nums[1]})'}

    def _handle_like(self, query: str, base: str) -> Dict:
        column = self._extract_column(query)
        value = self._extract_quoted_value(query)
        if not column or not value:
            return {"supabase_query": base}
        return {"supabase_query": f'{base}.ilike("{column}", "%{value}%")'}

    def _handle_order(self, query: str, base: str) -> Dict:
        column = self._extract_column(query)
        desc = any(w in query for w in ["desc", "descending", "highest", "largest"])
        return {"supabase_query": f'{base}.order("{column}", desc={desc})'} if column else {"supabase_query": base}

    def _handle_status_filter(self, query: str, base: str) -> Dict:
        status_col = next((c for c in self.columns if "status" in c.lower()), None)
        if not status_col:
            return {"supabase_query": base}

        for status in ["active", "inactive", "pending", "completed", "cancelled", "suspended"]:
            if status in query:
                return {"supabase_query": f'{base}.eq("{status_col}", "{status}")'}

        return {"supabase_query": base}

    # ---------------- HELPERS ---------------- #

    def _extract_column(self, query: str) -> Optional[str]:
        for col in self.columns:
            if col.lower() in query:
                return col
        return None

    def _extract_value(self, query: str, column: str) -> Optional[str]:
        quoted = re.findall(r'["\']([^"\']+)["\']', query)
        if quoted:
            return quoted[0]

        numbers = re.findall(r'\d+(?:\.\d+)?', query)
        if numbers:
            return numbers[0]

        match = re.search(rf'{column}\s*(?:is|=|equals?)\s*(\w+)', query, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_quoted_value(self, query: str) -> Optional[str]:
        quoted = re.findall(r'["\']([^"\']+)["\']', query)
        return quoted[0] if quoted else None

    def _extract_update_values(self, query: str) -> Dict:
        updates = {}
        match = re.search(r'set (.+?)( where|$)', query, re.IGNORECASE)
        if not match:
            return updates

        assignments = match.group(1).split(',')

        for a in assignments:
            if '=' not in a:
                continue
            col, val = a.split('=', 1)
            col = col.strip()
            val = val.strip().strip('"\'')
            if col in self.columns:
                updates[col] = val if self.columns[col]["type"] == "STRING" else int(val)
        return updates

    def _extract_conditions(self, query: str) -> Dict:
        conditions = {}
        for col in self.columns:
            match = re.search(rf'{col}\s*=\s*["\']?([^"\']+)', query, re.IGNORECASE)
            if match:
                val = match.group(1)
                conditions[col] = val if self.columns[col]["type"] == "STRING" else int(val)
        return conditions


def build_filter(context_key: str, query: str) -> Dict:
    try:
        return FilterBuilder(context_key).parse_query(query)
    except ValueError:
        return {"supabase_query": ""}

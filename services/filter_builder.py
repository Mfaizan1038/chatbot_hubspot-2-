import re
from typing import Dict, Optional
from context_definitions import get_context_info


class FilterBuilder:
    """
    Build Supabase SELECT and UPDATE queries from natural language
    """

    def __init__(self, context_key: str):
        self.context_key = context_key.upper()
        self.context_info = get_context_info(self.context_key)

        if not self.context_info:
            raise ValueError(f"Context '{context_key}' not found")

        self.table_name = self.context_info["table_name"]
        self.columns = self.context_info["columns"]

    # ==========================================================
    # ENTRY POINT
    # ==========================================================

    def parse_query(self, query: str) -> Dict:
        query_lower = query.lower().strip()

        # -------- UPDATE ----------
        if any(w in query_lower for w in ["update", "set", "change", "modify"]):
            return self._handle_update(query)

        base = f'supabase.table("{self.table_name}").select("*")'

        # -------- AGGREGATIONS ----------
        if any(w in query_lower for w in ["maximum", "max", "highest", "largest"]):
            return self._handle_max(query_lower, base)

        if any(w in query_lower for w in ["minimum", "min", "lowest", "smallest"]):
            return self._handle_min(query_lower, base)

        if any(w in query_lower for w in ["average", "avg", "mean"]):
            return self._handle_avg(query_lower)

        # -------- COUNT ----------
        if re.search(r"\b(count|total|how many|number of)\b", query_lower):
            return self._handle_count()

        # -------- FILTERS ----------
        if "between" in query_lower:
            return self._handle_between(query_lower, base)

        if any(w in query_lower for w in ["like", "contains", "includes"]):
            return self._handle_like(query_lower, base)

        # -------- CONDITIONS & COMPARISONS ----------
        if any(w in query_lower for w in ["=", " is ", " equals ", "less than", "greater than",
                                         "below", "above", "<", ">"]):
            base = self._apply_conditions(query_lower, base)
            return {"supabase_query": base}

        # If no recognized pattern, return base
        return {"supabase_query": base}

    # ==========================================================
    # UPDATE HANDLER
    # ==========================================================

    def _handle_update(self, query: str) -> Dict:
        updates = self._extract_update_values(query)
        conditions = self._extract_conditions(query)

        if not updates or not conditions:
            return {"error": "Invalid UPDATE query. SET or WHERE clause missing"}

        update_payload = "{ " + ", ".join(
            f'"{k}": "{v}"' if self.columns[k]["type"] == "STRING"
            else f'"{k}": {v}'
            for k, v in updates.items()
        ) + " }"

        base = f'supabase.table("{self.table_name}").update({update_payload})'

        for col, val in conditions.items():
            if self.columns[col]["type"] == "STRING":
                base += f'.eq("{col}", "{val}")'
            else:
                base += f'.eq("{col}", {val})'

        return {"supabase_query": base}

    # ==========================================================
    # SELECT HANDLERS
    # ==========================================================

    def _handle_max(self, query: str, base: str) -> Dict:
        col = self._extract_column(query)
        return {"supabase_query": f'{base}.order("{col}", desc=True).limit(1)'} if col else {"supabase_query": base}

    def _handle_min(self, query: str, base: str) -> Dict:
        col = self._extract_column(query)
        return {"supabase_query": f'{base}.order("{col}").limit(1)'} if col else {"supabase_query": base}

    def _handle_avg(self, query: str) -> Dict:
        col = self._extract_column(query)
        return {
            "supabase_query": f'supabase.table("{self.table_name}").select("avg({col})")'
        } if col else {"supabase_query": ""}

    def _handle_count(self) -> Dict:
        return {
            "supabase_query": f'supabase.table("{self.table_name}").select("*", count="exact")'
        }

    def _handle_between(self, query: str, base: str) -> Dict:
        col = self._extract_column(query)
        nums = re.findall(r'\d+', query)

        if not col or len(nums) < 2:
            return {"supabase_query": base}

        return {
            "supabase_query": f'{base}.gte("{col}", {nums[0]}).lte("{col}", {nums[1]})'
        }

    def _handle_like(self, query: str, base: str) -> Dict:
        col = self._extract_column(query)
        val = self._extract_quoted_value(query)

        if not col or not val:
            return {"supabase_query": base}

        return {
            "supabase_query": f'{base}.ilike("{col}", "%{val}%")'
        }

    # ==========================================================
    # CONDITIONS + COMPARISONS (AND MULTIPLE)
    # ==========================================================

    def _apply_conditions(self, query: str, base: str) -> str:
        conditions = {}
        operators = {
            "less than": "lt",
            "below": "lt",
            "under": "lt",
            "<": "lt",
            "greater than": "gt",
            "above": "gt",
            "over": "gt",
            ">": "gt",
        }

        for col, meta in self.columns.items():
            # ----- EQUALITY -----
            quoted_pattern = rf'{col}\s*(=|is|equals?)\s*["\']([^"\']+)["\']'
            plain_pattern = rf'{col}\s*(=|is|equals?)\s*([0-9]+)'

            quoted_match = re.search(quoted_pattern, query, re.IGNORECASE)
            plain_match = re.search(plain_pattern, query, re.IGNORECASE)

            if quoted_match:
                val = quoted_match.group(2)
                conditions[col] = val
            elif plain_match:
                val = int(plain_match.group(2))
                conditions[col] = val

            # ----- COMPARISONS -----
            for phrase, op in operators.items():
                pattern = rf'{col}.*?{phrase}.*?(\d+)'
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    val = int(match.group(1))
                    if meta["type"] == "INTEGER":
                        base += f'.{op}("{col}", {val})'
                    else:
                        base += f'.{op}("{col}", "{val}")'

        # Apply equality conditions
        for col, val in conditions.items():
            if self.columns[col]["type"] == "STRING":
                base += f'.eq("{col}", "{val}")'
            else:
                base += f'.eq("{col}", {val})'

        return base

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _extract_column(self, query: str) -> Optional[str]:
        for col in self.columns:
            if col.lower() in query:
                return col
        return None

    def _extract_quoted_value(self, query: str) -> Optional[str]:
        match = re.findall(r'["\']([^"\']+)["\']', query)
        return match[0] if match else None

    def _extract_update_values(self, query: str) -> Dict:
        updates = {}
        match = re.search(r'set (.+?)( where|$)', query, re.IGNORECASE)
        if not match:
            return updates

        assignments = match.group(1).split(",")

        for item in assignments:
            if "=" not in item:
                continue
            col, val = item.split("=", 1)
            col = col.strip()
            val = val.strip().strip('"\'')
            if col in self.columns:
                updates[col] = (
                    val if self.columns[col]["type"] == "STRING" else int(val)
                )

        return updates

    def _extract_conditions(self, query: str) -> Dict:
        conditions = {}
        match = re.search(r'where (.+)', query, re.IGNORECASE)
        if not match:
            return conditions

        where_clause = match.group(1)

        for col in self.columns:
            m = re.search(
                rf'{col}\s*=\s*["\']?([^"\']+)',
                where_clause,
                re.IGNORECASE
            )
            if m:
                val = m.group(1)
                if self.columns[col]["type"] == "INTEGER":
                    val = int(val)
                conditions[col] = val

        return conditions


# ==========================================================
# PUBLIC FUNCTION
# ==========================================================

def build_filter(context_key: str, query: str) -> Dict:
    try:
        return FilterBuilder(context_key).parse_query(query)
    except Exception as e:
        return {"error": str(e)}

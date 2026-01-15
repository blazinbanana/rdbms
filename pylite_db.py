import json
import os
import re

class Table:
    def __init__(self, name, columns, pk_column=None):
        self.name = name
        self.columns = columns  # {"id": "int", "name": "str"}
        self.rows = []
        self.pk_column = pk_column
        self.index = {}  # Hash Index for Primary Key {pk_val: row_data}

    def insert(self, values):
        if len(values) != len(self.columns):
            raise ValueError("Column count mismatch")
        
        row = dict(zip(self.columns.keys(), values))
        
        # Unique Key Check / Indexing
        if self.pk_column:
            pk_val = row[self.pk_column]
            if pk_val in self.index:
                raise ValueError(f"Duplicate entry for Primary Key '{pk_val}'")
            self.index[pk_val] = row
            
        self.rows.append(row)

    def delete(self, col, val):
        # Delete from rows
        initial_len = len(self.rows)
        self.rows = [r for r in self.rows if str(r.get(col)) != str(val)]
        
        # Rebuild Index if needed
        if self.pk_column and col == self.pk_column and len(self.rows) < initial_len:
            del self.index[val]
            
        return initial_len - len(self.rows)

class Database:
    def __init__(self):
        self.tables = {}
        self.load_metadata()

    def load_metadata(self):
        if os.path.exists("db_meta.json"):
            with open("db_meta.json", "r") as f:
                meta = json.load(f)
                for t_name, t_data in meta.items():
                    # Reconstruct tables
                    t = Table(t_name, t_data['columns'], t_data.get('pk'))
                    t.rows = t_data['rows']
                    # Rebuild index
                    if t.pk_column:
                        for row in t.rows:
                            t.index[row[t.pk_column]] = row
                    self.tables[t_name] = t

    def save_metadata(self):
        data = {name: {'columns': t.columns, 'rows': t.rows, 'pk': t.pk_column} 
                for name, t in self.tables.items()}
        with open("db_meta.json", "w") as f:
            json.dump(data, f, indent=4)

    def execute(self, query):
        query = query.strip()
        
        # 1. CREATE TABLE table (col1 type, col2 type) PRIMARY KEY col1
        match_create = re.match(r"CREATE TABLE (\w+) \((.*?)\)(?: PRIMARY KEY (\w+))?", query, re.IGNORECASE)
        if match_create:
            name, cols_str, pk = match_create.groups()
            
            # --- FIX STARTS HERE ---
            # Guard clause: If table exists, do nothing and return.
            if name in self.tables:
                return f"Table '{name}' already exists. Skipping creation."
            # --- FIX ENDS HERE ---

            columns = {}
            for col_def in cols_str.split(','):
                c_name, c_type = col_def.strip().split()
                columns[c_name] = c_type
            
            self.tables[name] = Table(name, columns, pk)
            self.save_metadata()
            return f"Table '{name}' created."

        # 2. INSERT INTO table VALUES (val1, val2)
        match_insert = re.match(r"INSERT INTO (\w+) VALUES \((.*?)\)", query, re.IGNORECASE)
        if match_insert:
            name, vals_str = match_insert.groups()
            if name not in self.tables: return f"Error: Table {name} not found."
            
            # Simple type conversion
            values = []
            for v in vals_str.split(','):
                v = v.strip().strip("'").strip('"')
                if v.isdigit(): v = int(v)
                values.append(v)
            
            try:
                self.tables[name].insert(values)
                self.save_metadata()
                return "1 row inserted."
            except ValueError as e:
                return f"Error: {e}"

        # 3. SELECT * FROM table [JOIN table2 ON col=col] [WHERE col=val]
        if query.upper().startswith("SELECT"):
            # Simple parser for: SELECT * FROM t1 [JOIN t2 ON t1.c=t2.c] [WHERE c=v]
            parts = query.split()
            t_name = parts[3]
            
            if t_name not in self.tables: return "Table not found."
            
            result = self.tables[t_name].rows
            
            # Handle JOIN (Nested Loop Join)
            if "JOIN" in parts:
                join_idx = parts.index("JOIN")
                t2_name = parts[join_idx + 1]
                on_idx = parts.index("ON")
                condition = parts[on_idx + 1] # t1.id=t2.fk
                left_key, right_key = condition.split('=')
                left_col = left_key.split('.')[1]
                right_col = right_key.split('.')[1]
                
                joined_rows = []
                for r1 in result:
                    for r2 in self.tables[t2_name].rows:
                        if str(r1[left_col]) == str(r2[right_col]):
                            # Merge dicts
                            new_row = {**r1, **{f"{t2_name}_{k}": v for k, v in r2.items()}}
                            joined_rows.append(new_row)
                result = joined_rows

            # Handle WHERE (Linear Scan or Index Lookup)
            if "WHERE" in parts:
                where_idx = parts.index("WHERE")
                cond = parts[where_idx + 1]
                col, val = cond.split('=')
                val = val.strip("'").strip('"')
                
                # Check if we can use Index (Primary Key lookup)
                table_obj = self.tables[t_name]
                if table_obj.pk_column == col and "JOIN" not in parts:
                     # O(1) Lookup
                     res = table_obj.index.get(int(val) if val.isdigit() else val)
                     result = [res] if res else []
                else:
                    # O(N) Scan
                    result = [r for r in result if str(r.get(col, r.get(f"{t_name}_{col}"))) == val]

            return result

        # 4. DELETE FROM table WHERE col=val
        match_delete = re.match(r"DELETE FROM (\w+) WHERE (\w+)=(.*)", query, re.IGNORECASE)
        if match_delete:
            name, col, val = match_delete.groups()
            val = val.strip().strip("'").strip('"')
            if name not in self.tables: return "Table not found"
            
            count = self.tables[name].delete(col, int(val) if val.isdigit() else val)
            self.save_metadata()
            return f"{count} rows deleted."

        return "Syntax Error or Unknown Command"

# REPL Mode
if __name__ == "__main__":
    db = Database()
    print("PyLiteDB v1.0 - Type 'exit' to quit")
    while True:
        try:
            cmd = input("SQL> ")
            if cmd.lower() == 'exit': break
            res = db.execute(cmd)
            if isinstance(res, list):
                print(json.dumps(res, indent=2) if res else "No results.")
            else:
                print(res)
        except Exception as e:
            print(f"Error: {e}")
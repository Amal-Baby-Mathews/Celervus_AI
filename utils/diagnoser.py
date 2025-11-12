#!/usr/bin/env python3
# diagnose_and_fix_lancedb.py
"""
Diagnose and sanitize the exact batch you attempt to add to LanceDB.

Place this file in the same directory as diagnoser.py and entries.json (or ensure
utils.multimodal_db.debug_sample_entries exists with the same batch).
Run: python3 diagnose_and_fix_lancedb.py
"""

import os
import sys
import json
import traceback
from pprint import pprint

try:
    import numpy as np
except Exception:
    np = None
try:
    import torch
except Exception:
    torch = None

import pyarrow as pa
import lancedb

DB_PATH = "./lancedb"
TABLE_NAME = "multimodal_table"
ENTRIES_JSON = "entries.json"
SANITIZED_JSON = "sanitized_entries.json"

def print_versions():
    try:
        import pyarrow as pa
        import lancedb as ldb
        print("pyarrow:", pa.__version__)
        print("lancedb:", ldb.__version__)
    except Exception as e:
        print("Error printing versions:", e)

def get_table_schema():
    if not os.path.exists(DB_PATH):
        print(f"No DB folder at {DB_PATH}")
        return None, None, None
    db = lancedb.connect(DB_PATH)
    if TABLE_NAME not in db.table_names():
        print(f"Table {TABLE_NAME} not present in DB (tables: {db.table_names()})")
        return db, None, None
    table = db.open_table(TABLE_NAME)
    try:
        schema_repr = repr(table.schema)
    except Exception:
        schema_repr = str(table.schema)
    print("\n--- TABLE SCHEMA REPR ---")
    print(schema_repr)
    # Try to parse expected dims from repr
    expected_text_dim = None
    expected_image_dim = None
    try:
        s = schema_repr
        # parse patterns fixed_size_list<item: float>[NNN]
        import re
        m_text = re.search(r"text_vector:.*?fixed_size_list.*?\[(\d+)\]", s)
        if m_text:
            expected_text_dim = int(m_text.group(1))
        m_image = re.search(r"image_vector:.*?fixed_size_list.*?\[(\d+)\]", s)
        if m_image:
            expected_image_dim = int(m_image.group(1))
    except Exception:
        pass
    return db, expected_text_dim, expected_image_dim

def load_entries():
    if os.path.exists(ENTRIES_JSON):
        with open(ENTRIES_JSON, "r") as f:
            entries = json.load(f)
            print(f"Loaded {len(entries)} entries from {ENTRIES_JSON}")
            return entries
    # fallback: try to import debug sample from utils.multimodal_db
    try:
        import multimodal_db as mdb
        entries = getattr(mdb, "debug_sample_entries", None)
        if entries is not None:
            print("Loaded debug_sample_entries from utils.multimodal_db")
            return entries
    except Exception as e:
        print("Could not import debug_sample_entries from utils.multimodal_db:", e)
    print("No entries found. Create entries.json or define debug_sample_entries in utils.multimodal_db")
    return None

def info_for_vector(v):
    if v is None:
        return ("None", None, None)
    # numpy
    if np is not None and isinstance(v, np.ndarray):
        return ("ndarray", v.shape, str(v.dtype))
    if torch is not None and isinstance(v, torch.Tensor):
        return ("torch", tuple(v.shape), str(v.dtype))
    if isinstance(v, list):
        nested = any(isinstance(x, (list, tuple, np.ndarray)) or (torch is not None and isinstance(x, torch.Tensor)) for x in v)
        elem_types = {}
        for x in v[:20]:
            elem_types[type(x).__name__] = elem_types.get(type(x).__name__, 0) + 1
        return ("list", len(v), {"nested": nested, "elem_types_sample": elem_types})
    return (type(v).__name__, None, None)

def normalize_vector_to_list(v):
    # Convert tensor/ndarray to flat python list of floats
    if v is None:
        return None
    # treat empty list as missing
    if isinstance(v, list) and len(v) == 0:
        return None
    if torch is not None and isinstance(v, torch.Tensor):
        a = v.detach().cpu().numpy()
        v = a
    if np is not None and isinstance(v, np.ndarray):
        if v.ndim != 1:
            raise ValueError(f"ndarray must be 1-D, got shape {v.shape}")
        return v.astype(float).tolist()
    if isinstance(v, list):
        # nested list detection
        if any(isinstance(x, (list, tuple, np.ndarray)) or (torch is not None and isinstance(x, torch.Tensor)) for x in v):
            raise ValueError("Nested lists detected inside vector (list-of-lists)")
        return [float(x) for x in v]
    if isinstance(v, (int, float)):
        raise ValueError("Scalar provided where vector expected")
    raise TypeError(f"Unhandled vector type: {type(v)}")

def inspect_batch(entries, expect_text_dim=None, expect_image_dim=None):
    print("\n=== BATCH INSPECTION ===")
    problems = []
    for i, e in enumerate(entries):
        pk = e.get("pk")
        text = e.get("text")
        print(f"\nEntry[{i}] pk={pk!r} text={text!r}")
        for col in ("image_vector", "text_vector"):
            v = e.get(col, None)
            typ, shape, extra = info_for_vector(v)
            print(f"  - {col}: type={typ}, shape={shape}, extra={extra}")
            if typ == "list" and shape == 0:
                problems.append((i, col, "empty list [] (should be None)"))
            if typ == "list" and extra and extra.get("nested"):
                problems.append((i, col, "nested lists inside vector"))
            if typ in ("ndarray", "torch") and (shape is None or (isinstance(shape, tuple) and len(shape) > 1)):
                problems.append((i, col, f"ndarray/torch with bad ndim: {shape}"))
            # length mismatches if we expect dims
            if typ == "list" and expect_image_dim and col == "image_vector" and shape is not None and shape != expect_image_dim:
                problems.append((i, col, f"image length {shape} != expected {expect_image_dim}"))
            if typ == "list" and expect_text_dim and col == "text_vector" and shape is not None and shape != expect_text_dim:
                problems.append((i, col, f"text length {shape} != expected {expect_text_dim}"))
    print("\n=== END BATCH INSPECTION ===")
    if problems:
        print("\nPROBLEMS FOUND:")
        pprint(problems)
    else:
        print("\nNo obvious problems detected in batch structure (type/empty/nested/length mismatches).")
    return problems

def try_pyarrow_cast(entries, db, expect_text_dim, expect_image_dim):
    # attempt to create a pyarrow table and cast it to the DB's schema to reproduce Arrow errors
    if db is None:
        print("No DB connection / table to test pyarrow cast against.")
        return False
    if TABLE_NAME not in db.table_names():
        print("Table not present in DB - cannot cast to table schema.")
        return False
    table = db.open_table(TABLE_NAME)
    try:
        schema = table.schema
    except Exception:
        schema = None
    print("\n--- Attempt PyArrow table creation and cast (this may reproduce the ArrowInvalid error) ---")
    # Build dict of columns using keys present in first entry (safe superset)
    colnames = set()
    for e in entries:
        colnames.update(e.keys())
    cols = {}
    for name in colnames:
        cols[name] = [e.get(name, None) for e in entries]
    try:
        pa_cols = {k: pa.array(v) for k, v in cols.items()}
        pa_tbl = pa.table(pa_cols)
        print("Created pyarrow table with schema:", pa_tbl.schema)
        if schema is not None:
            try:
                # Try cast
                target = schema.to_arrow_schema() if hasattr(schema, "to_arrow_schema") else pa_tbl.schema
                print("Attempting cast to target schema ...")
                pa_tbl.cast(target)
                print("Cast successful (unexpected).")
                return True
            except Exception:
                print("Cast failed; traceback:")
                traceback.print_exc()
                return False
        else:
            print("No table schema available to cast to.")
            return False
    except Exception:
        print("Failed to build pyarrow table from columns; traceback:")
        traceback.print_exc()
        return False

def try_add_one_by_one(db, entries):
    if db is None or TABLE_NAME not in db.table_names():
        print("No existing table to try per-row add. Skipping one-by-one add test.")
        return None
    table = db.open_table(TABLE_NAME)
    print("\n--- Attempting to add rows one-by-one to find first failing index ---")
    for i, e in enumerate(entries):
        try:
            table.add([e])
            print(f"Added entry index {i} OK")
        except Exception:
            print(f"Failed to add entry index {i}. Dumping diagnostics for this entry:")
            pprint(e)
            print("Entry vector diagnostics:")
            for col in ("image_vector", "text_vector"):
                v = e.get(col, None)
                print(" ", col, "->", info_for_vector(v))
            traceback.print_exc()
            return i
    print("All rows added individually successfully.")
    return None

def sanitize_entries(entries):
    sanitized = []
    for i, e in enumerate(entries):
        se = dict(e)
        for col in ("image_vector", "text_vector"):
            try:
                se[col] = normalize_vector_to_list(se.get(col, None))
            except Exception as ex:
                print(f"Normalization error on entry[{i}] col={col}: {ex}")
                # keep original, but annotate error in a key so user sees it
                se[f"_normalize_error_{col}"] = str(ex)
        sanitized.append(se)
    # write out sanitized file
    with open(SANITIZED_JSON, "w") as f:
        json.dump(sanitized, f, indent=2)
    print(f"Sanitized entries written to {SANITIZED_JSON}")
    return sanitized

def main():
    print_versions()
    db, expect_text_dim, expect_image_dim = get_table_schema()
    print("\nExpected dims parsed from table schema:")
    print(" text_vector dim:", expect_text_dim)
    print(" image_vector dim:", expect_image_dim)

    entries = load_entries()
    if entries is None:
        return

    problems = inspect_batch(entries, expect_text_dim, expect_image_dim)

    # Try a pyarrow cast to reproduce the ArrowInvalid
    cast_ok = try_pyarrow_cast(entries, db, expect_text_dim, expect_image_dim)
    print("PyArrow cast result:", cast_ok)

    # Sanitize entries (convert ndarrays/tensors to lists, []->None); writes sanitized_entries.json
    sanitized = sanitize_entries(entries)

    # Try per-row add to find the first failing index (does not change DB if failing rows are skipped)
    if db is not None and TABLE_NAME in db.table_names():
        failing_index = try_add_one_by_one(db, sanitized)
        if failing_index is not None:
            print(f"First failing index (one-by-one add): {failing_index}")
        else:
            print("No failing index in per-row add test (odd — may be batch-cast issue).")
    else:
        print("Table not present or DB missing; skipping one-by-one add test.")

    print("\n--- DIAGNOSTIC SUMMARY ---")
    if problems:
        print("Problems found in structure/lengths:")
        pprint(problems)
    else:
        print("No obvious structural problems found in the source batch; the failure likely arises from mismatched lengths or batch-cast behaviour.")
    print("Sanitized copy created:", SANITIZED_JSON)
    print("If you want to try adding the sanitized entries automatically, open this script and un-comment the final section to call table.add(sanitized).")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)

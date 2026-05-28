import sqlite3
import json
from ..db import fetchone


def apply_override(
    line_item_id: int,
    field_name: str,
    override_value: float,
    reason: str,
    user_id: int,
    db: sqlite3.Connection,
) -> None:
    row = fetchone(
        db,
        "SELECT is_overridden, override_values, original_calc_values FROM quote_line_items WHERE id=?",
        (line_item_id,),
    )
    if not row:
        raise ValueError(f"line_item_id={line_item_id} not found")

    is_overridden = json.loads(row["is_overridden"] or "{}")
    override_values = json.loads(row["override_values"] or "{}")
    original_calc = json.loads(row["original_calc_values"] or "{}")

    if field_name not in original_calc:
        current_val = db.execute(
            f"SELECT {field_name} FROM quote_line_items WHERE id=?", (line_item_id,)
        ).fetchone()
        original_calc[field_name] = current_val[0] if current_val else None

    is_overridden[field_name] = True
    override_values[field_name] = override_value

    db.execute(
        "UPDATE quote_line_items SET is_overridden=?, override_values=?, original_calc_values=? WHERE id=?",
        (json.dumps(is_overridden), json.dumps(override_values), json.dumps(original_calc), line_item_id),
    )
    db.execute(
        """INSERT INTO field_override_log(quote_line_item_id, field_name, original_value, override_value, reason, user_id)
           VALUES(?,?,?,?,?,?)""",
        (line_item_id, field_name,
         str(original_calc.get(field_name)), str(override_value),
         reason, user_id),
    )
    db.commit()


def reset_override(
    line_item_id: int, field_name: str, user_id: int, db: sqlite3.Connection
) -> None:
    row = fetchone(
        db,
        "SELECT is_overridden, override_values, original_calc_values FROM quote_line_items WHERE id=?",
        (line_item_id,),
    )
    if not row:
        raise ValueError(f"line_item_id={line_item_id} not found")

    is_overridden = json.loads(row["is_overridden"] or "{}")
    override_values = json.loads(row["override_values"] or "{}")
    original_calc = json.loads(row["original_calc_values"] or "{}")

    original_value = original_calc.pop(field_name, None)
    is_overridden.pop(field_name, None)
    override_values.pop(field_name, None)

    db.execute(
        "UPDATE quote_line_items SET is_overridden=?, override_values=?, original_calc_values=? WHERE id=?",
        (json.dumps(is_overridden), json.dumps(override_values), json.dumps(original_calc), line_item_id),
    )
    db.execute(
        """INSERT INTO field_override_log(quote_line_item_id, field_name, original_value, override_value, reason, user_id)
           VALUES(?,?,?,?,?,?)""",
        (line_item_id, field_name, str(original_value), "RESET", "Reset to calculated value", user_id),
    )
    db.commit()

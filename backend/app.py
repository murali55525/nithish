from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)

# ── Database config (Kubernetes-safe) ─────────────────────
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "healthcare"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "host": os.getenv("DB_HOST", "database-service"),  # ✅ K8s service name
    "port": os.getenv("DB_PORT", "5432")
}

def get_db():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# ── Health ───────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy"})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

# ── Patients ─────────────────────────────────────────────
@app.route("/api/patients", methods=["GET"])
def get_patients():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, age, condition, risk FROM patients ORDER BY name"
    )
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.get_json(silent=True)
    required = ["name", "age", "condition", "risk"]

    if not data or not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO patients (name, age, condition, risk)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, age, condition, risk
            """,
            (data["name"], data["age"], data["condition"], data["risk"])
        )
        new_patient = cur.fetchone()
        conn.commit()
        return jsonify(new_patient), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route("/api/patients/<int:id>", methods=["PUT"])
def update_patient(id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no data"}), 400

    updates = []
    params = []

    for key in ["name", "age", "condition", "risk"]:
        if key in data:
            updates.append(f"{key} = %s")
            params.append(data[key])

    if not updates:
        return jsonify({"error": "no fields to update"}), 400

    params.append(id)

    conn = get_db()
    cur = conn.cursor()
    try:
        query = f"""
            UPDATE patients
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, name, age, condition, risk
        """
        cur.execute(query, params)
        updated = cur.fetchone()
        if not updated:
            conn.rollback()
            return jsonify({"error": "patient not found"}), 404
        conn.commit()
        return jsonify(updated)
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route("/api/patients/<int:id>", methods=["DELETE"])
def delete_patient(id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM patients WHERE id = %s RETURNING id",
            (id,)
        )
        if not cur.fetchone():
            conn.rollback()
            return jsonify({"error": "patient not found"}), 404
        conn.commit()
        return jsonify({"message": "deleted"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

# ── Appointments ─────────────────────────────────────────
@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, patient_id, patient_name, date_time, doctor, status
        FROM appointments
        ORDER BY date_time DESC
        """
    )
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json(silent=True)
    required = ["patient_id", "patient_name", "date_time", "doctor", "status"]

    if not data or not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO appointments
            (patient_id, patient_name, date_time, doctor, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, patient_id, patient_name, date_time, doctor, status
            """,
            (
                data["patient_id"],
                data["patient_name"],
                data["date_time"],
                data["doctor"],
                data["status"]
            )
        )
        new_appt = cur.fetchone()
        conn.commit()
        return jsonify(new_appt), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route("/api/appointments/<int:id>", methods=["PUT"])
def update_appointment(id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no data"}), 400

    updates = []
    params = []

    for key in ["patient_id", "patient_name", "date_time", "doctor", "status"]:
        if key in data:
            updates.append(f"{key} = %s")
            params.append(data[key])

    if not updates:
        return jsonify({"error": "no fields to update"}), 400

    params.append(id)

    conn = get_db()
    cur = conn.cursor()
    try:
        query = f"""
            UPDATE appointments
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, patient_id, patient_name, date_time, doctor, status
        """
        cur.execute(query, params)
        updated = cur.fetchone()
        if not updated:
            conn.rollback()
            return jsonify({"error": "appointment not found"}), 404
        conn.commit()
        return jsonify(updated)
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route("/api/appointments/<int:id>", methods=["DELETE"])
def delete_appointment(id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM appointments WHERE id = %s RETURNING id",
            (id,)
        )
        if not cur.fetchone():
            conn.rollback()
            return jsonify({"error": "appointment not found"}), 404
        conn.commit()
        return jsonify({"message": "deleted"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

# ── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

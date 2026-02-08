CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    condition TEXT,
    risk TEXT CHECK (risk IN ('Low','Medium','High'))
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE SET NULL,
    patient_name TEXT,
    date_time TIMESTAMP NOT NULL,
    doctor TEXT NOT NULL,
    status TEXT CHECK (status IN ('Pending','Confirmed','Completed','Cancelled')) DEFAULT 'Pending'
);
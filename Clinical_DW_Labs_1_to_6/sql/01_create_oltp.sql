DROP DATABASE IF EXISTS hospital_oltp;
CREATE DATABASE hospital_oltp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_oltp;

CREATE TABLE patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender VARCHAR(10),
    date_of_birth DATE,
    contact_number VARCHAR(30),
    address VARCHAR(255),
    registration_date DATE,
    insurance_provider VARCHAR(100),
    insurance_number VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE doctors (
    doctor_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    specialization VARCHAR(100),
    phone_number VARCHAR(30),
    years_experience INT,
    hospital_branch VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE appointments (
    appointment_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20),
    doctor_id VARCHAR(20),
    appointment_date DATE,
    appointment_time TIME,
    reason_for_visit VARCHAR(100),
    status VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE treatments (
    treatment_id VARCHAR(20) PRIMARY KEY,
    appointment_id VARCHAR(20),
    treatment_type VARCHAR(100),
    description VARCHAR(255),
    cost DECIMAL(12, 2),
    treatment_date DATE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE billing (
    bill_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20),
    treatment_id VARCHAR(20),
    bill_date DATE,
    amount DECIMAL(12, 2),
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (treatment_id) REFERENCES treatments(treatment_id)
);

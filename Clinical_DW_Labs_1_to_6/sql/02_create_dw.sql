DROP DATABASE IF EXISTS hospital_dw;
CREATE DATABASE hospital_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_dw;

CREATE TABLE Dim_Patient (
    Patient_Key INT AUTO_INCREMENT PRIMARY KEY,
    Anonymized_Patient_ID VARCHAR(64) UNIQUE NOT NULL,
    Age_Group VARCHAR(20),
    Gender VARCHAR(10),
    Location VARCHAR(255),
    Insurance_Tier VARCHAR(100)
);

CREATE TABLE Dim_Doctor (
    Doctor_Key INT AUTO_INCREMENT PRIMARY KEY,
    Doctor_ID VARCHAR(20) NOT NULL,
    Doctor_Name VARCHAR(100),
    Specialty VARCHAR(100),
    Hospital_Branch VARCHAR(100),
    Years_Experience INT,
    Effective_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Is_Current TINYINT(1) DEFAULT 1
);

CREATE TABLE Dim_Department (
    Department_Key INT AUTO_INCREMENT PRIMARY KEY,
    Department_Name VARCHAR(100) UNIQUE NOT NULL,
    Clinic_Room VARCHAR(50),
    Division VARCHAR(50)
);

CREATE TABLE Dim_Date (
    Date_Key INT PRIMARY KEY,
    Full_Date DATE NOT NULL,
    Day_Of_Week VARCHAR(15),
    `Month` INT,
    `Quarter` INT,
    `Year` INT,
    `Year_Month` VARCHAR(7),
    Shift VARCHAR(20),
    Is_Weekend TINYINT(1)
);

CREATE TABLE Dim_Diagnosis (
    Diagnosis_Key INT AUTO_INCREMENT PRIMARY KEY,
    ICD10_Code VARCHAR(20),
    Treatment_Type VARCHAR(100) UNIQUE NOT NULL,
    Disease_Category VARCHAR(100),
    Chronic_Indicator TINYINT(1)
);

-- ★ MỚI: Bảng chiều Dịch vụ y tế (Outpatient / Inpatient / Surgery / Emergency)
CREATE TABLE Dim_Service (
    Service_Key INT AUTO_INCREMENT PRIMARY KEY,
    Service_Code VARCHAR(20) NOT NULL,
    Service_Name VARCHAR(100),
    Service_Type VARCHAR(50)
);

CREATE TABLE Fact_Patient_Visits (
    Visit_Key INT AUTO_INCREMENT PRIMARY KEY,
    Appointment_ID VARCHAR(20) UNIQUE NOT NULL,
    Patient_Key INT NOT NULL,
    Doctor_Key INT NOT NULL,
    Department_Key INT NOT NULL,
    Date_Key INT NOT NULL,
    Diagnosis_Key INT NOT NULL,
    Service_Key INT NOT NULL,
    Waiting_Time_Minutes INT,
    Consultation_Duration INT,
    Length_Of_Stay_Days INT,
    Total_Cost DECIMAL(12, 2),
    Insurance_Covered_Amount DECIMAL(12, 2),
    Patient_Paid_Amount DECIMAL(12, 2),
    FOREIGN KEY (Patient_Key) REFERENCES Dim_Patient(Patient_Key),
    FOREIGN KEY (Doctor_Key) REFERENCES Dim_Doctor(Doctor_Key),
    FOREIGN KEY (Department_Key) REFERENCES Dim_Department(Department_Key),
    FOREIGN KEY (Date_Key) REFERENCES Dim_Date(Date_Key),
    FOREIGN KEY (Diagnosis_Key) REFERENCES Dim_Diagnosis(Diagnosis_Key),
    FOREIGN KEY (Service_Key) REFERENCES Dim_Service(Service_Key)
);

CREATE TABLE Staging_Doctors (
    Doctor_ID VARCHAR(20),
    Doctor_Name VARCHAR(100),
    Specialty VARCHAR(100),
    Hospital_Branch VARCHAR(100),
    Years_Experience INT,
    Source_System VARCHAR(50)
);

CREATE INDEX idx_fact_date ON Fact_Patient_Visits(Date_Key);
CREATE INDEX idx_fact_dept ON Fact_Patient_Visits(Department_Key);
CREATE INDEX idx_fact_diag ON Fact_Patient_Visits(Diagnosis_Key);
CREATE INDEX idx_fact_patient ON Fact_Patient_Visits(Patient_Key);
CREATE INDEX idx_fact_service ON Fact_Patient_Visits(Service_Key);
CREATE INDEX idx_doc_id_current ON Dim_Doctor(Doctor_ID, Is_Current);

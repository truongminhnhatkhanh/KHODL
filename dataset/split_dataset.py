from pathlib import Path
import pandas as pd


def split_healthcare_dataset() -> None:
    """Tách file healthcare_dataset.csv thành 5 bảng chuẩn hóa (CSV)."""
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "healthcare_dataset.csv"
    output_dir = base_dir / "split_tables"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    # Chuẩn hóa định dạng ngày sang YYYY-MM-DD
    date_cols = [
        "date_of_birth",
        "registration_date",
        "appointment_date",
        "treatment_date",
        "bill_date",
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

    tables = {
        "patients": (
            df[
                [
                    "patient_id",
                    "patient_first_name",
                    "patient_last_name",
                    "gender",
                    "date_of_birth",
                    "patient_phone",
                    "patient_address",
                    "registration_date",
                    "insurance_provider",
                    "insurance_number",
                    "patient_email",
                ]
            ]
            .rename(
                columns={
                    "patient_first_name": "first_name",
                    "patient_last_name": "last_name",
                    "patient_phone": "contact_number",
                    "patient_address": "address",
                    "patient_email": "email",
                }
            )
            .drop_duplicates(subset=["patient_id"])
        ),
        "doctors": (
            df[
                [
                    "doctor_id",
                    "doctor_first_name",
                    "doctor_last_name",
                    "specialization",
                    "doctor_phone",
                    "years_experience",
                    "hospital_branch",
                    "doctor_email",
                ]
            ]
            .rename(
                columns={
                    "doctor_first_name": "first_name",
                    "doctor_last_name": "last_name",
                    "doctor_phone": "phone_number",
                    "doctor_email": "email",
                }
            )
            .drop_duplicates(subset=["doctor_id"])
        ),
        "appointments": (
            df[
                [
                    "appointment_id",
                    "patient_id",
                    "doctor_id",
                    "appointment_date",
                    "appointment_time",
                    "reason_for_visit",
                    "appointment_status",
                ]
            ]
            .rename(columns={"appointment_status": "status"})
            .drop_duplicates(subset=["appointment_id"])
        ),
        "treatments": (
            df[
                [
                    "treatment_id",
                    "appointment_id",
                    "treatment_type",
                    "treatment_description",
                    "treatment_cost",
                    "treatment_date",
                ]
            ]
            .rename(
                columns={
                    "treatment_description": "description",
                    "treatment_cost": "cost",
                }
            )
            .drop_duplicates(subset=["treatment_id"])
        ),
        "billing": (
            df[
                [
                    "bill_id",
                    "patient_id",
                    "treatment_id",
                    "bill_date",
                    "billing_amount",
                    "payment_method",
                    "payment_status",
                ]
            ]
            .rename(columns={"billing_amount": "amount"})
            .drop_duplicates(subset=["bill_id"])
        ),
    }

    for name, table_df in tables.items():
        out_file = output_dir / f"{name}.csv"
        table_df.to_csv(out_file, index=False)
        print(f"Đã xuất {out_file} ({len(table_df)} dòng)")


if __name__ == "__main__":
    split_healthcare_dataset()

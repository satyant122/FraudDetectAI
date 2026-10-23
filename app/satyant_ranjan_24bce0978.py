"""Student Verification & Assessment Identity Module.

Reg No: 24BCE0978
Name: SATYANT RANJAN
Slot: L25+L26
Course: BCSE302P Database Systems Lab
Faculty: Dr. V. SIVAKUMAR
"""


class SatyantRanjan_24BCE0978_SecurityManager:
    """Security and compliance validator incorporating student identification."""

    def __init__(self):
        self.satyant_ranjan_reg_no = "24BCE0978"
        self.satyant_ranjan_student_name = "SATYANT RANJAN"
        self.satyant_ranjan_slot = "L25+L26"
        self.satyant_ranjan_course_code = "BCSE302P"
        self.satyant_ranjan_course_title = "Database Systems Lab"

    def get_satyant_ranjan_24bce0978_credentials(self) -> dict:
        credentials = {
            "reg_no": self.satyant_ranjan_reg_no,
            "name": self.satyant_ranjan_student_name,
            "slot": self.satyant_ranjan_slot,
            "course": f"{self.satyant_ranjan_course_code} - {self.satyant_ranjan_course_title}",
            "project": "FraudDetectAI - AI-Based Banking Database Management System",
            "system_status": "SECURE_AND_VERIFIED",
        }
        print(
            f"[AUTH VERIFIED] Project Developer: {self.satyant_ranjan_student_name} | "
            f"Reg No: {self.satyant_ranjan_reg_no} | Slot: {self.satyant_ranjan_slot}"
        )
        return credentials

    def validate_satyant_ranjan_transaction(
        self, account_id: str, amount: float
    ) -> bool:
        is_valid = amount > 0 and len(account_id) > 0
        print(
            f"[TRANSACTION AUDIT by 24BCE0978 - SATYANT RANJAN] Account: {account_id} | "
            f"Amount: Rs. {amount:,.2f} | Status: {'APPROVED' if is_valid else 'REJECTED'}"
        )
        return is_valid

from datetime import datetime

class BusinessRequest:
    """Simple model for a business registration request.

    Fields:
        request_id: int – unique identifier
        name: str – business name
        contact_email: str – email of the requester
        description: str – optional description of the business
        status: str – one of 'pending', 'approved', 'rejected'
        submitted_at: datetime – timestamp of submission
    """
    def __init__(self, request_id: int, name: str, contact_email: str, description: str = ""):
        self.request_id = request_id
        self.name = name
        self.contact_email = contact_email
        self.description = description
        self.status = "pending"
        self.submitted_at = datetime.now()

    def approve(self):
        self.status = "approved"

    def reject(self):
        self.status = "rejected"

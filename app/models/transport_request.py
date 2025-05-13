"""
Transport request system for equipment movement.
This module provides models and functionality for creating, tracking, and
managing equipment transportation requests.
"""
import os
import uuid
from datetime import datetime, timedelta
from app.models.json_utils import save_json, load_json, DateTimeEncoder

class TransportStatus:
    """Status constants for the transport request system"""
    REQUESTED = "requested"  # Initial state
    APPROVED = "approved"    # Request approved
    SCHEDULED = "scheduled"  # Transport scheduled
    IN_TRANSIT = "in_transit"  # Currently being transported
    COMPLETED = "completed"  # Transport completed
    CANCELLED = "cancelled"  # Transport cancelled

class TransportPriority:
    """Priority constants for transport requests"""
    LOW = "low"        # Routine move, not time-sensitive
    MEDIUM = "medium"  # Standard priority
    HIGH = "high"      # Urgent transport needed
    RUSH = "rush"      # Immediate transport required

class TransportType:
    """Type constants for different transport scenarios"""
    RELOCATION = "relocation"    # Moving to a new permanent location
    CALIBRATION = "calibration"  # Transport for calibration
    MAINTENANCE = "maintenance"  # Transport for maintenance/repair
    LOAN = "loan"                # Temporary loan to another location
    RETURN = "return"            # Return from loan/calibration/repair

class TransportRequest:
    """Represents a transport request in the system"""
    def __init__(self, equipment_id, origin, destination, requested_by, 
                 requested_date=None, special_instructions="",
                 transport_type=TransportType.RELOCATION,
                 priority=TransportPriority.MEDIUM, 
                 status=TransportStatus.REQUESTED):
        """Initialize a transport request.
        
        Args:
            equipment_id: ID of the equipment to transport
            origin: Origin location
            destination: Destination location
            requested_by: Username of requester
            requested_date: Requested date for transport (default: now + 1 day)
            special_instructions: Special handling instructions
            transport_type: Type of transport request
            priority: Priority level for the request
            status: Initial status
        """
        self.id = str(uuid.uuid4())
        self.equipment_id = equipment_id
        self.origin = origin
        self.destination = destination
        self.requested_by = requested_by
        self.transport_coordinator = None
        
        # Set requested date (default to next business day if not specified)
        if requested_date:
            self.requested_date = requested_date
        else:
            # Default to tomorrow
            self.requested_date = (datetime.now() + timedelta(days=1)).replace(
                hour=10, minute=0, second=0, microsecond=0
            )
            
        self.scheduled_date = None
        self.completion_date = None
        
        self.transport_type = transport_type
        self.priority = priority
        self.status = status
        self.special_instructions = special_instructions
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.comments = []
        
    def to_dict(self):
        """Convert transport request to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "origin": self.origin,
            "destination": self.destination,
            "requested_by": self.requested_by,
            "transport_coordinator": self.transport_coordinator,
            "requested_date": self.requested_date,
            "scheduled_date": self.scheduled_date,
            "completion_date": self.completion_date,
            "transport_type": self.transport_type,
            "priority": self.priority,
            "status": self.status,
            "special_instructions": self.special_instructions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "comments": self.comments
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a transport request from a dictionary"""
        transport_request = cls(
            equipment_id=data["equipment_id"],
            origin=data["origin"],
            destination=data["destination"],
            requested_by=data["requested_by"],
            transport_type=data.get("transport_type", TransportType.RELOCATION),
            priority=data.get("priority", TransportPriority.MEDIUM),
            status=data.get("status", TransportStatus.REQUESTED),
            special_instructions=data.get("special_instructions", "")
        )
        
        transport_request.id = data["id"]
        transport_request.transport_coordinator = data.get("transport_coordinator")
        
        # Parse datetime objects
        date_fields = ["requested_date", "scheduled_date", "completion_date", 
                       "created_at", "updated_at"]
        for date_field in date_fields:
            if data.get(date_field):
                try:
                    if isinstance(data[date_field], str):
                        setattr(transport_request, date_field, 
                                datetime.fromisoformat(data[date_field].replace('Z', '+00:00')))
                    else:
                        setattr(transport_request, date_field, data[date_field])
                except (ValueError, AttributeError):
                    # If parsing fails, keep the string
                    setattr(transport_request, date_field, data[date_field])
        
        transport_request.comments = data.get("comments", [])
        return transport_request


class TransportComment:
    """Represents a comment on a transport request"""
    def __init__(self, transport_id, comment, user):
        self.id = str(uuid.uuid4())
        self.transport_id = transport_id
        self.comment = comment
        self.user = user
        self.created_at = datetime.now()
        
    def to_dict(self):
        """Convert comment to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "transport_id": self.transport_id,
            "comment": self.comment,
            "user": self.user,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a comment from a dictionary"""
        comment = cls(
            transport_id=data["transport_id"],
            comment=data["comment"],
            user=data["user"]
        )
        
        comment.id = data["id"]
        
        # Parse datetime objects
        if data.get("created_at"):
            try:
                if isinstance(data["created_at"], str):
                    comment.created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                else:
                    comment.created_at = data["created_at"]
            except (ValueError, AttributeError):
                # If parsing fails, keep the string
                comment.created_at = data["created_at"]
        
        return comment


class TransportManager:
    """Manages transport requests for equipment"""
    def __init__(self, data_dir='app/data'):
        """Initialize the transport request manager"""
        self.data_dir = data_dir
        
        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Transport requests file
        self.transport_requests_file = os.path.join(data_dir, 'transport_requests.json')
        
        # Load data
        self.transport_requests = self._load_transport_requests()
        
    def _load_transport_requests(self):
        """Load transport requests from file"""
        transport_data = load_json(self.transport_requests_file)
        if transport_data:
            try:
                return {t["id"]: TransportRequest.from_dict(t) for t in transport_data}
            except Exception as e:
                print(f"Error parsing transport requests: {e}")
                return {}
        return {}
    
    def _save_transport_requests(self):
        """Save transport requests to file"""
        transport_data = [req.to_dict() for req in self.transport_requests.values()]
        save_json(transport_data, self.transport_requests_file)
    
    def create_transport_request(self, equipment_id, origin, destination, requested_by,
                              requested_date=None, special_instructions="", 
                              transport_type=TransportType.RELOCATION,
                              priority=TransportPriority.MEDIUM):
        """Create a new transport request"""
        transport_request = TransportRequest(
            equipment_id=equipment_id,
            origin=origin,
            destination=destination,
            requested_by=requested_by,
            requested_date=requested_date,
            special_instructions=special_instructions,
            transport_type=transport_type,
            priority=priority
        )
        
        self.transport_requests[transport_request.id] = transport_request
        
        # Save changes
        self._save_transport_requests()
        
        return transport_request
    
    def get_transport_request(self, request_id):
        """Get a specific transport request by ID"""
        return self.transport_requests.get(request_id)
    
    def update_transport_request(self, request_id, **kwargs):
        """Update a transport request"""
        transport_request = self.get_transport_request(request_id)
        if not transport_request:
            return None
        
        # Update request fields
        for key, value in kwargs.items():
            if hasattr(transport_request, key) and key not in ["id", "created_at"]:
                setattr(transport_request, key, value)
        
        # Update timestamps
        transport_request.updated_at = datetime.now()
        
        # Special handling for status changes
        if "status" in kwargs:
            if kwargs["status"] == TransportStatus.COMPLETED and not transport_request.completion_date:
                transport_request.completion_date = datetime.now()
            elif kwargs["status"] == TransportStatus.SCHEDULED and not transport_request.scheduled_date:
                # If moving to scheduled status with no scheduled date, use requested date
                transport_request.scheduled_date = transport_request.requested_date
        
        # Save changes
        self._save_transport_requests()
        
        return transport_request
    
    def add_comment(self, request_id, comment, user):
        """Add a comment to a transport request"""
        transport_request = self.get_transport_request(request_id)
        if not transport_request:
            return None
        
        transport_comment = TransportComment(
            transport_id=request_id,
            comment=comment,
            user=user
        )
        
        transport_request.comments.append(transport_comment.to_dict())
        transport_request.updated_at = datetime.now()
        
        # Save changes
        self._save_transport_requests()
        
        return transport_comment
    
    def get_requests_by_equipment(self, equipment_id):
        """Get all transport requests for a specific piece of equipment"""
        requests = []
        for request in self.transport_requests.values():
            if request.equipment_id == equipment_id:
                requests.append(request)
        
        # Sort by requested_date, soonest first
        requests.sort(key=lambda r: r.requested_date)
        return requests
    
    def get_requests_by_status(self, status):
        """Get all transport requests with a specific status"""
        requests = []
        for request in self.transport_requests.values():
            if request.status == status:
                requests.append(request)
        
        # Sort by requested_date
        requests.sort(key=lambda r: r.requested_date)
        return requests
    
    def get_requests_by_user(self, user, role="requested_by"):
        """Get all transport requests created by or assigned to a specific user"""
        requests = []
        for request in self.transport_requests.values():
            if role == "requested_by" and request.requested_by == user:
                requests.append(request)
            elif role == "transport_coordinator" and request.transport_coordinator == user:
                requests.append(request)
        
        # Sort by requested_date
        requests.sort(key=lambda r: r.requested_date)
        return requests
    
    def get_all_transport_requests(self, limit=None):
        """Get all transport requests, optionally limited to a certain number"""
        requests = list(self.transport_requests.values())
        
        # Sort by requested_date (soonest first)
        requests.sort(key=lambda r: r.requested_date)
        
        if limit and isinstance(limit, int) and limit > 0:
            requests = requests[:limit]
            
        return requests
    
    def get_pending_transport_requests(self):
        """Get all transport requests that are not completed or cancelled"""
        return [r for r in self.transport_requests.values() 
                if r.status not in [TransportStatus.COMPLETED, TransportStatus.CANCELLED]]
    
    def get_upcoming_transport_requests(self, days=7):
        """Get transport requests scheduled in the next X days"""
        cutoff_date = datetime.now() + timedelta(days=days)
        upcoming = []
        
        for request in self.transport_requests.values():
            # Skip completed/cancelled
            if request.status in [TransportStatus.COMPLETED, TransportStatus.CANCELLED]:
                continue
                
            # Use scheduled_date if available, otherwise requested_date
            check_date = request.scheduled_date or request.requested_date
            
            if check_date and check_date <= cutoff_date:
                upcoming.append(request)
                
        # Sort by date
        upcoming.sort(key=lambda r: r.scheduled_date or r.requested_date)
        return upcoming
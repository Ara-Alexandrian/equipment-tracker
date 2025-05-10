"""
Ticket system for equipment management
"""
import os
import uuid
from datetime import datetime
from app.models.json_utils import save_json, load_json, DateTimeEncoder

class TicketStatus:
    """Status constants for the ticket system"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority:
    """Priority constants for the ticket system"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketType:
    """Type constants for the ticket system"""
    ISSUE = "issue"
    REQUEST = "request"
    MAINTENANCE = "maintenance"
    CALIBRATION = "calibration"

class EquipmentCondition:
    """Equipment condition traffic light system"""
    NORMAL = "normal"  # Green - fully operational
    WARNING = "warning"  # Yellow - needs attention/troubleshooting
    CRITICAL = "critical"  # Red - out of service/needs repair

class Ticket:
    """Represents a ticket in the system"""
    def __init__(self, equipment_id, title, description, created_by, ticket_type=TicketType.ISSUE,
                 priority=TicketPriority.MEDIUM, status=TicketStatus.OPEN, 
                 equipment_condition=EquipmentCondition.NORMAL):
        self.id = str(uuid.uuid4())
        self.equipment_id = equipment_id
        self.title = title
        self.description = description
        self.created_by = created_by
        self.assigned_to = None
        self.ticket_type = ticket_type
        self.priority = priority
        self.status = status
        self.equipment_condition = equipment_condition
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.resolved_at = None
        self.closed_at = None
        self.comments = []
        
    def to_dict(self):
        """Convert ticket to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "ticket_type": self.ticket_type,
            "priority": self.priority,
            "status": self.status,
            "equipment_condition": self.equipment_condition,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "closed_at": self.closed_at,
            "comments": self.comments
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a ticket from a dictionary"""
        ticket = cls(
            equipment_id=data["equipment_id"],
            title=data["title"],
            description=data["description"],
            created_by=data["created_by"],
            ticket_type=data.get("ticket_type", TicketType.ISSUE),
            priority=data.get("priority", TicketPriority.MEDIUM),
            status=data.get("status", TicketStatus.OPEN),
            equipment_condition=data.get("equipment_condition", EquipmentCondition.NORMAL)
        )
        
        ticket.id = data["id"]
        ticket.assigned_to = data.get("assigned_to")
        
        # Parse datetime objects
        for date_field in ["created_at", "updated_at", "resolved_at", "closed_at"]:
            if data.get(date_field):
                try:
                    if isinstance(data[date_field], str):
                        setattr(ticket, date_field, datetime.fromisoformat(data[date_field].replace('Z', '+00:00')))
                    else:
                        setattr(ticket, date_field, data[date_field])
                except (ValueError, AttributeError):
                    # If parsing fails, keep the string
                    setattr(ticket, date_field, data[date_field])
        
        ticket.comments = data.get("comments", [])
        return ticket


class TicketComment:
    """Represents a comment on a ticket"""
    def __init__(self, ticket_id, comment, user):
        self.id = str(uuid.uuid4())
        self.ticket_id = ticket_id
        self.comment = comment
        self.user = user
        self.created_at = datetime.now()
        
    def to_dict(self):
        """Convert comment to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "comment": self.comment,
            "user": self.user,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a comment from a dictionary"""
        comment = cls(
            ticket_id=data["ticket_id"],
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


class TicketManager:
    """Manages tickets for equipment"""
    def __init__(self, data_dir='app/data'):
        """Initialize the ticket manager"""
        self.data_dir = data_dir
        
        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Tickets file
        self.tickets_file = os.path.join(data_dir, 'tickets.json')
        
        # Equipment conditions file - stores current condition of equipment
        self.conditions_file = os.path.join(data_dir, 'equipment_conditions.json')
        
        # Load data
        self.tickets = self._load_tickets()
        self.equipment_conditions = self._load_equipment_conditions()
        
    def _load_tickets(self):
        """Load tickets from file"""
        tickets_data = load_json(self.tickets_file)
        if tickets_data:
            try:
                return {t["id"]: Ticket.from_dict(t) for t in tickets_data}
            except Exception as e:
                print(f"Error parsing tickets: {e}")
                return {}
        return {}
    
    def _save_tickets(self):
        """Save tickets to file"""
        tickets_data = [ticket.to_dict() for ticket in self.tickets.values()]
        save_json(tickets_data, self.tickets_file)
            
    def _load_equipment_conditions(self):
        """Load equipment conditions from file"""
        return load_json(self.conditions_file)
    
    def _save_equipment_conditions(self):
        """Save equipment conditions to file"""
        save_json(self.equipment_conditions, self.conditions_file)
    
    def create_ticket(self, equipment_id, title, description, created_by, ticket_type=TicketType.ISSUE,
                     priority=TicketPriority.MEDIUM, equipment_condition=None):
        """Create a new ticket"""
        # Get the current condition from existing ticket if not specified
        if not equipment_condition:
            equipment_condition = self.get_equipment_condition(equipment_id)
        
        ticket = Ticket(
            equipment_id=equipment_id,
            title=title,
            description=description,
            created_by=created_by,
            ticket_type=ticket_type,
            priority=priority,
            equipment_condition=equipment_condition
        )
        
        self.tickets[ticket.id] = ticket
        
        # Update equipment condition based on the ticket
        self.update_equipment_condition(equipment_id, equipment_condition)
        
        # Save changes
        self._save_tickets()
        self._save_equipment_conditions()
        
        return ticket
    
    def get_ticket(self, ticket_id):
        """Get a specific ticket by ID"""
        return self.tickets.get(ticket_id)
    
    def update_ticket(self, ticket_id, **kwargs):
        """Update a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        # Update ticket fields
        for key, value in kwargs.items():
            if hasattr(ticket, key) and key not in ["id", "created_at"]:
                setattr(ticket, key, value)
        
        # Update timestamps
        ticket.updated_at = datetime.now()
        
        # Special handling for status changes
        if "status" in kwargs:
            if kwargs["status"] == TicketStatus.RESOLVED and not ticket.resolved_at:
                ticket.resolved_at = datetime.now()
            elif kwargs["status"] == TicketStatus.CLOSED and not ticket.closed_at:
                ticket.closed_at = datetime.now()
        
        # Update equipment condition if specified
        if "equipment_condition" in kwargs:
            self.update_equipment_condition(ticket.equipment_id, kwargs["equipment_condition"])
        
        # Save changes
        self._save_tickets()
        self._save_equipment_conditions()
        
        return ticket
    
    def add_comment(self, ticket_id, comment, user):
        """Add a comment to a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        ticket_comment = TicketComment(
            ticket_id=ticket_id,
            comment=comment,
            user=user
        )
        
        ticket.comments.append(ticket_comment.to_dict())
        ticket.updated_at = datetime.now()
        
        # Save changes
        self._save_tickets()
        
        return ticket_comment
    
    def get_tickets_by_equipment(self, equipment_id):
        """Get all tickets for a specific piece of equipment"""
        tickets = []
        for ticket in self.tickets.values():
            if ticket.equipment_id == equipment_id:
                tickets.append(ticket)
        
        # Sort by created_at, newest first
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        return tickets
    
    def get_tickets_by_status(self, status):
        """Get all tickets with a specific status"""
        tickets = []
        for ticket in self.tickets.values():
            if ticket.status == status:
                tickets.append(ticket)
        
        # Sort by created_at, newest first
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        return tickets
    
    def get_tickets_by_user(self, user, role="created_by"):
        """Get all tickets created by or assigned to a specific user"""
        tickets = []
        for ticket in self.tickets.values():
            if role == "created_by" and ticket.created_by == user:
                tickets.append(ticket)
            elif role == "assigned_to" and ticket.assigned_to == user:
                tickets.append(ticket)
        
        # Sort by created_at, newest first
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        return tickets
    
    def get_all_tickets(self, limit=None):
        """Get all tickets, optionally limited to a certain number"""
        tickets = list(self.tickets.values())
        
        # Sort by created_at, newest first
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        
        if limit and isinstance(limit, int) and limit > 0:
            tickets = tickets[:limit]
            
        return tickets
    
    def get_equipment_condition(self, equipment_id):
        """Get the current condition of a piece of equipment"""
        if equipment_id in self.equipment_conditions:
            return self.equipment_conditions[equipment_id]
        
        # Default to normal if not found
        return EquipmentCondition.NORMAL
    
    def update_equipment_condition(self, equipment_id, condition):
        """Update the condition of a piece of equipment"""
        if condition not in [EquipmentCondition.NORMAL, EquipmentCondition.WARNING, EquipmentCondition.CRITICAL]:
            condition = EquipmentCondition.NORMAL
            
        self.equipment_conditions[equipment_id] = condition
        self._save_equipment_conditions()
        
        return condition
    
    def get_equipment_with_condition(self, condition=None):
        """Get all equipment IDs with a specific condition, or all if not specified"""
        if condition:
            return [e_id for e_id, cond in self.equipment_conditions.items() if cond == condition]
        else:
            return list(self.equipment_conditions.keys())
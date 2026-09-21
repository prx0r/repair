from dataclasses import dataclass, field

@dataclass
class WorkflowStep:
    """A single step in a government workflow."""
    step_id: str
    description: str
    action_class: str          # AUTO / APPROVAL_REQUIRED / USER_HANDOFF
    
    # Source verification
    source_url: str = ""
    source_hash: str = ""      # hash of page content at verification
    verification_status: str = "NOT_VERIFIED"  # VERIFIED / NOT_VERIFIED / STALE
    verified_at: str = ""
    next_verification_due: str = ""
    verification_method: str = ""  # manual_check / api_check / automated
    
    # Requirements
    fee: float = 0
    deadline: str = ""
    required_documents: list = field(default_factory=list)
    
    # Failure modes
    failure_modes: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return self.__dict__.copy()

@dataclass
class Workflow:
    """A verified workflow for accomplishing a UK administrative task.
    
    This is Boring UK's core accumulated asset. Each workflow
    captures the confirmed sequence of steps to achieve an outcome.
    """
    workflow_id: str           # e.g. "manchester.move_house"
    task_name: str             # e.g. "Move house"
    authority: str             # e.g. "Manchester City Council"
    jurisdiction: str          # e.g. "GB", "England", "Scotland"
    
    # The workflow
    trigger: str = ""          # what initiates this workflow
    steps: list = field(default_factory=list)  # list of WorkflowStep
    
    # Verification
    verification_status: str = "CONCEPTUAL"  # VERIFIED / CONCEPTUAL / STALE
    last_verified: str = ""
    next_verification_due: str = ""
    verification_period_days: int = 30
    
    # Source tracking
    source_urls: list = field(default_factory=list)
    official_url: str = ""
    
    # Outcome tracking
    completion_evidence: list = field(default_factory=list)
    known_failure_modes: list = field(default_factory=list)
    historical_executions: int = 0
    
    # Metadata
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d['steps'] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.steps]
        return d

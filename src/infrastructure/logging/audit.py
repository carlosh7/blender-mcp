"""
blender-mcp-ultra — Audit Logger
Logs all security-relevant operations for audit trail.
"""
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Log levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data."""
    timestamp: str
    event_type: str
    level: LogLevel
    user_id: Optional[str]
    action: str
    details: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None


class AuditLogger:
    """
    Audit logger for security events.
    
    Features:
    - Structured JSON logging
    - Multiple log levels
    - File rotation
    - Optional remote logging
    """
    
    def __init__(
        self,
        log_dir: str = None,
        log_file: str = "audit.log",
        max_file_size_mb: int = 10,
        backup_count: int = 5
    ):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory for log files
            log_file: Name of log file
            max_file_size_mb: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        if log_dir is None:
            log_dir = os.path.expanduser("~/.config/blender-mcp-ultra/logs")
        
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, log_file)
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.backup_count = backup_count
        
        # Setup Python logger
        self.logger = logging.getLogger("blender-mcp-ultra.audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            self.log_path,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        
        # Statistics
        self.event_count = 0
        self.error_count = 0
    
    def log(self, event: AuditEvent) -> None:
        """
        Log an audit event.
        
        Args:
            event: Audit event to log
        """
        self.event_count += 1
        if not event.success:
            self.error_count += 1
        
        # Convert to dict and log as JSON
        event_dict = asdict(event)
        event_dict['level'] = event.level.value
        
        log_entry = json.dumps(event_dict, ensure_ascii=False)
        self.logger.info(log_entry)
    
    def log_code_execution(
        self,
        code: str,
        success: bool,
        output: str = "",
        error: str = None,
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log code execution event."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="code_execution",
            level=LogLevel.ERROR if not success else LogLevel.INFO,
            user_id=user_id,
            action="execute_code",
            details={
                'code_length': len(code),
                'code_preview': code[:100] + '...' if len(code) > 100 else code,
                'output_preview': output[:200] if output else '',
            },
            success=success,
            error_message=error,
            **kwargs
        )
        self.log(event)
    
    def log_security_violation(
        self,
        violation_type: str,
        details: Dict[str, Any],
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log security violation."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="security_violation",
            level=LogLevel.CRITICAL,
            user_id=user_id,
            action=violation_type,
            details=details,
            success=False,
            **kwargs
        )
        self.log(event)
    
    def log_tool_execution(
        self,
        tool_name: str,
        params: Dict[str, Any],
        success: bool,
        execution_time: float,
        error: str = None,
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log tool execution."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="tool_execution",
            level=LogLevel.ERROR if not success else LogLevel.INFO,
            user_id=user_id,
            action=tool_name,
            details={
                'params': params,
                'execution_time_ms': execution_time * 1000,
            },
            success=success,
            error_message=error,
            **kwargs
        )
        self.log(event)
    
    def log_connection(
        self,
        action: str,
        success: bool,
        details: Dict[str, Any] = None,
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log connection event."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="connection",
            level=LogLevel.INFO,
            user_id=user_id,
            action=action,
            details=details or {},
            success=success,
            **kwargs
        )
        self.log(event)
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        details: Dict[str, Any] = None,
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log error event."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="error",
            level=LogLevel.ERROR,
            user_id=user_id,
            action=error_type,
            details=details or {},
            success=False,
            error_message=error_message,
            **kwargs
        )
        self.log(event)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit logger statistics."""
        return {
            'total_events': self.event_count,
            'error_events': self.error_count,
            'success_rate': (
                (self.event_count - self.error_count) / self.event_count * 100
                if self.event_count > 0 else 0
            ),
            'log_file': self.log_path,
            'log_file_size_mb': os.path.getsize(self.log_path) / (1024 * 1024)
            if os.path.exists(self.log_path) else 0,
        }
    
    def read_logs(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        level: Optional[LogLevel] = None
    ) -> List[AuditEvent]:
        """Read recent audit logs."""
        events = []
        
        if not os.path.exists(self.log_path):
            return events
        
        with open(self.log_path, 'r') as f:
            for line in f:
                if len(events) >= limit:
                    break
                
                try:
                    data = json.loads(line.strip())
                    event = AuditEvent(
                        timestamp=data['timestamp'],
                        event_type=data['event_type'],
                        level=LogLevel(data['level']),
                        user_id=data.get('user_id'),
                        action=data['action'],
                        details=data.get('details', {}),
                        success=data['success'],
                        error_message=data.get('error_message'),
                        ip_address=data.get('ip_address'),
                        session_id=data.get('session_id')
                    )
                    
                    # Apply filters
                    if event_type and event.event_type != event_type:
                        continue
                    if level and event.level != level:
                        continue
                    
                    events.append(event)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return events


# Singleton instance
_logger = None

def get_logger(**kwargs) -> AuditLogger:
    """Get singleton audit logger instance."""
    global _logger
    if _logger is None:
        _logger = AuditLogger(**kwargs)
    return _logger

def log_code_execution(*args, **kwargs) -> None:
    """Convenience function to log code execution."""
    get_logger().log_code_execution(*args, **kwargs)

def log_security_violation(*args, **kwargs) -> None:
    """Convenience function to log security violation."""
    get_logger().log_security_violation(*args, **kwargs)

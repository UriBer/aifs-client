"""
Custom exceptions for the AIFS client application.
"""

from typing import Optional, Dict, Any


class AIFSException(Exception):
    """Base exception for AIFS client errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "AIFS_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AIFSConnectionError(AIFSException):
    """Raised when unable to connect to AIFS server."""
    
    def __init__(self, message: str = "Failed to connect to AIFS server", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AIFS_CONNECTION_ERROR", 503, details)


class AIFSAuthenticationError(AIFSException):
    """Raised when AIFS authentication fails."""
    
    def __init__(self, message: str = "AIFS authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AIFS_AUTHENTICATION_ERROR", 401, details)


class AssetNotFoundError(AIFSException):
    """Raised when an asset is not found."""
    
    def __init__(self, asset_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Asset with ID '{asset_id}' not found"
        super().__init__(message, "ASSET_NOT_FOUND", 404, details)


class AssetAccessDeniedError(AIFSException):
    """Raised when access to an asset is denied."""
    
    def __init__(self, asset_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Access denied to asset '{asset_id}'"
        super().__init__(message, "ASSET_ACCESS_DENIED", 403, details)


class InvalidFileTypeError(AIFSException):
    """Raised when an invalid file type is uploaded."""
    
    def __init__(self, file_type: str, allowed_types: list, details: Optional[Dict[str, Any]] = None):
        message = f"Invalid file type '{file_type}'. Allowed types: {', '.join(allowed_types)}"
        super().__init__(message, "INVALID_FILE_TYPE", 400, details)


class FileTooLargeError(AIFSException):
    """Raised when a file exceeds the size limit."""
    
    def __init__(self, file_size: int, max_size: int, details: Optional[Dict[str, Any]] = None):
        message = f"File size {file_size} bytes exceeds maximum allowed size {max_size} bytes"
        super().__init__(message, "FILE_TOO_LARGE", 413, details)


class UploadFailedError(AIFSException):
    """Raised when file upload fails."""
    
    def __init__(self, message: str = "File upload failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "UPLOAD_FAILED", 500, details)


class SearchError(AIFSException):
    """Raised when search operation fails."""
    
    def __init__(self, message: str = "Search operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SEARCH_ERROR", 500, details)


class RAGError(AIFSException):
    """Raised when RAG operation fails."""
    
    def __init__(self, message: str = "RAG operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RAG_ERROR", 500, details)


class OpenAIError(AIFSException):
    """Raised when OpenAI API operation fails."""
    
    def __init__(self, message: str = "OpenAI API error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "OPENAI_ERROR", 502, details)


class AuthenticationFailedError(AIFSException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_FAILED", 401, details)


class RateLimitExceededError(AIFSException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429, details)


class CloudProviderError(AIFSException):
    """Raised when cloud provider operation fails."""
    
    def __init__(self, provider: str, message: str = "Cloud provider operation failed", details: Optional[Dict[str, Any]] = None):
        full_message = f"{provider}: {message}"
        super().__init__(full_message, "CLOUD_PROVIDER_ERROR", 502, details)

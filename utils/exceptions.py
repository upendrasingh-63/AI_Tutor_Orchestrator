
# This file defines custom exception classes for the application.
# Using custom exceptions makes error handling more specific and the code more readable.

class OrchestratorException(Exception):
    """Base class for exceptions in this application."""
    pass

class ToolNotFoundException(OrchestratorException):
    """Raised when a requested tool cannot be found."""
    pass

class ParameterExtractionException(OrchestratorException):
    """Raised when the LLM fails to extract parameters correctly."""
    pass

class ToolExecutionException(OrchestratorException):
    """Raised when a tool fails to execute for any reason."""
    pass

class ClarificationNeededException(OrchestratorException):
    """
    A special case exception raised when the LLM determines it needs more
    information from the user to proceed.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

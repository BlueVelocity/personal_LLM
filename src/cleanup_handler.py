"""
Note: SIGHUP from Hyprland killactive may trigger cleanup.
Ollama's keep_alive timer will handle model unloading.
For immediate cleanup, use Ctrl+C or type the exit term (e.g. 'exit' or 'quit').
"""

import atexit
import signal
import sys
from typing import Callable


class CleanupHandler:
    """Handle graceful cleanup on various termination signals"""

    def __init__(self, cleanup_func: Callable[[], None]):
        """
        Args:
            cleanup_func: Function to call on cleanup
        """
        self.cleanup_func = cleanup_func
        self._cleanup_called = False

    def _cleanup(self):
        """Internal cleanup wrapper to prevent double-execution"""
        if not self._cleanup_called:
            self._cleanup_called = True
            self.cleanup_func()

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        signal_names = {
            signal.SIGHUP: "SIGHUP (terminal closed)",
            signal.SIGTERM: "SIGTERM (kill command)",
            signal.SIGINT: "SIGINT (Ctrl+C)",
        }
        if signum in signal_names:
            print(f"\nReceived {signal_names[signum]}")
        self._cleanup()
        sys.exit(0)

    def register(self):
        """Register all cleanup handlers"""
        # Register atexit for normal exits
        atexit.register(self._cleanup)

        # Register signal handlers
        signal.signal(signal.SIGHUP, self._signal_handler)  # Terminal closed
        signal.signal(signal.SIGTERM, self._signal_handler)  # Kill command
        signal.signal(signal.SIGINT, self._signal_handler)  # Ctrl+C

        return self


def register_cleanup(cleanup_func: Callable[[], None]) -> CleanupHandler:
    """
    Convenience function to register cleanup handler

    Args:
        cleanup_func: Function to call on cleanup

    Returns:
        CleanupHandler instance

    Example:
        register_cleanup(end_session)
    """
    handler = CleanupHandler(cleanup_func)
    handler.register()
    return handler

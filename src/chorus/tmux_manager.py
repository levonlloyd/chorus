"""Tmux session manager for Chorus."""

import os
import libtmux


class TmuxSessionManager:
    """Manages tmux sessions for Chorus workspaces."""
    
    def __init__(self, session_name="chorus"):
        self.session_name = session_name
        self.server = libtmux.Server()
    
    def create_session(self, git_repo_root, agent_command):
        """Create or attach to a tmux session with the Chorus layout.
        
        Args:
            git_repo_root: Path to the git repository root
            agent_command: Command to run for the agent pane
        """
        # Kill existing session if it exists
        existing_session = self.server.find_where({"session_name": self.session_name})
        if existing_session:
            existing_session.kill_session()
        
        # Create new session
        session = self.server.new_session(
            session_name=self.session_name,
            start_directory=git_repo_root,
            window_name="main"
        )
        
        # Get the default window
        window = session.windows[0]
        
        # Use tmux commands directly for precise control
        # Split window vertically (left/right) - 50/50
        window.cmd('split-window', '-h', '-c', git_repo_root)
        
        # Now we have 2 panes: left (pane 0) and right (pane 1)
        # Split the right pane horizontally twice
        window.cmd('select-pane', '-t', '1')  # Select right pane
        window.cmd('split-window', '-v', '-c', git_repo_root)  # Split it horizontally
        window.cmd('split-window', '-v', '-c', git_repo_root)  # Split again
        
        # Now we have 4 panes:
        # 0: left (agent)
        # 1: top right (editor)
        # 2: middle right (shell)
        # 3: bottom right (shell)
        
        # Get pane references
        panes = window.panes
        agent_pane = panes[0]
        editor_pane = panes[1]
        shell_pane_1 = panes[2]
        shell_pane_2 = panes[3]
        
        # Send commands to each pane
        agent_pane.send_keys(agent_command)
        editor_pane.send_keys(os.environ.get('EDITOR', 'vim'))
        shell_pane_1.send_keys("# Shell pane 1")
        shell_pane_2.send_keys("# Shell pane 2")
        
        # Focus on the agent pane
        agent_pane.select_pane()
        
        return session
    
    def attach_to_session(self):
        """Attach to the existing Chorus tmux session."""
        session = self.server.find_where({"session_name": self.session_name})
        if session:
            # Use tmux command to attach since libtmux doesn't have a direct attach method
            os.system(f"tmux attach-session -t {self.session_name}")
        else:
            raise ValueError(f"Session '{self.session_name}' not found")
    
    def session_exists(self):
        """Check if the Chorus session exists."""
        return self.server.find_where({"session_name": self.session_name}) is not None
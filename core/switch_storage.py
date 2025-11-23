#!/usr/bin/env python3
"""
Switch storage module - handles saving and loading switch configurations.
"""
import json
import os
import sys
from typing import List, Dict, Optional


class SwitchStorage:
    """Manages persistent storage of switch configurations."""
    
    def __init__(self, storage_file: Optional[str] = None):
        """
        Initialize storage with a file path.
        
        Args:
            storage_file: Path to JSON file for storage. If None, uses default location.
        """
        if storage_file is None:
            # Default storage location: user config directory
            if sys.platform == 'win32':
                config_dir = os.path.join(os.environ.get('APPDATA', ''), 'YaP-Switch-Manager')
            else:
                # Linux/Mac: use ~/.config
                config_dir = os.path.join(os.path.expanduser('~'), '.config', 'yap-switch-manager')
            
            # Create config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            storage_file = os.path.join(config_dir, 'switches.json')
        
        self.storage_file = storage_file
    
    def save_switch(self, name: str, url: str) -> bool:
        """
        Save a switch configuration.
        
        Args:
            name: Display name for the switch
            url: URL of the switch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            switches = self.load_switches()
            
            # Update existing or add new switch
            switches[name] = {
                'name': name,
                'url': url
            }
            
            # Write to file
            with open(self.storage_file, 'w') as f:
                json.dump(switches, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving switch: {e}")
            return False
    
    def load_switches(self) -> Dict[str, Dict[str, str]]:
        """
        Load all saved switches.
        
        Returns:
            Dictionary mapping switch names to their configurations
        """
        if not os.path.exists(self.storage_file):
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                # Ensure format is correct
                if isinstance(data, dict):
                    return data
                return {}
        except Exception as e:
            print(f"Error loading switches: {e}")
            return {}
    
    def delete_switch(self, name: str) -> bool:
        """
        Delete a saved switch.
        
        Args:
            name: Name of the switch to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            switches = self.load_switches()
            
            if name in switches:
                del switches[name]
                
                # Write updated list to file
                with open(self.storage_file, 'w') as f:
                    json.dump(switches, f, indent=2)
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting switch: {e}")
            return False
    
    def get_switch(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get a specific switch configuration.
        
        Args:
            name: Name of the switch
            
        Returns:
            Switch configuration dict or None if not found
        """
        switches = self.load_switches()
        return switches.get(name)
    
    def get_switch_names(self) -> List[str]:
        """
        Get list of all saved switch names.
        
        Returns:
            List of switch names
        """
        switches = self.load_switches()
        return sorted(list(switches.keys()))


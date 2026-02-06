"""
Template Manager for Lab Sheet Generator V2.0.0
Manages available templates and provides template selection interface
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Type


class BaseTemplate(ABC):
    """Abstract base class for lab sheet templates."""
    
    # Template metadata
    template_id: str = ""
    template_name: str = ""
    template_description: str = ""
    template_preview_image: str = None  # Optional path to preview image
    
    @abstractmethod
    def generate(self, student_name: str, student_id: str, module_name: str, 
                 module_code: str, sheet_label: str, logo_path: str = None) -> str:
        """
        Generate a lab sheet document.
        
        Args:
            student_name: Student's full name
            student_id: Student ID number
            module_name: Name of the module
            module_code: Module code
            sheet_label: Sheet label (e.g., "Practical 01", "Lab 05")
            logo_path: Path to the university logo image
            
        Returns:
            str: Path to the generated document
        """
        pass
    
    @abstractmethod
    def get_required_fonts(self) -> List[str]:
        """
        Get list of fonts required by this template.
        
        Returns:
            List of font names needed
        """
        pass
    
    def validate_fonts(self) -> Dict[str, bool]:
        """
        Check if required fonts are available.
        
        Returns:
            Dict mapping font names to availability status
        """
        from matplotlib import font_manager
        system_fonts = {f.name for f in font_manager.fontManager.ttflist}
        
        required = self.get_required_fonts()
        return {font: font in system_fonts for font in required}


class TemplateManager:
    """Manages available lab sheet templates."""
    
    def __init__(self):
        self._templates: Dict[str, Type[BaseTemplate]] = {}
        self._template_instances: Dict[str, BaseTemplate] = {}
    
    def register_template(self, template_class: Type[BaseTemplate]):
        """
        Register a new template.
        
        Args:
            template_class: Template class to register
        """
        instance = template_class()
        template_id = instance.template_id
        
        if not template_id:
            raise ValueError(f"Template {template_class.__name__} must have a template_id")
        
        self._templates[template_id] = template_class
        self._template_instances[template_id] = instance
    
    def get_template(self, template_id: str) -> BaseTemplate:
        """
        Get template instance by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            BaseTemplate instance
            
        Raises:
            KeyError: If template not found
        """
        if template_id not in self._template_instances:
            raise KeyError(f"Template '{template_id}' not found")
        
        return self._template_instances[template_id]
    
    def get_all_templates(self) -> Dict[str, BaseTemplate]:
        """
        Get all registered templates.
        
        Returns:
            Dict mapping template IDs to instances
        """
        return self._template_instances.copy()
    
    def get_template_list(self) -> List[Dict[str, str]]:
        """
        Get list of templates with metadata.
        
        Returns:
            List of dicts containing template info
        """
        templates = []
        for template_id, template in self._template_instances.items():
            templates.append({
                'id': template_id,
                'name': template.template_name,
                'description': template.template_description,
                'preview_image': template.template_preview_image
            })
        return templates
    
    def template_exists(self, template_id: str) -> bool:
        """Check if template exists."""
        return template_id in self._templates
    
    def generate_with_template(self, template_id: str, **kwargs) -> str:
        """
        Generate a lab sheet using specified template.
        
        Args:
            template_id: ID of template to use
            **kwargs: Arguments to pass to template generate method
            
        Returns:
            Path to generated document
        """
        template = self.get_template(template_id)
        return template.generate(**kwargs)


# Global template manager instance
_template_manager = None


def get_template_manager() -> TemplateManager:
    """Get the global template manager instance."""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager


def register_template(template_class: Type[BaseTemplate]):
    """Convenience function to register a template."""
    manager = get_template_manager()
    manager.register_template(template_class)
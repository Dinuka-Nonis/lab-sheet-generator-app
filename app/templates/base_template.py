from abc import ABC, abstractmethod

class BaseTemplate(ABC):
    template_id: str = ""
    template_name: str = ""
    template_description: str = ""
    
    @abstractmethod
    def generate(self, student_name, student_id, module_name, 
                 module_code, sheet_label, logo_path=None):
        pass
    
    @abstractmethod
    def get_required_fonts(self):
        pass
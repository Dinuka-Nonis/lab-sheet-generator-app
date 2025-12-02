import re

def validate_student_name(name):
    """
    Validate student name.
    
    Args:
        name: Student name string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name cannot be empty"
    
    if len(name.strip()) < 2:
        return False, "Name is too short"
    
    return True, ""

def validate_student_id(student_id):
    """
    Validate student ID.
    
    Args:
        student_id: Student ID string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not student_id or not student_id.strip():
        return False, "Student ID cannot be empty"
    
    # Remove spaces for validation
    student_id = student_id.strip().replace(" ", "")
    
    if len(student_id) < 5:
        return False, "Student ID is too short"
    
    return True, ""

def validate_module_name(module_name):
    """
    Validate module name.
    
    Args:
        module_name: Module name string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not module_name or not module_name.strip():
        return False, "Module name cannot be empty"
    
    if len(module_name.strip()) < 3:
        return False, "Module name is too short"
    
    return True, ""

def validate_module_code(module_code):
    """
    Validate module code.
    
    Args:
        module_code: Module code string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not module_code or not module_code.strip():
        return False, "Module code cannot be empty"
    
    # Module codes are typically alphanumeric
    code = module_code.strip()
    if len(code) < 4:
        return False, "Module code is too short"
    
    if not re.match(r'^[A-Z]{2}\d{4}$', code):
        return False, "Module code should be in format: XX0000 (e.g., SE2052)"
    
    return True, ""

def validate_practical_number(practical_num):
    """
    Validate practical number.
    
    Args:
        practical_num: Practical number (int or string)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        num = int(practical_num)
        if num < 1 or num > 99:
            return False, "Practical number should be between 1 and 99"
        return True, ""
    except (ValueError, TypeError):
        return False, "Practical number must be a valid number"
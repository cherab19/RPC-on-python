"""IDL (Interface Definition Language) - Parser and code generator"""

from .parser import IDLParser
from .generator import CodeGenerator

__all__ = ["IDLParser", "CodeGenerator"]

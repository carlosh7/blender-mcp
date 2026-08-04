"""
blender-mcp — Voice Control
Control por voz para blender-mcp-ultra.
"""
try:
    import bpy
except ImportError:
    bpy = None

import json
import os


# ═══════════════════════════════════════════════════════════════
# VOICE COMMANDS
# ═══════════════════════════════════════════════════════════════

VOICE_COMMANDS = {
    "create": ["crear", "create", "generate", "make", "add"],
    "delete": ["eliminar", "delete", "remove", "clear"],
    "move": ["mover", "move", "position", "place"],
    "rotate": ["rotar", "rotate", "spin", "turn"],
    "scale": ["escalar", "scale", "resize", "resize"],
    "color": ["color", "color", "paint", "dye"],
    "material": ["material", "texture", "surface"],
    "animate": ["animar", "animate", "motion", "move"],
    "export": ["exportar", "export", "save", "download"],
    "render": ["render", "renderizar", "draw"],
    "analyze": ["analizar", "analyze", "check", "verify"],
}


def parse_voice_command(transcript):
    """
    Parsear comando de voz.
    
    Args:
        transcript: Texto transcrito del audio
    
    Returns:
        dict con comando parseado
    """
    result = {
        "action": "unknown",
        "object": None,
        "parameters": {},
        "confidence": 0.0,
    }
    
    transcript_lower = transcript.lower()
    
    # Detectar acción
    for action, keywords in VOICE_COMMANDS.items():
        for keyword in keywords:
            if keyword in transcript_lower:
                result["action"] = action
                result["confidence"] = 0.8
                break
    
    # Detectar objeto
    object_keywords = {
        "cubo": "cube", "cube": "cube",
        "esfera": "sphere", "sphere": "sphere", "bola": "sphere",
        "cilindro": "cylinder", "cylinder": "cylinder",
        "cono": "cone", "cone": "cone",
        "silla": "chair", "chair": "chair",
        "mesa": "table", "table": "table",
        "casa": "house", "house": "house",
        "perro": "dog", "dog": "dog",
        "gato": "cat", "cat": "cat",
    }
    
    for keyword, obj_type in object_keywords.items():
        if keyword in transcript_lower:
            result["object"] = obj_type
            result["confidence"] = 0.9
            break
    
    # Detectar color
    color_keywords = {
        "rojo": (0.8, 0.1, 0.1), "red": (0.8, 0.1, 0.1),
        "azul": (0.1, 0.1, 0.8), "blue": (0.1, 0.1, 0.8),
        "verde": (0.1, 0.7, 0.1), "green": (0.1, 0.7, 0.1),
        "amarillo": (0.9, 0.9, 0.1), "yellow": (0.9, 0.9, 0.1),
        "negro": (0.05, 0.05, 0.05), "black": (0.05, 0.05, 0.05),
        "blanco": (0.9, 0.9, 0.9), "white": (0.9, 0.9, 0.9),
    }
    
    for keyword, color in color_keywords.items():
        if keyword in transcript_lower:
            result["parameters"]["color"] = color
            break
    
    # Detectar tamaño
    size_keywords = {
        "pequeño": 0.5, "small": 0.5,
        "mediano": 1.0, "medium": 1.0,
        "grande": 2.0, "large": 2.0,
    }
    
    for keyword, size in size_keywords.items():
        if keyword in transcript_lower:
            result["parameters"]["size"] = size
            break
    
    return result


def execute_voice_command(transcript):
    """
    Ejecutar comando de voz.
    
    Args:
        transcript: Texto transcrito del audio
    
    Returns:
        dict con resultado
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    # Parsear comando
    parsed = parse_voice_command(transcript)
    
    print(f"\nVoice Command: {transcript}")
    print(f"Parsed: {parsed}")
    
    # Ejecutar acción
    action = parsed["action"]
    
    if action == "create":
        # Crear objeto
        obj_type = parsed.get("object", "cube")
        params = {
            "shape": obj_type,
            "size": parsed.get("parameters", {}).get("size", 1.0),
            "color": parsed.get("parameters", {}).get("color", (0.5, 0.5, 0.5)),
        }
        
        from .ai_integration import _create_generic
        obj = _create_generic(params)
        
        if obj:
            return {"success": True, "object": obj.name, "action": "create"}
        else:
            return {"error": "Failed to create object"}
    
    elif action == "analyze":
        # Analizar escena
        from ..perception import perception_system
        result = perception_system.analyze_scene()
        return {"success": True, "analysis": result["summary"]}
    
    elif action == "export":
        # Exportar
        from ..export import export_engine
        filepath = "/tmp/voice_export.glb"
        result = export_engine.smart_export(filepath, "GLB")
        return {"success": result.get("success", False), "filepath": filepath}
    
    else:
        return {"error": f"Unknown action: {action}"}


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_voice_commands():
    """Listar comandos de voz disponibles"""
    return VOICE_COMMANDS

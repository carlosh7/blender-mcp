"""
blender-mcp — Expert Knowledge & Standards
Provides standard dimensions and functional rules to the AI.
"""
import json
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)

# Base de datos de estándares humanos y técnicos (Matrix Download)
STANDARDS = {
    "arcade_machine": {
        "overall": {"height": 1.8, "width": 0.7, "depth": 0.8},
        "components": {
            "control_panel": {"height_from_floor": 0.95, "depth": 0.4},
            "screen": {"size_diagonal_inches": 24, "tilt_degrees": 20},
            "button": {"diameter": 0.028, "height": 0.01},
            "joystick": {"ball_diameter": 0.035, "shaft_height": 0.06}
        },
        "rules": [
            "Buttons must be children of or snapped to the Control Panel surface.",
            "Screen should be at eye level (approx 1.4m - 1.6m from floor)."
        ]
    },
    "table": {
        "overall": {"height": 0.75, "width": 1.2, "depth": 0.8},
        "rules": ["Surface must be horizontal (Z-up normal)."]
    },
    "chair": {
        "overall": {"seat_height": 0.45, "back_rest_height": 0.9},
        "rules": ["Seat must be at 0.45m for ergonomic comfort."]
    },
    "door": {
        "overall": {"height": 2.1, "width": 0.9, "depth": 0.04},
        "rules": ["Standard clearance is 2.1m."]
    },
    "av_truss_f34": {
        "overall": {"section": 0.29, "main_tube_dia": 0.05},
        "variants": {"1m": 1.0, "2m": 2.0, "3m": 3.0},
        "rules": ["Connect units using conical couplers.", "Always snap to 0.29m grid."]
    },
    "av_led_panel": {
        "overall": {"width": 0.5, "height": 0.5, "depth": 0.075},
        "pixel_pitch": "3.9mm",
        "rules": ["Snap in perfect X-Z grid.", "Always use 0.5m increments."]
    },
    "av_moving_head": {
        "overall": {"height": 0.81, "width": 0.48, "depth": 0.33},
        "weight_kg": 36,
        "rules": ["Attach to av_truss using clamps.", "Allow 1m clearance for rotation."]
    },
    "av_mixer_cl5": {
        "overall": {"width": 1.05, "depth": 0.67, "height": 0.3},
        "rules": ["Place on a stable desk or 19-inch rack adapter."]
    },
    "human_reference": {
        "overall": {"height": 1.75, "shoulder_width": 0.45},
        "rules": ["Use for scale validation only."]
    }
}

def register_tools(mcp):
    @mcp.tool(**RO())
    def get_standard_dimensions(category: str) -> str:
        """Returns real-world standard dimensions and functional rules for a given category.
        Consulta las dimensiones estándar y reglas funcionales (Trinity Matrix Download).
        Categorías disponibles: arcade_machine, table, chair, door, human_reference.
        """
        data = STANDARDS.get(category.lower())
        if not data:
            return json.dumps({
                "error": f"Categoría '{category}' no encontrada.",
                "available": list(STANDARDS.keys())
            })
        return json.dumps(data, indent=2)

    @mcp.tool(**RO())
    def validate_human_scale(object_type: str, dimensions: list[float]) -> str:
        """Validates if the provided dimensions for an object type are within reasonable human-scale bounds.
        Verifica si las dimensiones [x, y, z] son realistas para un humano.
        Retorna advertencias si el objeto es demasiado grande o pequeño.
        """
        std = STANDARDS.get(object_type.lower())
        if not std:
            return "No hay estándar para validar este objeto."
        
        target = std["overall"]
        warnings = []
        # Comparar Z (altura)
        if "height" in target:
            if dimensions[2] > target["height"] * 1.5:
                warnings.append(f"Altura crítica: {dimensions[2]}m es mucho mayor al estándar {target['height']}m.")
            elif dimensions[2] < target["height"] * 0.5:
                warnings.append(f"Altura crítica: {dimensions[2]}m es demasiado pequeña.")
        
        return json.dumps({
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "recommendation": f"Usa get_standard_dimensions('{object_type}') para valores precisos."
        })

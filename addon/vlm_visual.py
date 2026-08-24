"""
blender-mcp — Visual VLM Loop
Bucle visual para evaluación estética con Vision-Language Models.

Captura viewport, envía a modelo de visión multimodal, recibe feedback.
"""

import base64
import json
import os
import time

import bpy

# ═══════════════════════════════════════════════════════════════
# VLM CONFIGURATION
# ═══════════════════════════════════════════════════════════════

VLM_PROVIDERS = {
    "ollama": {
        "endpoint": "http://localhost:11434/api/generate",
        "model": "llava:latest",
        "supports_images": True,
    },
    "openai": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o",
        "supports_images": True,
    },
    "claude": {
        "endpoint": "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "supports_images": True,
    },
}


# ═══════════════════════════════════════════════════════════════
# CAPTURE
# ═══════════════════════════════════════════════════════════════


def capture_viewport(filepath: str | None = None, resolution: int = 800) -> str | None:
    """
    Capturar viewport actual como imagen.

    Args:
        filepath: Ruta donde guardar (None = temporal)
        resolution: Resolución máxima

    Returns:
        Path a la imagen capturada
    """
    if filepath is None:
        temp_dir = "/tmp/blender_mcp_vlm"
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, f"capture_{int(time.time())}.png")

    try:
        # Get active window and 3D area
        window = bpy.context.window if bpy.context.window else bpy.context.window_manager.windows[0]
        screen = window.screen
        area = next((a for a in screen.areas if a.type == "VIEW_3D"), None)

        if not area:
            print("[vlm] No 3D viewport found")
            return None

        # Capture
        with bpy.context.temp_override(window=window, screen=screen, area=area):
            bpy.ops.screen.screenshot_area(filepath=filepath)

        # Resize if needed
        if os.path.exists(filepath):
            img = bpy.data.images.load(filepath)
            if max(img.size) > resolution:
                scale = resolution / max(img.size)
                img.scale(int(img.size[0] * scale), int(img.size[1] * scale))
                img.save()

            return filepath

        return None

    except Exception as e:
        print(f"[vlm] Capture failed: {e}")
        return None


def capture_to_base64(filepath: str) -> str | None:
    """
    Convertir imagen a base64 para envío a API.

    Args:
        filepath: Ruta de la imagen

    Returns:
        String base64 de la imagen
    """
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"[vlm] Base64 conversion failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# VLM ANALYSIS
# ═══════════════════════════════════════════════════════════════


def analyze_with_vlm(image_path: str, prompt: str, provider: str = "ollama") -> dict:
    """
    Enviar imagen a VLM para análisis.

    Args:
        image_path: Ruta de la imagen
        prompt: Pregunta/instrucción para el VLM
        provider: Proveedor (ollama, openai, claude)

    Returns:
        Dict con análisis del VLM
    """
    if provider not in VLM_PROVIDERS:
        return {"error": f"Unknown provider: {provider}"}

    config = VLM_PROVIDERS[provider]

    # Convert image to base64
    image_b64 = capture_to_base64(image_path)
    if not image_b64:
        return {"error": "Failed to encode image"}

    # Prepare request based on provider
    if provider == "ollama":
        return _analyze_ollama(image_b64, prompt, config)
    elif provider == "openai":
        return _analyze_openai(image_b64, prompt, config)
    elif provider == "claude":
        return _analyze_claude(image_b64, prompt, config)

    return {"error": "Provider not implemented"}


def _analyze_ollama(image_b64: str, prompt: str, config: dict) -> dict:
    """Analyze with Ollama (llava)."""
    import urllib.request

    payload = {
        "model": config["model"],
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
    }

    try:
        req = urllib.request.Request(
            config["endpoint"],
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
            return {
                "provider": "ollama",
                "model": config["model"],
                "analysis": result.get("response", ""),
                "success": True,
            }
    except Exception as e:
        return {"error": str(e), "success": False}


def _analyze_openai(image_b64: str, prompt: str, config: dict) -> dict:
    """Analyze with OpenAI GPT-4o."""
    import urllib.request

    payload = {
        "model": config["model"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ],
        "max_tokens": 1000,
    }

    try:
        req = urllib.request.Request(
            config["endpoint"],
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
            return {
                "provider": "openai",
                "model": config["model"],
                "analysis": result["choices"][0]["message"]["content"],
                "success": True,
            }
    except Exception as e:
        return {"error": str(e), "success": False}


def _analyze_claude(image_b64: str, prompt: str, config: dict) -> dict:
    """Analyze with Claude."""
    import urllib.request

    payload = {
        "model": config["model"],
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    try:
        req = urllib.request.Request(
            config["endpoint"],
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
            return {
                "provider": "claude",
                "model": config["model"],
                "analysis": result["content"][0]["text"],
                "success": True,
            }
    except Exception as e:
        return {"error": str(e), "success": False}


# ═══════════════════════════════════════════════════════════════
# VISUAL FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════════

AESTHETIC_PROMPTS = {
    "composition": "Analyze the composition of this 3D scene. Is it balanced? Are there any objects floating or misaligned? Suggest improvements.",
    "lighting": "Analyze the lighting in this 3D scene. Is it too dark/bright? Are there harsh shadows? Suggest improvements.",
    "materials": "Analyze the materials and colors in this 3D scene. Do they work well together? Are there any clashing colors? Suggest improvements.",
    "overall": "Rate this 3D scene from 1-10 on overall quality. List specific issues and suggestions for improvement.",
}


def visual_feedback_loop(
    prompt_type: str = "overall", provider: str = "ollama", max_iterations: int = 3
) -> dict:
    """
    Ejecutar bucle de retroalimentación visual.

    Args:
        prompt_type: Tipo de análisis (composition, lighting, materials, overall)
        provider: Proveedor VLM
        max_iterations: Máximo de iteraciones

    Returns:
        Dict con análisis y sugerencias
    """
    prompt = AESTHETIC_PROMPTS.get(prompt_type, AESTHETIC_PROMPTS["overall"])

    feedback_history = []

    for i in range(max_iterations):
        # Capture viewport
        image_path = capture_viewport()
        if not image_path:
            return {"error": "Failed to capture viewport", "iterations": i}

        # Analyze with VLM
        result = analyze_with_vlm(image_path, prompt, provider)

        feedback_history.append(
            {
                "iteration": i + 1,
                "image_path": image_path,
                "analysis": result,
            }
        )

        # Check if analysis succeeded
        if not result.get("success", False):
            break

    return {
        "iterations": len(feedback_history),
        "feedback": feedback_history,
        "provider": provider,
        "prompt_type": prompt_type,
    }


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def quick_scene_check(provider: str = "ollama") -> dict:
    """
    Verificación rápida de la escena.

    Args:
        provider: Proveedor VLM

    Returns:
        Dict con análisis rápido
    """
    return visual_feedback_loop("overall", provider, max_iterations=1)


def composition_check(provider: str = "ollama") -> dict:
    """Verificar composición de la escena."""
    return visual_feedback_loop("composition", provider, max_iterations=1)


def lighting_check(provider: str = "ollama") -> dict:
    """Verificar iluminación de la escena."""
    return visual_feedback_loop("lighting", provider, max_iterations=1)

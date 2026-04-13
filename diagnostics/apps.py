"""
diagnostics/apps.py
Loads the CNN model once at Django startup (only in worker process).
FR-08: CNN model is loaded once and reused per request — never reloaded.
Reference: .agent/ohms.md — Section 8 (CNN Model), Section 9 (Project Structure)
"""
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class DiagnosticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diagnostics'
    verbose_name = 'CT Diagnostics & CNN Inference'

    def ready(self):
        """
        Called once when Django starts. Loads the CNN model into memory.
        Uses a guard to avoid double-loading with Django's auto-reloader.

        At Step 9: set MODEL_PATH to the real .h5 or .pt file.
        """
        import os
        # Prevent double load during Django dev server reload
        if os.environ.get('RUN_MAIN') != 'true' and not os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('test'):
            return

        from django.conf import settings
        from diagnostics.cnn_service import load_cnn_model

        model_path = settings.BASE_DIR / 'diagnostics' / 'ml_models' / 'cardiac_cnn.h5'

        if model_path.exists():
            logger.info(f"[Diagnostics] Loading CNN model from {model_path}")
            load_cnn_model(str(model_path))
        else:
            # Stub mode — model file not yet trained. Pipeline still functional.
            logger.warning(
                "[Diagnostics] CNN model file not found at %s. "
                "Running in STUB mode — predictions are hardcoded. "
                "Train and place model at this path for Step 9.", model_path
            )

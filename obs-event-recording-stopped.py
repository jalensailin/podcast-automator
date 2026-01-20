import obspython as obs  # type: ignore
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_PODCAST_SCRIPT = os.path.join(SCRIPT_DIR, "podcast-automation.py")

SKIP_SCENE_SUFFIX = "-x"


def script_description():
    return (
        "After recording ends, runs the script to convert the recorded video "
        "to audio and upload to the server, but only if the active scene "
        "does not end with '-x'."
    )


def script_load(settings):
    obs.script_log(obs.LOG_INFO, "Script loaded: 'recording-stopped.py'.")
    obs.obs_frontend_add_event_callback(on_event)


def on_event(event):
    if event != obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        return

    scene_source = obs.obs_frontend_get_current_scene()
    if not scene_source:
        obs.script_log(obs.LOG_WARNING, "No current scene found.")
        return

    try:
        scene_name = obs.obs_source_get_name(scene_source)  # type: str

        obs.script_log(obs.LOG_INFO, f"Recording stopped on scene: {scene_name}.")

        if scene_name.endswith(SKIP_SCENE_SUFFIX):
            obs.script_log(
                obs.LOG_INFO,
                f"Scene ends with '{SKIP_SCENE_SUFFIX}', skipping script.",
            )
            return

        result = subprocess.run(
            [sys.executable, CREATE_PODCAST_SCRIPT],
            capture_output=True,
            text=True,
        )

        obs.script_log(obs.LOG_INFO, f"Script stdout: {result.stdout}.")
        if result.stderr:
            obs.script_log(obs.LOG_ERROR, f"Script stderr: {result.stderr}.")

        obs.script_log(obs.LOG_INFO, f"Executed: {CREATE_PODCAST_SCRIPT}.")

    except Exception as e:
        obs.script_log(obs.LOG_ERROR, f"Failed to run script: {e}.")

    finally:
        # IMPORTANT: release OBS source references
        obs.obs_source_release(scene_source)


def script_unload():
    obs.obs_frontend_remove_event_callback(on_event)

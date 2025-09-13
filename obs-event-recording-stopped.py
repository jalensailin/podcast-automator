import obspython as obs  # type: ignore
import subprocess
import sys
import os

# Path to the external Python script you want to run
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_PODCAST_SCRIPT = os.path.join(SCRIPT_DIR, "podcast-automation.py")


def script_description():
    return "After recording ends, runs the script to convert the recorded video to audio, and upload to the server for the podcast."


def script_load(settings):
    obs.script_log(obs.LOG_INFO, "Script loaded: 'recording-stopped.py'")
    obs.obs_frontend_add_event_callback(on_event)


def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        try:
            # Run the other script with the same Python executable OBS is using
            result = subprocess.run(
                [sys.executable, CREATE_PODCAST_SCRIPT], capture_output=True, text=True
            )
            obs.script_log(obs.LOG_INFO, f"Script stdout: {result.stdout}")
            obs.script_log(obs.LOG_ERROR, f"Script stderr: {result.stderr}")
            obs.script_log(obs.LOG_INFO, f"Executed: {CREATE_PODCAST_SCRIPT}")
        except Exception as e:
            obs.script_log(obs.LOG_ERROR, f"Failed to run script: {e}")


def script_unload():
    obs.obs_frontend_remove_event_callback(on_event)

# fraud_viz.py
import streamlit.web.bootstrap
import sys
import os

# This is needed for PyInstaller to work with Streamlit
if getattr(sys, 'frozen', False):
    import streamlit.runtime.scriptrunner.magic_funcs
    import streamlit.runtime.scriptrunner.script_runner
    import streamlit.web.server.server
    import streamlit.web.server.server_util
    import streamlit.runtime.credentials
    import streamlit.runtime.media_file_manager

def run_app():
    # Get the directory containing the executable
    if getattr(sys, 'frozen', False):
        app_path = os.path.join(sys._MEIPASS, "app.py")
    else:
        app_path = "app.py"
    
    sys.argv = ["streamlit", "run", app_path, "--server.headless", "true", "--global.developmentMode", "false"]
    streamlit.web.bootstrap.run()

if __name__ == "__main__":
    run_app()
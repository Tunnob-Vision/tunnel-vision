import os
import sys
import subprocess

os.environ["OPENCV_DISABLE_QT"] = "1"
os.environ["QT_QPA_PLATFORM"] = "offscreen"

if 'cv2' not in sys.modules:
    try:
        try:
            from importlib.metadata import distributions
            installed_packages = {dist.metadata['Name']: dist for dist in distributions()}
        except ImportError:
            import pkg_resources
            installed_packages = {pkg.key: pkg for pkg in pkg_resources.working_set}

        has_opencv = 'opencv-python' in installed_packages
        has_headless = 'opencv-python-headless' in installed_packages

        if has_opencv and has_headless:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                if 'cv2' in sys.modules:
                    del sys.modules['cv2']
            except Exception:
                pass
    except Exception:
        pass

from views import upload_page, confirmation_page
import streamlit as st

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = None

if st.session_state['current_page'] is None:
    if st.button("Upload Page"):
        st.session_state['current_page'] = 'upload'
        st.rerun()

    if st.button("Confirmation Page"):
        st.session_state['current_page'] = 'confirmation'
        st.rerun()
else:
    if st.session_state['current_page'] == 'upload':
        if st.button("← Back"):
            st.session_state['current_page'] = None
            st.rerun()
        upload_page.show_upload_page()
    elif st.session_state['current_page'] == 'confirmation':
        if st.button("← Back"):
            st.session_state['current_page'] = None
            st.rerun()
        confirmation_page.show_confirmation_page()

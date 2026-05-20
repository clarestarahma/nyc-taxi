import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from nyc_taxi.pipeline.step_05_dashboard.app import streamlit_pages
    streamlit_pages()
    
    # ATAU jika ingin langsung menjalankan file tersebut:
    # with open("src/nyc_taxi/pipeline/step_05_dashboard/app.py") as f:
    #     code = compile(f.read(), "app.py", "exec")
    #     exec(code, globals())
except Exception as e:
    import streamlit as st
    st.error(f"Gagal memuat dashboard: {e}")
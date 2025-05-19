import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import zipfile
import tempfile
import shutil

st.set_page_config(layout="wide")
st.title("🧬 PCR Viewer – ZIP Upload + Kanalvergleich")

# 📤 Upload ZIP
uploaded_zip = st.file_uploader("📂 Lade eine ZIP-Datei mit deinen Positionsordnern hoch", type="zip")

if uploaded_zip:
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "data.zip")

    # ZIP speichern
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())

    # Entpacken
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    st.success("✅ ZIP erfolgreich entpackt.")

    # Sensorauswahl
    sensor_list = [f"{i:02d}" for i in range(17)]
    farbtoene = ["FAM", "HEX", "ROX", "CY5", "CY5_5"]

    col1, col2 = st.columns(2)
    selected_sensor = col1.selectbox("🔢 Sensor wählen", sensor_list)
    selected_color = col2.selectbox("🎨 Farbton wählen", farbtoene)

    # Zielsuffix zur Erkennung der Dateien
    file_matches = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            expected_filename_part = f"Sensor_{selected_sensor}_{selected_color}.csv"
            if file == expected_filename_part:
                full_path = os.path.join(root, file)
                file_matches.append(full_path)

    if not file_matches:
        st.warning("⚠️ Keine passenden Dateien gefunden.")
        shutil.rmtree(temp_dir)
        st.stop()

    # Kanäle, die angezeigt werden sollen
    plot_channels = ['F1', 'F2', 'FZ', 'F3', 'F4', 'FY', 'F5', 'FXL', 'F6', 'F7', 'F8', 'NIR', 'VIS']

    # 🔍 CSVs laden und jeweils alle gewünschten Kanäle plotten
    for filepath in file_matches:
        st.markdown(f"### 📄 Datei: `{os.path.basename(filepath)}`")

        try:
            df = pd.read_csv(filepath, sep=";")
            if 'cycle' not in df.columns:
                st.error(f"❌ 'cycle' fehlt in Datei {filepath}")
                continue

            cycle = df["cycle"]
            available = [ch for ch in plot_channels if ch in df.columns]
            if not available:
                st.warning(f"⚠️ Keine gültigen Kanäle in Datei: {filepath}")
                continue

            cols = 2
            rows = math.ceil(len(available) / cols)
            fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 2.5), squeeze=False)

            for idx, ch in enumerate(available):
                r, c = divmod(idx, cols)
                ax = axes[r][c]
                ax.plot(cycle, df[ch], label=ch, color='tab:blue', linewidth=1.5)
                ax.set_title(ch, fontsize=10, fontweight='bold')
                ax.grid(True, linestyle='--', alpha=0.3)
                ax.tick_params(labelsize=7)
                ax.set_xlabel("")
                ax.set_ylabel("")
                for spine in ax.spines.values():
                    spine.set_edgecolor('lightgray')
                    spine.set_linewidth(1)

            for i in range(len(available), rows * cols):
                r, c = divmod(i, cols)
                fig.delaxes(axes[r][c])

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            st.pyplot(fig)

            # 🔁 Kanalvergleichsmenü für diese Datei
            st.markdown("#### ➗ Kanalvergleich")
            col_a, col_b = st.columns(2)
            unique_id = os.path.basename(filepath)  # z. B. Sensor_04_ROX.csv
            ch_a = col_a.selectbox("Zähler (oben)", available, key=f"{unique_id}_a")
            ch_b = col_b.selectbox("Nenner (unten)", available, key=f"{unique_id}_b")

            try:
                result = df[ch_a] / df[ch_b]
                fig2, ax2 = plt.subplots(figsize=(10, 3))
                ax2.plot(cycle, result, color='tab:green')
                ax2.set_title(f"{ch_a} / {ch_b}", fontsize=12, fontweight='bold')
                ax2.grid(True, linestyle='--', alpha=0.4)
                ax2.tick_params(labelsize=8)
                ax2.set_xlabel("")
                ax2.set_ylabel("")
                st.pyplot(fig2)
            except Exception as e:
                st.error(f"❌ Fehler bei Berechnung {ch_a} / {ch_b}: {e}")

        except Exception as e:
            st.error(f"❌ Fehler beim Einlesen von {filepath}: {e}")

    # Aufräumen
    shutil.rmtree(temp_dir)
else:
    st.info("⬆ Bitte lade eine ZIP-Datei mit deiner Datenstruktur hoch.")
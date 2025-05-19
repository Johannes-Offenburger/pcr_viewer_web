import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# 📐 Layout: Seitenbreite nutzen
st.set_page_config(layout="wide")
st.title("🧬 PCR CSV Viewer – Webversion")

# 📂 CSV hochladen
uploaded_file = st.file_uploader("📄 CSV-Datei auswählen", type="csv")

if uploaded_file:
    # CSV einlesen
    try:
        df = pd.read_csv(uploaded_file, sep=';')
    except Exception as e:
        st.error(f"❌ Fehler beim Einlesen: {e}")
        st.stop()

    if 'cycle' not in df.columns:
        st.error("❌ Spalte 'cycle' fehlt in der Datei.")
        st.stop()

    cycle = df['cycle']

    # Nur gewünschte Spalten
    selected_cols = [
        'temp_wellblock', 'temp_heatsink', 'temp_led',
        'F1', 'F2', 'FZ', 'F3', 'F4', 'FY', 'F5', 'FXL',
        'F6', 'F7', 'F8', 'NIR', 'VIS'
    ]
    data_cols = [col for col in selected_cols if col in df.columns]

    st.markdown("### 📊 Einzelkurven")
    cols = 2
    rows = math.ceil(len(data_cols) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 2.5), squeeze=False)
    for idx, col in enumerate(data_cols):
        r, c = divmod(idx, cols)
        ax = axes[r][c]
        ax.plot(cycle, df[col], label=col, color='tab:blue', linewidth=1.5)
        ax.set_title(col, fontsize=10, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.tick_params(labelsize=7)
        ax.set_xlabel("")
        ax.set_ylabel("")
        for spine in ax.spines.values():
            spine.set_edgecolor('lightgray')
            spine.set_linewidth(1)

    for i in range(len(data_cols), rows * cols):
        r, c = divmod(i, cols)
        fig.delaxes(axes[r][c])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    st.pyplot(fig)

    # 🔍 Vergleichsbereich
    st.markdown("---")
    st.markdown("### 🔍 Kanalvergleich (Division A / B)")

    col1, col2 = st.columns(2)
    kanal1 = col1.selectbox("🧮 Zähler (oben)", data_cols, key="k1")
    kanal2 = col2.selectbox("📉 Nenner (unten)", data_cols, key="k2")

    if kanal1 and kanal2:
        try:
            result = df[kanal1] / df[kanal2]
            fig2, ax2 = plt.subplots(figsize=(10, 3))
            ax2.plot(cycle, result, color='tab:green')
            ax2.set_title(f"{kanal1} / {kanal2}", fontsize=12, fontweight='bold')
            ax2.grid(True, linestyle='--', alpha=0.4)
            ax2.tick_params(labelsize=8)
            ax2.set_xlabel("")
            ax2.set_ylabel("")
            st.pyplot(fig2)
        except Exception as e:
            st.error(f"Fehler bei Berechnung: {e}")
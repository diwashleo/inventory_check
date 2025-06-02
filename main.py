import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Storewise Product Checker", layout="centered")
st.title("🛒 Storewise Product Checker App")

# Session state setup
if 'df' not in st.session_state:
    st.session_state.df = None
if 'store' not in st.session_state:
    st.session_state.store = None
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Load Excel file from project directory (only if not already loaded)
excel_file_path = "products.xlsx"  # Change filename if needed

if st.session_state.df is None:
    try:
        df = pd.read_excel(excel_file_path)
        df.columns = ["Store", "Product", "Planned Quantity", "Received Qty", "Product Unit Tags", "Rack Name", "Remark"]
        df["Remark"] = df["Remark"].astype(str).fillna("")
        st.session_state.df = df
    except FileNotFoundError:
        st.error(f"❌ Could not find the file '{excel_file_path}'. Please place it in the project directory.")
        st.stop()

df = st.session_state.df

# Store Selection
if df is not None:
    stores = df["Store"].unique().tolist()
    if st.session_state.store is None:
        st.subheader("Step 1️⃣: Select a Store")
        store_selected = st.selectbox("Choose a store", stores)
        if st.button("Start Checking"):
            st.session_state.store = store_selected
            st.session_state.current_index = 0
            st.rerun()
    else:
        # Filter data by store, keep original index for updating
        store_mask = st.session_state.df["Store"] == st.session_state.store
        store_indices = st.session_state.df[store_mask].index.tolist()
        store_df = st.session_state.df.loc[store_indices].reset_index()  # 'index' column is the original index

        index = st.session_state.current_index

        if index < len(store_df):
            row = store_df.iloc[index]
            st.subheader(f"Step 2️⃣: Checking Products for **{st.session_state.store}**")
            st.write(f"**Product:** {row['Product']}")
            st.write(f"**Planned Qty:** {row['Planned Quantity']}")
            st.write(f"**Received Qty:** {row['Received Qty']}")
            st.write(f"**Rack Name:** {row['Rack Name']}")
            st.write("**Product Unit Tags:**")
            for tag in str(row["Product Unit Tags"]).split(","):
                st.markdown(f"- {tag.strip()}")

            # Remark input
            with st.expander("📝 Add Remark"):
                original_index = row["index"]  # This is the index in st.session_state.df
                existing_remark = st.session_state.df.at[original_index, "Remark"]
                remark_key = f"remark_{index}"
                remark_text = st.text_area("Enter your remark here (if any)", value=existing_remark, key=remark_key)

            col1, col2 = st.columns(2)
            if col1.button("✅ Mark as Correct & Next", key=f"correct_next_{index}"):
                st.session_state.df.at[original_index, "Remark"] = remark_text
                st.session_state.current_index += 1
                st.rerun()

            if col2.button("📝 Save Remark & Next", key=f"save_next_{index}"):
                st.session_state.df.at[original_index, "Remark"] = remark_text
                st.session_state.current_index += 1
                st.rerun()

            st.markdown(f"---\n**{index + 1} of {len(store_df)} products checked**")
        else:
            st.success(f"✅ All products checked for **{st.session_state.store}**!")

            if st.button("🔙 Go Back to Store Selection"):
                st.session_state.store = None
                st.session_state.current_index = 0
                st.rerun()

    # Final download
    st.markdown("---")
    st.subheader("📥 Download Final Checked File")
    output = BytesIO()
    st.session_state.df.to_excel(output, index=False)
    output.seek(0)
    st.download_button("Download Excel", output, file_name="checked_products.xlsx")

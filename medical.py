import pandas as pd
import streamlit as st
import plotly.express as px

def main():
    st.set_page_config(page_title="Medical Insurance Analytics", layout="wide")
    st.title("Medical Life Assurance Dashboard")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    option = st.sidebar.selectbox(
        "Select Analysis",
        ("Load Data", "Staff vs Dependents", "Age Distribution", "Family Analysis", "Gender Distribution")
    )

    # Predefined file path
    file_path = "data/BANK OF KIGALI UPDATED MEMBERSHIP LIST.xlsx"

    # Load data when app starts
    try:
        # Define the column names explicitly
        column_names = [
            'Member Number', 'Surname', 'Other Name(s)', 'CAT',
            'P/Cont', 'Birth Date', 'Sex', 'Entry Date', 'Status'
        ]

        # Read the file
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path, names=column_names, skiprows=1)
        elif file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path, names=column_names, skiprows=1)

        # Process dates
        data['Birth Date'] = pd.to_datetime(data['Birth Date'], format='%d-%b-%Y', errors='coerce', dayfirst=True)
        data['Entry Date'] = pd.to_datetime(data['Entry Date'], errors='coerce', dayfirst=True)

        # Calculate age
        data["Age"] = (pd.Timestamp.now() - data['Birth Date']).dt.days // 365

        # Classify staff and dependents
        data["Type"] = data["P/Cont"].fillna("").apply(lambda x: "Staff" if x == "Y" else "Dependent")

        # Classify relationships
        data["Relationship"] = data.apply(lambda row: 
            "Staff" if row["P/Cont"] == "Y" else 
            "Spouse" if row["Sex"] in ["F", "M"] and row["Age"] >= 18 else 
            "Child", axis=1)

        # Save data to session state
        st.session_state['data'] = data

    except Exception as e:
        st.error(f"Error loading the data: {str(e)}")
        return

    # Perform analysis based on user selection
    if option == "Load Data":
        st.header("Staff and Dependents Data")
        st.dataframe(st.session_state['data'])

    elif option == "Staff vs Dependents":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return

        data = st.session_state['data']
        st.header("Staff vs Dependents Analysis")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(data, names="Type", title="Distribution of Staff vs Dependents")
            st.plotly_chart(fig)

        with col2:
            rel_breakdown = data["Relationship"].value_counts()
            fig = px.bar(rel_breakdown, title="Relationship Distribution")
            st.plotly_chart(fig)

        st.subheader("Summary Statistics")
        stats = pd.DataFrame({
            "Category": ["Total Staff", "Total Dependents", "Average Dependents per Staff"],
            "Value": [
                len(data[data["Type"] == "Staff"]),
                len(data[data["Type"] == "Dependent"]),
                round(len(data[data["Type"] == "Dependent"]) / len(data[data["Type"] == "Staff"]), 2)
            ]
        })
        st.table(stats)

    elif option == "Age Distribution":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return

        data = st.session_state['data']
        st.header("Age Distribution of Staff and Dependents")

        fig = px.box(data, x="Type", y="Age", points="all", title="Age Distribution by Type")
        st.plotly_chart(fig)

    elif option == "Family Analysis":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return

        data = st.session_state['data']
        st.header("Family Analysis")

        family_breakdown = data["Relationship"].value_counts()
        fig = px.bar(family_breakdown, title="Family Relationship Breakdown")
        st.plotly_chart(fig)

        family_stats = pd.DataFrame({
            "Category": ["Total Families", "Average Number of Dependents per Family"],
            "Value": [
                len(data[data["Relationship"] != "Staff"]),
                round(len(data[data["Relationship"] != "Staff"]) / len(data[data["Relationship"] == "Staff"]), 2)
            ]
        })
        st.table(family_stats)

    elif option == "Gender Distribution":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return

        data = st.session_state['data']
        st.header("Gender Distribution")

        gender_distribution = data['Sex'].value_counts()
        fig = px.bar(gender_distribution, title="Gender Distribution", labels={"index": "Gender", "value": "Count"})
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()

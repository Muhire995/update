import pandas as pd
import streamlit as st
import datetime as dt
import plotly.express as px
import io

def main():
    st.set_page_config(page_title="Medical Insurance Analytics", layout="wide")
    st.title("Medical Life Assurance Dashboard")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    option = st.sidebar.selectbox(
        "Select Analysis",
        ("Upload Data", "Staff vs Dependents", "Age Distribution", "Family Analysis", "Gender Distribution")
    )

    # File Upload and Data Handling
    if option == "Upload Data":
        st.header("Upload Staff and Dependents Data")
        uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])
        
        if uploaded_file:
            try:
                # Define the column names explicitly
                column_names = [
                    'Member Number', 'Surname', 'Other Name(s)', 'CAT', 
                    'P/Cont', 'Birth Date', 'Sex', 'Entry Date', 'Status'
                ]
                
                # Read the file with explicit column names
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file, names=column_names, skiprows=1)
                elif uploaded_file.name.endswith('.xlsx'):
                    data = pd.read_excel(uploaded_file, names=column_names, skiprows=1)
                
                # Display raw data before processing
                st.subheader("Raw Data")
                st.dataframe(data.head())
                
                # Process dates
                st.info("Processing dates...")

                # Convert dates with error handling and coercion
                try:
                    # Attempt to parse dates with the dayfirst flag and error handling
                    data['Birth Date'] = pd.to_datetime(data['Birth Date'], format='%d-%b-%Y', errors='coerce', dayfirst=True)
                    data['Entry Date'] = pd.to_datetime(data['Entry Date'], errors='coerce', dayfirst=True)

                    # Check for any NaT values and provide feedback to the user
                    if data['Birth Date'].isnull().any():
                        st.warning("Some birth dates could not be parsed correctly. Check the 'Birth Date' column for invalid entries.")
                    
                    if data['Entry Date'].isnull().any():
                        st.warning("Some entry dates could not be parsed correctly. Check the 'Entry Date' column for invalid entries.")

                    # Calculate age (assuming the birth date is now properly parsed)
                    data["Age"] = (pd.Timestamp.now() - data['Birth Date']).dt.days // 365

                    # Handle staff/dependent classification
                    data["Type"] = data["P/Cont"].fillna("").apply(lambda x: "Staff" if x == "Y" else "Dependent")

                    # Add relationship classification
                    data["Relationship"] = data.apply(lambda row: 
                        "Staff" if row["P/Cont"] == "Y" else 
                        "Spouse" if row["Sex"] in ["F", "M"] and row["Age"] >= 18 else 
                        "Child", axis=1)

                    # Display processed data
                    st.header("Processed Staff and Dependents Data")
                    st.dataframe(data)

                    # Save data to session state
                    st.session_state['data'] = data

                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
                    st.write("Data sample for debugging:")
                    st.write(data.head())
                    return

            except Exception as e:
                st.error(f"An error occurred while reading the file: {str(e)}")
                st.error("Please check your file format and try again.")
                return

    elif option == "Staff vs Dependents":
        if 'data' not in st.session_state:
            st.error("Please upload data first.")
            return

        data = st.session_state['data']
        st.header("Staff vs Dependents Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart using plotly
            fig = px.pie(data, names="Type", title="Distribution of Staff vs Dependents")
            st.plotly_chart(fig)

        with col2:
            # Relationship breakdown
            rel_breakdown = data["Relationship"].value_counts()
            fig = px.bar(rel_breakdown, title="Relationship Distribution")
            st.plotly_chart(fig)

        # Detailed statistics
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
            st.error("Please upload data first.")
            return
        
        data = st.session_state['data']
        st.header("Age Distribution of Staff and Dependents")

        fig = px.box(data, x="Type", y="Age", points="all", title="Age Distribution by Type")
        st.plotly_chart(fig)

    elif option == "Family Analysis":
        if 'data' not in st.session_state:
            st.error("Please upload data first.")
            return
        
        data = st.session_state['data']
        st.header("Family Analysis")

        # Relationship breakdown
        family_breakdown = data["Relationship"].value_counts()
        fig = px.bar(family_breakdown, title="Family Relationship Breakdown")
        st.plotly_chart(fig)

        # Show statistics about families (average number of dependents per staff)
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
            st.error("Please upload data first.")
            return
        
        data = st.session_state['data']
        st.header("Gender Distribution")

        gender_distribution = data['Sex'].value_counts()
        fig = px.bar(gender_distribution, title="Gender Distribution", labels={"Sex": "Gender"})
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()

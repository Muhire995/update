import pandas as pd
import streamlit as st
import plotly.express as px

def main():
    st.set_page_config(page_title="Medical Insurance Analytics", layout="wide")
    st.title("Medical Scheme Analysis")

    # Sidebar navigation
    st.sidebar.title("All Analysis")
    option = st.sidebar.selectbox(
        "Select Analysis",
        ("Dashboard Overview", "Load Data", "Staff vs Dependents", "Age Distribution", 
         "Family Analysis", "Gender Distribution", "Leavers Analysis", 
         "Current Members Category Analysis", "Leavers Category Analysis")
    )

    # Predefined file paths
    data_file_path = "data/Full List.xlsx"
    leavers_file_path = "data/Leavers.xlsx"

    # Load Full List data when app starts
    try:
        column_names = [
            'Member Number', 'Surname', 'Other Name(s)', 'Relationship', 'CAT',
            'P/Cont', 'Birth Date', 'Sex', 'Entry Date', 'Family Al Size', 'Status'
        ]

        # Read the main data file
        if data_file_path.endswith('.csv'):
            data = pd.read_csv(data_file_path, names=column_names, skiprows=1)
        elif data_file_path.endswith('.xlsx'):
            data = pd.read_excel(data_file_path, names=column_names, skiprows=1)

        # Process dates
        data['Birth Date'] = pd.to_datetime(data['Birth Date'], format='%d-%b-%Y', errors='coerce', dayfirst=True)
        data['Entry Date'] = pd.to_datetime(data['Entry Date'], errors='coerce', dayfirst=True)

        # Calculate age
        data["Age"] = (pd.Timestamp.now() - data['Birth Date']).dt.days // 365

        # Classify staff and dependents based on the P/Cont column
        data["Relationship"] = data["P/Cont"].apply(lambda x: "Member" if x == "Y" else "Dependent")

        # Save data to session state
        st.session_state['data'] = data

    except Exception as e:
        st.error(f"Error loading the main data: {str(e)}")
        return

    # Dashboard Overview
    if option == "Dashboard Overview":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return

        data = st.session_state['data']

        # Key Metrics
        total_members = len(data[data["Relationship"] == "Member"])
        total_dependents = len(data[data["Relationship"] == "Dependent"])
        total_staff = total_members
        avg_age_staff = round(data[data["Relationship"] == "Member"]["Age"].mean(), 2)
        avg_age_dependents = round(data[data["Relationship"] == "Dependent"]["Age"].mean(), 2)
        gender_distribution = data["Sex"].value_counts()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Staff", total_staff)
        with col2:
            st.metric("Total Dependents", total_dependents)
        with col3:
            st.metric("Average Age (Staff)", avg_age_staff)
        with col4:
            st.metric("Average Age (Dependents)", avg_age_dependents)

        # Gender Distribution Chart
        st.subheader("Gender Distribution")
        fig = px.pie(names=gender_distribution.index, values=gender_distribution.values, title="Gender Breakdown")
        st.plotly_chart(fig, use_container_width=True)

        # Display dependents who are between 21 and 26 years old
        st.subheader("Dependents Between 21 and 26 Years Old")
        dependents_between_21_and_26 = data[(data["Relationship"] == "Dependent") & (data["Age"] >= 21) & (data["Age"] <= 26)]

        if not dependents_between_21_and_26.empty:
            st.dataframe(dependents_between_21_and_26[['Member Number', 'Surname', 'Other Name(s)', 'Age']])
        else:
            st.write("No dependents found who are between 21 and 26 years old.")

    # Load Data option
    elif option == "Load Data":
        st.header("Staff and Dependents Data")
        st.dataframe(st.session_state['data'])

    # Staff vs Dependents option
    elif option == "Staff vs Dependents":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return
        data = st.session_state['data']
        st.header("Staff vs Dependents Analysis")
        staff_count = len(data[data["Relationship"] == "Member"])
        dependent_count = len(data[data["Relationship"] == "Dependent"])
        average_dependents_per_staff = round(dependent_count / staff_count, 2) if staff_count > 0 else 0
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(data, names="Relationship", title="Distribution of Staff vs Dependents")
            st.plotly_chart(fig)
        with col2:
            rel_breakdown = data["Relationship"].value_counts()
            fig = px.bar(rel_breakdown, title="Relationship Distribution")
            st.plotly_chart(fig)
        st.subheader("Summary Statistics")
        stats = pd.DataFrame({
            "Category": ["Total Staff", "Total Dependents", "Average Dependents per Staff"],
            "Value": [staff_count, dependent_count, average_dependents_per_staff]
        })
        st.table(stats)

    # Age Distribution option
    elif option == "Age Distribution":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return
        data = st.session_state['data']
        st.header("Age Distribution of Staff and Dependents")
        fig = px.box(data, x="Relationship", y="Age", points="all", title="Age Distribution by Type")
        st.plotly_chart(fig)

    # Family Analysis option
    elif option == "Family Analysis":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return
        data = st.session_state['data']
        st.header("Family Analysis")
        family_breakdown = data["Relationship"].value_counts()
        fig = px.bar(family_breakdown, title="Family Relationship Breakdown")
        st.plotly_chart(fig)
        total_families = len(data[data["Relationship"] == "Dependent"])
        average_dependents_per_family = round(total_families / len(data[data["Relationship"] == "Member"]), 2) if len(data[data["Relationship"] == "Member"]) > 0 else 0
        family_stats = pd.DataFrame({
            "Category": ["Total Families", "Average Number of Dependents per Family"],
            "Value": [total_families, average_dependents_per_family]
        })
        st.table(family_stats)

    # Gender Distribution option
    elif option == "Gender Distribution":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return
        data = st.session_state['data']
        st.header("Gender Distribution")
        gender_by_relationship = data.groupby(["Relationship", "Sex"]).size().reset_index(name="Count")
        fig = px.bar(
            gender_by_relationship,
            x="Sex",
            y="Count",
            color="Relationship",
            barmode="group",
            title="Gender Distribution by Relationship Type",
            labels={"Sex": "Gender", "Count": "Number of Individuals"}
        )
        st.plotly_chart(fig)
        st.subheader("Gender Breakdown Table")
        st.dataframe(gender_by_relationship)

    # Current Members Category Analysis option
    elif option == "Current Members Category Analysis":
        if 'data' not in st.session_state:
            st.error("Data not loaded.")
            return
            
        data = st.session_state['data']
        st.header("Category Analysis - Current Members")
        
        # Clean and standardize the CAT column
        data['CAT'] = data['CAT'].fillna('Not Specified')
        
        # Category Distribution
        st.subheader("Category Distribution")
        cat_distribution = data['CAT'].value_counts()
        fig = px.pie(
            values=cat_distribution.values,
            names=cat_distribution.index,
            title="Distribution of Categories"
        )
        st.plotly_chart(fig)
        
        # Category by Relationship
        st.subheader("Category Distribution by Relationship")
        cat_by_relationship = pd.crosstab(data['CAT'], data['Relationship'])
        fig = px.bar(
            cat_by_relationship,
            barmode='group',
            title="Category Distribution by Relationship Type"
        )
        st.plotly_chart(fig)
        
        # Average Age by Category
        st.subheader("Average Age by Category")
        avg_age_by_cat = data.groupby('CAT')['Age'].mean().round(2)
        fig = px.bar(
            avg_age_by_cat,
            title="Average Age by Category"
        )
        st.plotly_chart(fig)
        
        # Detailed Statistics
        #st.subheader("Category Statistics")
        #cat_stats = pd.DataFrame({
            #'Total Count': data['CAT'].value_counts(),
            #'Average Age': data.groupby('CAT')['Age'].mean().round(2),
            #'Members': data[data['Relationship'] == 'Member'].groupby('CAT').size(),
            #'Dependents': data[data['Relationship'] == 'Dependent'].groupby('CAT').size()
        #}).fillna(0)
        #st.dataframe(cat_stats)

    # Leavers Analysis option
    elif option == "Leavers Analysis":
        st.header("Leavers Analysis")
        try:
            leaver_columns = ['NAMES', 'DATE OF BIRTH', 'SEX', 'RELATIONSHIP', 'CAT']
            leavers_data = pd.read_excel(leavers_file_path, names=leaver_columns, skiprows=1)
            leavers_data['DATE OF BIRTH'] = pd.to_datetime(leavers_data['DATE OF BIRTH'], format='%d-%b-%Y', errors='coerce', dayfirst=True)
            leavers_data["Age"] = (pd.Timestamp.now() - leavers_data['DATE OF BIRTH']).dt.days // 365

            # Clean the 'SEX' column
            leavers_data = leavers_data.dropna(subset=['SEX'])
            leavers_data['SEX'] = leavers_data['SEX'].str.strip().str.upper()

            # Filter to show only "Staff" and "Dependents" for Relationship
            leavers_data_filtered = leavers_data[leavers_data['RELATIONSHIP'].isin(['EMPLOYEE', 'DEPENDENT'])]

            st.subheader("Leavers Data")
            st.dataframe(leavers_data_filtered)

            st.subheader("Relationship Breakdown")
            rel_breakdown = leavers_data_filtered['RELATIONSHIP'].value_counts()
            fig = px.bar(rel_breakdown, title="Relationship Breakdown (Leavers)", labels={"index": "Relationship", "value": "Count"})
            st.plotly_chart(fig)

            st.subheader("Gender Distribution")
            gender_breakdown = leavers_data_filtered['SEX'].value_counts()
            fig = px.pie(names=gender_breakdown.index, values=gender_breakdown.values, title="Gender Distribution (Leavers)")
            st.plotly_chart(fig)

            st.subheader("Summary Statistics")
            total_leavers = len(leavers_data_filtered)
            total_employees = len(leavers_data_filtered[leavers_data_filtered["RELATIONSHIP"] == "EMPLOYEE"])
            total_dependents = len(leavers_data_filtered[leavers_data_filtered["RELATIONSHIP"] == "DEPENDENT"])
            avg_age_leavers = leavers_data_filtered["Age"].mean()

            summary_stats = pd.DataFrame({
                "Category": ["Total Leavers", "Total Employees", "Total Dependents", "Average Age of Leavers"],
                "Value": [total_leavers, total_employees, total_dependents, round(avg_age_leavers, 2)]
            })
            st.table(summary_stats)

        except Exception as e:
            st.error(f"Error loading or processing leavers data: {str(e)}")

    # Leavers Category Analysis option
    elif option == "Leavers Category Analysis":
        st.header("Category Analysis - Leavers")
        try:
            leaver_columns = ['NAMES', 'DATE OF BIRTH', 'SEX', 'RELATIONSHIP', 'CAT']
            leavers_data = pd.read_excel(leavers_file_path, names=leaver_columns, skiprows=1)
            leavers_data['DATE OF BIRTH'] = pd.to_datetime(leavers_data['DATE OF BIRTH'], format='%d-%b-%Y', errors='coerce', dayfirst=True)
            leavers_data["Age"] = (pd.Timestamp.now() - leavers_data['DATE OF BIRTH']).dt.days // 365
            
            # Clean and standardize the CAT column
            leavers_data['CAT'] = leavers_data['CAT'].fillna('Not Specified')
            
            # Category Distribution for Leavers
            st.subheader("Category Distribution - Leavers")
            leavers_cat_distribution = leavers_data['CAT'].value_counts()
            fig = px.pie(
                values=leavers_cat_distribution.values,
                names=leavers_cat_distribution.index,
                title="Distribution of Categories among Leavers"
            )
            st.plotly_chart(fig)
            
            # Category by Relationship for Leavers
            st.subheader("Category Distribution by Relationship - Leavers")
            leavers_cat_by_relationship = pd.crosstab(leavers_data['CAT'], leavers_data['RELATIONSHIP'])
            fig = px.bar(
                leavers_cat_by_relationship,
                barmode='group',
                title="Category Distribution by Relationship Type - Leavers"
            )
            st.plotly_chart(fig)
            
            # Average Age by Category for Leavers
            st.subheader("Average Age by Category - Leavers")
            leavers_avg_age_by_cat = leavers_data.groupby('CAT')['Age'].mean().round(2)
            fig = px.bar(
                leavers_avg_age_by_cat,
                title="Average Age by Category - Leavers"
            )
            st.plotly_chart(fig)
            
            # Detailed Statistics for Leavers
            st.subheader("Category Statistics - Leavers")
            leavers_cat_stats = pd.DataFrame({
                'Total Count': leavers_data['CAT'].value_counts(),
                'Average Age': leavers_data.groupby('CAT')['Age'].mean().round(2),
                'Employees': leavers_data[leavers_data['RELATIONSHIP'] == 'EMPLOYEE'].groupby('CAT').size(),
                'Dependents': leavers_data[leavers_data['RELATIONSHIP'] == 'DEPENDENT'].groupby('CAT').size()
            }).fillna(0)
            st.dataframe(leavers_cat_stats)

        except Exception as e:
            st.error(f"Error loading or processing leavers category data: {str(e)}")

if __name__ == "__main__":
    main()

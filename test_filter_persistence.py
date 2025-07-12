#!/usr/bin/env python3
"""
Test script to verify filter persistence in the dashboard
"""

import streamlit as st
import pandas as pd

def test_filter_persistence():
    """Test that filters persist across page refreshes"""
    
    # Initialize session state
    if 'show_mismatches_only' not in st.session_state:
        st.session_state.show_mismatches_only = False
    if 'selected_product_type' not in st.session_state:
        st.session_state.selected_product_type = "All"
    if 'selected_diagnosis' not in st.session_state:
        st.session_state.selected_diagnosis = "All"
    
    st.title("Filter Persistence Test")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'TradeID': ['T001', 'T002', 'T003', 'T004', 'T005'],
        'ProductType': ['Swap', 'Option', 'Swap', 'Option', 'Swap'],
        'Diagnosis': ['Pricing_Error', 'Model_Change', 'Data_Issue', 'Pricing_Error', 'Model_Change'],
        'Any_Mismatch': [True, False, True, True, False],
        'PV_old': [1000, 2000, 3000, 4000, 5000],
        'PV_new': [1100, 2000, 3200, 4100, 5000],
        'Delta_old': [0.5, 0.3, 0.7, 0.2, 0.8],
        'Delta_new': [0.52, 0.3, 0.75, 0.22, 0.8]
    })
    
    st.write("### Sample Data")
    st.dataframe(sample_data)
    
    # Filter controls
    st.write("### Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_mismatches_only = st.checkbox(
            "Show mismatches only",
            value=st.session_state.show_mismatches_only,
            key="test_mismatches_filter"
        )
        st.session_state.show_mismatches_only = show_mismatches_only
    
    with col2:
        product_types = ["All"] + list(sample_data['ProductType'].unique())
        selected_product_type = st.selectbox(
            "Filter by Product Type",
            options=product_types,
            index=product_types.index(st.session_state.selected_product_type) if st.session_state.selected_product_type in product_types else 0,
            key="test_product_type_filter"
        )
        st.session_state.selected_product_type = selected_product_type
    
    with col3:
        diagnoses = ["All"] + list(sample_data['Diagnosis'].unique())
        selected_diagnosis = st.selectbox(
            "Filter by Diagnosis",
            options=diagnoses,
            index=diagnoses.index(st.session_state.selected_diagnosis) if st.session_state.selected_diagnosis in diagnoses else 0,
            key="test_diagnosis_filter"
        )
        st.session_state.selected_diagnosis = selected_diagnosis
    
    # Apply filters
    filtered_data = sample_data.copy()
    if show_mismatches_only:
        filtered_data = filtered_data[filtered_data['Any_Mismatch']]
    if selected_product_type != "All":
        filtered_data = filtered_data[filtered_data['ProductType'] == selected_product_type]
    if selected_diagnosis != "All":
        filtered_data = filtered_data[filtered_data['Diagnosis'] == selected_diagnosis]
    
    # Display results
    st.write("### Filtered Results")
    if show_mismatches_only or selected_product_type != "All" or selected_diagnosis != "All":
        st.info(f"📊 Showing {len(filtered_data)} of {len(sample_data)} trades")
        
        if st.button("🔄 Reset Filters"):
            st.session_state.show_mismatches_only = False
            st.session_state.selected_product_type = "All"
            st.session_state.selected_diagnosis = "All"
            st.rerun()
    
    st.dataframe(filtered_data)
    
    # Display current filter state
    st.write("### Current Filter State")
    st.write(f"Show mismatches only: {st.session_state.show_mismatches_only}")
    st.write(f"Selected product type: {st.session_state.selected_product_type}")
    st.write(f"Selected diagnosis: {st.session_state.selected_diagnosis}")

if __name__ == "__main__":
    test_filter_persistence() 
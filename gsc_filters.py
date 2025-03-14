import streamlit as st

def create_dimension_filter(dimension, operator, expression):
    """
    Create a dimension filter for Google Search Console API
    
    Parameters:
    - dimension: The dimension to filter ('country', 'device', 'page', 'query', 'searchAppearance')
    - operator: The operator ('equals', 'contains', 'notEquals', 'notContains', 'includingRegex', 'excludingRegex')
    - expression: The expression to match
    
    Returns:
    - A dimension filter dict
    """
    return {
        'dimension': dimension,
        'operator': operator,
        'expression': expression
    }

def create_filter_group(filters, group_type='and'):
    """
    Create a filter group for Google Search Console API
    
    Parameters:
    - filters: List of dimension filters
    - group_type: Type of grouping ('and' or 'or')
    
    Returns:
    - A filter group dict
    """
    return {
        'filters': filters,
        'groupType': group_type
    }

def add_filter_ui():
    """
    UI components for adding dimension filters
    
    Returns:
    - A list of dimension filter groups or None if no filters set
    """
    with st.expander("Add Filters"):
        add_filter = st.checkbox("Enable filtering")
        
        if not add_filter:
            return None
            
        filter_groups = []
        
        # UI for creating filters
        dimensions = ['country', 'device', 'page', 'query', 'searchAppearance']
        operators = ['equals', 'contains', 'notEquals', 'notContains', 'includingRegex', 'excludingRegex']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dimension = st.selectbox("Dimension", dimensions)
        
        with col2:
            operator = st.selectbox("Operator", operators)
        
        with col3:
            expression = st.text_input("Expression")
            
        group_type = st.radio("Filter Group Type", ['and', 'or'], horizontal=True)
            
        if st.button("Add Filter") and expression:
            # Create a filter
            filter_obj = create_dimension_filter(dimension, operator, expression)
            
            # Create a filter group
            filter_group = create_filter_group([filter_obj], group_type)
            
            # Add to session state if not exists
            if 'filter_groups' not in st.session_state:
                st.session_state.filter_groups = []
                
            st.session_state.filter_groups.append(filter_group)
            st.success(f"Filter added: {dimension} {operator} '{expression}'")
        
        # Show existing filters
        if 'filter_groups' in st.session_state and st.session_state.filter_groups:
            st.subheader("Applied Filters")
            
            for i, group in enumerate(st.session_state.filter_groups):
                for j, filter_obj in enumerate(group['filters']):
                    st.write(f"{i+1}.{j+1} {filter_obj['dimension']} {filter_obj['operator']} '{filter_obj['expression']}'")
                    
            if st.button("Clear All Filters"):
                st.session_state.filter_groups = []
                st.success("All filters cleared")
                
            filter_groups = st.session_state.filter_groups
        
        return filter_groups if filter_groups else None

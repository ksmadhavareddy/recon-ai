# 🤖 AI Reconciliation Dashboard

A modern, interactive web dashboard for the AI-powered reconciliation system built with Streamlit.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Dashboard
```bash
# Option 1: Using the launcher script
python run_dashboard.py

# Option 2: Direct streamlit command
streamlit run app.py
```

### 3. Open Browser
The dashboard will automatically open at: http://localhost:8501

## 📊 Dashboard Features

### 🎯 Core Functionality
- **File Upload**: Drag-and-drop interface for data files
- **Real-time Processing**: Live reconciliation analysis
- **Interactive Visualizations**: Charts and graphs with Plotly
- **Configurable Settings**: Adjustable tolerance thresholds
- **Export Capabilities**: Download results as Excel files

### 📈 Visualization Components
- **Mismatch Distribution**: Bar charts showing PV/Delta mismatches
- **Diagnosis Comparison**: Pie charts comparing rule-based vs ML diagnoses
- **Scatter Plots**: PV vs Delta changes with color coding
- **Trend Analysis**: Time series visualization of changes
- **Statistical Summary**: Descriptive statistics tables

### 🔍 Analysis Features
- **Filtering**: Filter results by product type, mismatch status
- **Comparison Tables**: Side-by-side rule-based vs ML diagnosis
- **Metrics Dashboard**: Key performance indicators
- **Detailed Results**: Comprehensive data tables

## 📁 Data Requirements

### Required Files
Upload these files through the dashboard interface:

1. **old_pricing.xlsx**
   - Columns: `TradeID`, `PV_old`, `Delta_old`

2. **new_pricing.xlsx**
   - Columns: `TradeID`, `PV_new`, `Delta_new`

3. **trade_metadata.xlsx**
   - Columns: `TradeID`, `ProductType`, `FundingCurve`, `CSA_Type`, `ModelVersion`

4. **funding_model_reference.xlsx**
   - Columns: `TradeID`, additional funding-related fields

### Sample Data Format
```
TradeID  PV_old   Delta_old
T001     104500   0.42
T002     -98000   -0.98
T003     50500    0.00
```

## 🎛️ Configuration Options

### Tolerance Settings
- **PV Tolerance**: Threshold for PV mismatch detection (100-10,000)
- **Delta Tolerance**: Threshold for Delta mismatch detection (0.01-0.50)

### Display Options
- **Show Mismatches Only**: Filter to display only flagged trades
- **Product Type Filter**: Filter by specific product types
- **Export Format**: Choose Excel or chart export

## 📊 Dashboard Sections

### 1. 📈 Overview Tab
- **Mismatch Distribution Chart**: Visual breakdown of mismatch types
- **Diagnosis Distribution**: Comparison of rule-based vs ML diagnoses
- **Key Metrics**: Total trades, mismatch counts, percentages

### 2. 🔍 Analysis Tab
- **PV vs Delta Scatter Plot**: Interactive scatter plot with hover details
- **Trend Chart**: Line chart showing changes over trade index
- **Statistical Summary**: Descriptive statistics table

### 3. 📋 Details Tab
- **Filtered Results**: Comprehensive data table with filtering options
- **Search and Sort**: Interactive table with search functionality
- **Export Options**: Download filtered results

### 4. 📊 Comparison Tab
- **Agreement Analysis**: Rule-based vs ML diagnosis comparison
- **Disagreement Details**: Trades where diagnoses differ
- **Accuracy Metrics**: Agreement rate and statistics

### 5. 💾 Export Tab
- **Excel Download**: Download complete results as Excel file
- **Chart Export**: Export visualizations as images (coming soon)
- **Summary Statistics**: Key metrics and performance indicators

## 🎨 User Interface

### Design Features
- **Responsive Layout**: Works on desktop and mobile devices
- **Modern Styling**: Clean, professional appearance
- **Intuitive Navigation**: Easy-to-use tabbed interface
- **Real-time Updates**: Live progress indicators and status messages

### Interactive Elements
- **File Upload**: Drag-and-drop file upload interface
- **Sliders**: Interactive tolerance configuration
- **Charts**: Zoom, pan, and hover interactions
- **Tables**: Sortable and filterable data tables

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Visualizations**: Plotly interactive charts
- **Data Processing**: Pandas for data manipulation
- **ML Integration**: Seamless integration with existing ML pipeline

### Performance
- **Real-time Processing**: Immediate analysis results
- **Memory Efficient**: Optimized for large datasets
- **Responsive UI**: Fast loading and smooth interactions

## 🛠️ Troubleshooting

### Common Issues

#### Dashboard Won't Start
```bash
# Check if streamlit is installed
pip install streamlit

# Check if all dependencies are installed
pip install -r requirements.txt

# Try running directly
streamlit run app.py
```

#### File Upload Issues
- Ensure files are in Excel (.xlsx) format
- Check that all required columns are present
- Verify file names match expected format

#### Processing Errors
- Check file format and column names
- Ensure all required files are uploaded
- Verify data types (numeric for PV/Delta values)

### Error Messages
- **"Missing required files"**: Upload all 4 required files
- **"Processing error"**: Check file format and data quality
- **"No data returned"**: Verify file contents and column names

## 🚀 Advanced Usage

### Custom Configuration
```python
# Modify app.py for custom settings
st.sidebar.slider(
    "Custom Tolerance",
    min_value=0,
    max_value=10000,
    value=1000
)
```

### Adding New Visualizations
```python
# Add new chart functions
def create_custom_chart(df):
    # Your custom visualization code
    return fig

# Add to dashboard
st.plotly_chart(create_custom_chart(df))
```

### Integration with External Systems
```python
# Add database connection
import sqlite3
conn = sqlite3.connect('reconciliation.db')

# Add API endpoints
import requests
response = requests.post('http://api.example.com/reconcile', json=data)
```

## 📈 Performance Optimization

### Large Datasets
- **Chunked Processing**: Process data in smaller chunks
- **Caching**: Cache results for repeated analysis
- **Lazy Loading**: Load visualizations on demand

### Memory Management
- **Garbage Collection**: Clean up temporary files
- **Streaming**: Process data streams for real-time analysis
- **Compression**: Compress large datasets

## 🔮 Future Enhancements

### Planned Features
- **Real-time Data Feeds**: Live data integration
- **Advanced Filtering**: Multi-criteria filtering
- **Custom Dashboards**: User-defined dashboard layouts
- **Export Formats**: PDF reports and chart images
- **User Authentication**: Multi-user support
- **API Integration**: REST API endpoints

### Technical Improvements
- **WebSocket Support**: Real-time updates
- **Caching Layer**: Redis integration for performance
- **Database Backend**: Persistent storage
- **Cloud Deployment**: AWS/Azure integration

## 📞 Support

### Getting Help
1. **Check Documentation**: Review this README and main documentation
2. **Test with Sample Data**: Use provided sample files
3. **Check Logs**: Review console output for error messages
4. **Community Support**: Join discussions and share experiences

### Reporting Issues
When reporting issues, include:
- **Error Message**: Complete error text
- **File Format**: Sample of problematic data
- **System Info**: Python version, OS, package versions
- **Steps to Reproduce**: Detailed reproduction steps

---

**🎉 Happy Reconciling!**

The AI Reconciliation Dashboard provides a powerful, user-friendly interface for your reconciliation analysis. Enjoy exploring your data with interactive visualizations and real-time processing! 
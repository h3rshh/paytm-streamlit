# 🎛️ Streamlit Size Control Guide

## Where to Change Image Sizes in app.py:

### 1. Upload Section Size
```python
col_upload, col_settings = st.columns([2, 1])  # 🎛️ CHANGE HERE
```
- `[2, 1]` = Upload area 2x bigger than settings
- `[3, 1]` = Upload area 3x bigger 
- `[1, 1]` = Equal sizes

### 2. Image Comparison Size (Main Images)
```python
img_col1, img_col2 = st.columns([1, 1])  # 🖼️ CHANGE HERE
```
- `[1, 1]` = Equal size images (current)
- `[2, 1]` = Left image 2x bigger than right
- `[1, 2]` = Right image 2x bigger than left
- `[3, 2]` = Left image 1.5x bigger than right

### 3. Metrics Row Size
```python
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)  # 📊 CHANGE HERE
```
- `4` = 4 equal columns
- `[2, 1, 1, 1]` = First metric 2x bigger
- `[1, 1, 2, 1]` = Third metric 2x bigger

### 4. Details Section Size
```python
detail_col1, detail_col2 = st.columns([1, 1])  # 📋 CHANGE HERE
```
- `[1, 1]` = Equal size (current)
- `[2, 1]` = Details 2x bigger than charts
- `[1, 2]` = Charts 2x bigger than details

## Quick Size Examples:

### Make Images Bigger:
```python
img_col1, img_col2 = st.columns([2, 1])  # Left image bigger
img_col1, img_col2 = st.columns([1, 2])  # Right image bigger
```

### Make Upload Area Smaller:
```python
col_upload, col_settings = st.columns([1, 1])  # Equal sizes
```

### Make Charts Bigger:
```python
detail_col1, detail_col2 = st.columns([1, 2])  # Charts bigger
```

## Current Settings:
- Upload: `[2, 1]` (Upload 2x bigger)
- Images: `[1, 1]` (Equal size)
- Metrics: `4` (4 equal columns)  
- Details: `[1, 1]` (Equal size)
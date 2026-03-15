# Enhanced Image Tab Layout
# Copy this content to replace the image tab section in app.py

    # Tab 2: Image Detection
    with tab2:
        st.header("Image Logo Detection")
        
        # Upload and settings section
        st.subheader("📤 Upload & Configure")
        col_upload, col_settings = st.columns([2, 1])
        
        with col_upload:
            uploaded_image = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg'],
                help="Upload an image to detect Paytm logos"
            )
        
        with col_settings:
            confidence = st.slider(
                "Confidence Threshold",
                min_value=0.05,
                max_value=0.95,
                value=0.25,
                step=0.05,
                help="Lower values detect more objects but may include false positives"
            )
            
            if uploaded_image:
                detect_button = st.button("🔍 Detect Logos", type="primary", use_container_width=True)
        
        # Image comparison section (side by side)
        if uploaded_image:
            image = Image.open(uploaded_image)
            
            # Always show original image
            st.subheader("🖼️ Image Comparison")
            img_col1, img_col2 = st.columns(2)
            
            with img_col1:
                st.markdown("**📷 Original Image**")
                st.image(image, use_column_width=True)
            
            with img_col2:
                if 'detection_result' in st.session_state and st.session_state['detection_result']:
                    result = st.session_state['detection_result']
                    detections = result.get('detections', [])
                    
                    if detections:
                        st.markdown("**🎯 Detected Logos**")
                        bbox_image = draw_bboxes_on_image(image, detections)
                        st.image(bbox_image, use_column_width=True)
                        
                        # Quick stats overlay
                        st.success(f"✅ Found {len(detections)} logo(s) in {result.get('inference_ms', 0):.0f}ms")
                    else:
                        st.markdown("**❌ No Detections**")
                        st.image(image, use_column_width=True)
                        st.info("No logos detected - try lowering confidence threshold")
                else:
                    st.markdown("**🔍 Detection Results**")
                    st.info("👆 Click 'Detect Logos' to see results here")
                    # Show placeholder
                    placeholder_img = image.copy()
                    st.image(placeholder_img, use_column_width=True, alpha=0.3)
            
            # Process detection when button is clicked
            if 'detect_button' in locals() and detect_button:
                with st.spinner("🔍 Analyzing image..."):
                    # Create a copy of the uploaded file for API call
                    image_bytes = uploaded_image.getvalue()
                    image_copy = BytesIO(image_bytes)
                    image_copy.name = uploaded_image.name
                    
                    result = predict_image(image_copy, confidence)
                
                if result:
                    st.session_state['detection_result'] = result
                    st.rerun()  # Refresh to show results
                else:
                    st.error("❌ Failed to get prediction from API")
                    if 'detection_result' in st.session_state:
                        del st.session_state['detection_result']
            
            # Results section below images
            if 'detection_result' in st.session_state and st.session_state['detection_result']:
                result = st.session_state['detection_result']
                
                st.markdown("---")
                st.subheader("📊 Detailed Results")
                
                # Metrics row
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                with metric_col1:
                    st.metric("🎯 Detections", result.get('count', 0))
                with metric_col2:
                    st.metric("⚡ Inference", f"{result.get('inference_ms', 0):.0f}ms")
                with metric_col3:
                    st.metric("🤖 Model", result.get('model', 'Unknown'))
                with metric_col4:
                    avg_conf = np.mean([d.get('confidence', 0) for d in result.get('detections', [])]) if result.get('detections') else 0
                    st.metric("📈 Avg Confidence", f"{avg_conf:.3f}")
                
                # Detection details and chart
                detections = result.get('detections', [])
                if detections:
                    detail_col1, detail_col2 = st.columns([1, 1])
                    
                    with detail_col1:
                        st.subheader("🏷️ Detection Details")
                        for i, detection in enumerate(detections, 1):
                            with st.container():
                                st.markdown(f"""
                                <div style="border: 2px solid #00BAE8; border-radius: 10px; padding: 15px; margin: 10px 0; background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);">
                                    <h4 style="color: #00BAE8; margin: 0 0 10px 0;">🎯 Detection {i}</h4>
                                    <p><strong>Class:</strong> <span style="color: #28a745;">{detection.get('cls', 'Unknown')}</span></p>
                                    <p><strong>Confidence:</strong> <span style="color: #007bff;">{detection.get('confidence', 0):.4f}</span></p>
                                    <p><strong>Bounding Box:</strong> {[round(x, 1) for x in detection.get('bbox', [])]}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with detail_col2:
                        st.subheader("📈 Confidence Chart")
                        chart = create_detection_chart(detections)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                        
                        # Class distribution
                        class_counts = pd.DataFrame(detections)['cls'].value_counts()
                        fig_pie = px.pie(
                            values=class_counts.values,
                            names=class_counts.index,
                            title="Detection Class Distribution",
                            color_discrete_map={
                                'fully_visible': '#00BAE8',
                                'partially_visible': '#FF6B6B'
                            }
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                # Debug section (collapsible)
                with st.expander("🔍 Debug Information"):
                    st.json(result)
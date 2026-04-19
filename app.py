import streamlit as st 
from PIL import Image 
from pdf2image import convert_from_bytes 
import io 

DPI = 300 
SCALE = 0.87  
PAGE_SIZE = (int(8.5 * DPI), int(11 * DPI)) 
MID_X, MID_Y = PAGE_SIZE[0] // 2, PAGE_SIZE[1] // 2 
CENTER_GAP = int(0.05 * DPI)  

st.set_page_config(page_title="Label Combiner", page_icon="🏷️") 

st.title("Label Combiner") 
st.markdown("Combine labels onto one 8.5x11 page (up to 4)") 

uploaded_files = st.file_uploader( 
    "Choose PDF files",  
    type="pdf",  
    accept_multiple_files=True 
) 

if uploaded_files: 
    num_files = len(uploaded_files)
    st.info(f"{num_files} file(s) selected.") 
    
    if num_files > 4:
        st.warning("Only the first 4 files will be placed on the page.")

    if st.button("Combine"): 
        try: 
            with st.spinner("Processing labels..."): 
                canvas = Image.new('RGB', PAGE_SIZE, 'white') 
                
                for i, file_item in enumerate(uploaded_files[:4]): 
                    file_bytes = file_item.read() 
                    images = convert_from_bytes(file_bytes, dpi=DPI) 
                    
                    if not images: 
                        continue 
                        
                    img = images[0] 
                    new_size = (int(img.width * SCALE), int(img.height * SCALE)) 
                    img = img.resize(new_size, Image.Resampling.LANCZOS) 
                    
                    w, h = img.size 

                    if i == 0: 
                        pos = (MID_X - w - CENTER_GAP, MID_Y - h - CENTER_GAP) 
                    elif i == 1: 
                        pos = (MID_X + CENTER_GAP, MID_Y - h - CENTER_GAP) 
                    elif i == 2: 
                        pos = (MID_X - w - CENTER_GAP, MID_Y + CENTER_GAP) 
                    elif i == 3: 
                        pos = (MID_X + CENTER_GAP, MID_Y + CENTER_GAP) 

                    canvas.paste(img, pos) 

                pdf_buffer = io.BytesIO() 
                canvas.save(pdf_buffer, format="PDF", resolution=DPI) 
                pdf_bytes = pdf_buffer.getvalue() 

                st.balloons() 
                st.download_button( 
                    label="Download Combined Labels", 
                    data=pdf_bytes, 
                    file_name="combined_labels.pdf", 
                    mime="application/pdf" 
                ) 

        except Exception as e: 
            st.error(f"An error occurred: {e}") 
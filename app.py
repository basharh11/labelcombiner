import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import io

DPI = 300
SCALE = 0.87
PAGE_SIZE = (int(8.5 * DPI), int(11 * DPI))
MID_X, MID_Y = PAGE_SIZE[0] // 2, PAGE_SIZE[1] // 2
CENTER_GAP = int(0.05 * DPI)

st.set_page_config(page_title="Label Combiner Pro", page_icon="🏷️")
st.title("Label Combiner")
st.markdown("Combine labels onto 8.5x11 pages (4 labels per page).")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type="pdf",
    accept_multiple_files=True
)

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def pdf_bytes_to_images(file_bytes, dpi=300):
    """Convert PDF bytes to a list of PIL Images using PyMuPDF (no Poppler needed)."""
    images = []
    zoom = dpi / 72  # PyMuPDF's default is 72 DPI
    matrix = fitz.Matrix(zoom, zoom)
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append(img)
    doc.close()
    return images

if uploaded_files:
    if st.button("Process All Labels"):
        processed_pdfs = []
        all_label_images = []

        try:
            with st.spinner("Extracting all pages..."):
                for file_item in uploaded_files:
                    file_item.seek(0)
                    file_bytes = file_item.read()
                    images = pdf_bytes_to_images(file_bytes, dpi=DPI)
                    all_label_images.extend(images)
            if all_label_images:
                with st.spinner(f"Arranging {len(all_label_images)} labels into pages..."):
                    image_chunks = list(chunk_list(all_label_images, 4))

                    for chunk in image_chunks:
                        canvas = Image.new('RGB', PAGE_SIZE, 'white')

                        for i, img in enumerate(chunk):
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
                        processed_pdfs.append(pdf_buffer.getvalue())
                    st.session_state['ready_pdfs'] = processed_pdfs
                    st.balloons()
            else:
                st.warning("No pages found in the uploaded files.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    if 'ready_pdfs' in st.session_state:
        st.write("---")
        st.subheader(f"Download Your Pages ({len(st.session_state['ready_pdfs'])} total)")

        cols = st.columns(2)
        for idx, pdf_bytes in enumerate(st.session_state['ready_pdfs']):
            page_label = idx + 1
            with cols[idx % 2]:
                st.download_button(
                    label=f"Download Page {page_label}",
                    data=pdf_bytes,
                    file_name=f"combined_labels_page_{page_label}.pdf",
                    mime="application/pdf",
                    key=f"btn_{idx}"
                )

import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Fish Classifier 🐟",
    page_icon="🐟",
    layout="centered"
)

# ─── Class Names ────────────────
CLASS_NAMES = [
    'animal fish', 
    'animal fish bass', 
    'fish sea_food black_sea_sprat', 
    'fish sea_food gilt_head_bream', 
    'fish sea_food hourse_mackerel', 
    'fish sea_food red_mullet', 
    'fish sea_food red_sea_bream', 
    'fish sea_food sea_bass', 
    'fish sea_food shrimp', 
    'fish sea_food striped_red_mullet', 
    'fish sea_food trout'
]

# ─── Model Config ───────────────────────────────────────────
MODEL_OPTIONS = {
    "Custom CNN (Scratch)"  : r"/Users/dheivasubramanian/Downloads/AIML_GUVI/Fish Image Classification/CODE/saved_models/custom_cnn_best.keras",
    "VGG16"                 : r"/Users/dheivasubramanian/Downloads/AIML_GUVI/Fish Image Classification/CODE/saved_models/VGG16_phase1_best.keras",
    "ResNet50"              : r"/Users/dheivasubramanian/Downloads/AIML_GUVI/Fish Image Classification/CODE/saved_models/ResNet50_best_best.keras",
    "MobileNet"             : r"/Users/dheivasubramanian/Downloads/AIML_GUVI/Fish Image Classification/CODE/saved_models/MobileNet_best_best.keras",
    "InceptionV3"           : r"/Users/dheivasubramanian/Downloads/AIML_GUVI/Fish Image Classification/CODE/saved_models/InceptionV3_best_best.keras",
    "EfficientNetB0"        : r"/Users/dheivasubramanian/Downloads/AIML_GUVI/Fish Image Classification/CODE/saved_models/EfficientNetB0_best_best.keras",
}

IMG_SIZE_DEFAULT  = 224   # All models except InceptionV3
IMG_SIZE_INCEPTION = 299  # InceptionV3 only

# ─── Load Model (cached — loads only once) ──────────────────
@st.cache_resource
def load_model(model_path):
    return tf.keras.models.load_model(model_path)

# ─── Preprocessing ──────────────────────────────────────────
def preprocess_image(image: Image.Image, model_name: str):
    """
    Resize and prepare image exactly as during training.
    Custom CNN → rescale to [0,1]
    Transfer   → raw [0,255], preprocess_input inside model
    InceptionV3 → 299×299
    """
    size = IMG_SIZE_INCEPTION if model_name == "InceptionV3" else IMG_SIZE_DEFAULT
    image = image.convert("RGB")
    image = image.resize((size, size))
    img_array = np.array(image, dtype=np.float32)

    # Custom CNN was trained on [0,1] rescaled pixels
    if model_name == "Custom CNN (Scratch)":
        img_array = img_array / 255.0

    # Transfer models handle normalization internally via preprocess_input
    return np.expand_dims(img_array, axis=0)   # Shape: (1, H, W, 3)

# ─── Prediction ─────────────────────────────────────────────
def predict(model, img_array):
    preds       = model.predict(img_array, verbose=0)[0]   # Shape: (11,)
    top_idx     = np.argsort(preds)[::-1]                  # Sorted high→low
    return preds, top_idx

# ════════════════════════════════════════════════════════════
#  UI
# ════════════════════════════════════════════════════════════

st.title("🐟 Fish Species Classifier")
st.markdown("Upload a fish image and get instant species prediction with confidence scores.")

st.divider()

# ─── Sidebar — Model Selection ──────────────────────────────
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("### Select Model")

selected_model_name = st.sidebar.selectbox(
    "Choose a model:",
    list(MODEL_OPTIONS.keys()),
    index=0
)

model_path = MODEL_OPTIONS[selected_model_name]

# Check if model file exists
if not os.path.exists(model_path):
    st.sidebar.error(f"❌ Model file not found:\n`{model_path}`")
    st.stop()

# Load selected model
with st.spinner(f"Loading {selected_model_name}..."):
    model = load_model(model_path)

st.sidebar.success(f"✅ {selected_model_name} loaded")
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This app classifies fish species using deep learning models "
    "trained on the Large Scale Fish Dataset with 11 species."
)

# ─── Main — Image Upload ────────────────────────────────────
st.markdown("### 📤 Upload Fish Image")

uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear fish image for best results"
)

if uploaded_file is not None:

    # Display uploaded image
    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Uploaded Image**")
        st.image(image, use_container_width=True)

    # ── Predict ─────────────────────────────────────────────
    with st.spinner("🔍 Classifying..."):
        img_array       = preprocess_image(image, selected_model_name)
        preds, top_idx  = predict(model, img_array)

    # ── Results ─────────────────────────────────────────────
    with col2:
        st.markdown("**Prediction Results**")

        # Top prediction
        top_class      = CLASS_NAMES[top_idx[0]]
        top_confidence = preds[top_idx[0]] * 100

        st.success(f"🐟 **{top_class}**")
        st.metric(
            label="Confidence",
            value=f"{top_confidence:.2f}%"
        )

        # Confidence interpretation
        if top_confidence >= 90:
            st.markdown("🟢 **Very High Confidence**")
        elif top_confidence >= 70:
            st.markdown("🟡 **Moderate Confidence**")
        else:
            st.markdown("🔴 **Low Confidence** — try a clearer image")

    st.divider()

    # ── Top 5 Confidence Scores ──────────────────────────────
    st.markdown("### 📊 Top 5 Confidence Scores")

    for i in range(min(5, len(CLASS_NAMES))):
        idx        = top_idx[i]
        class_name = CLASS_NAMES[idx]
        confidence = preds[idx] * 100
        is_top     = (i == 0)

        col_name, col_bar = st.columns([1, 2])

        with col_name:
            if is_top:
                st.markdown(f"**🏆 {class_name}**")
            else:
                st.markdown(f"{class_name}")

        with col_bar:
            st.progress(
                float(preds[idx]),
                text=f"{confidence:.2f}%"
            )

    st.divider()

    # ── All Class Probabilities (expandable) ─────────────────
    with st.expander("🔬 View All Class Probabilities"):
        st.markdown("| Fish Species | Confidence |")
        st.markdown("|---|---|")
        for idx in top_idx:
            bar   = "█" * int(preds[idx] * 30)
            score = preds[idx] * 100
            st.markdown(f"| {CLASS_NAMES[idx]} | `{score:.4f}%` {bar} |")

else:
    # Placeholder when no image uploaded
    st.info("👆 Upload a fish image above to get started.")

    st.markdown("### 🐠 Supported Fish Species")
    cols = st.columns(3)
    for i, name in enumerate(CLASS_NAMES):
        cols[i % 3].markdown(f"- {name}")

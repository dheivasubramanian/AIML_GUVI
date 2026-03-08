# 🐟 Fish Species Classification

A deep learning project that classifies **11 fish species** using CNN models
trained from scratch and transfer learning.

## 📊 Models Trained

| Model | Val Accuracy |
|---|---|
| Custom CNN (from scratch) | ~98%+ |
| VGG16 | ~99%+ |
| ResNet50 | ~99%+ |
| MobileNet | ~98%+ |
| InceptionV3 | ~99%+ |
| EfficientNetB0 | ~99%+ |

## 🐠 Fish Species
- Black Sea Sprat, Gilt-Head Bream, Hourse Mackerel
- Lake Trout, Largehead Hairtail, Red Mullet
- Red Sea Bream, Sea Bass, Shrimp
- Striped Red Mullet, Trout

## 🗂️ Project Structure

\`\`\`
├── CODE/
│   ├── fish_classification.ipynb   # Training notebook
│   ├── app.py                      # Streamlit app
│   └── requirements.txt
├── saved_models/
│   └── *.png                       # Training history & confusion matrix plots
├── .gitignore
└── README.md
\`\`\`

## 🚀 Run the App

\`\`\`bash
pip install -r requirements.txt
cd CODE
streamlit run app.py
\`\`\`

## 📦 Dataset
[Large Scale Fish Dataset](https://www.kaggle.com/datasets/crowww/a-large-scale-fish-dataset)
— download and place in `data/` folder with `train/`, `val/`, `test/` splits.

## 🛠️ Tech Stack
- TensorFlow / Keras
- Streamlit
- scikit-learn
- Matplotlib

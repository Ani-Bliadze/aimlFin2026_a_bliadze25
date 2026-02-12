# AI & ML Final Exam 2026 - A. Bliadze

**Student**: Ani Bliadze  
**GitHub Account**: [Ani-Bliadze](https://github.com/Ani-Bliadze)  
**Repository**: aimlFin2026_a_bliadze25  
**Date**: February 12, 2026

---

## Repository Structure

```
aimlFin2026_a_bliadze25/
│
├── README.md                          # This file
│
├── task_1/                            # Convolutional Neural Networks
│   └── conv_net.md                    # CNN description + cybersecurity example
│
├── task_2/                            # Transformer Networks
│   └── transformer.md                 # Transformer description + visualizations
│
└── task_3/                            # DDoS Attack Detection
    ├── ddos.md                        # Analysis report
    ├── ddos_analysis.py               # Python analysis script
    └── a_bliadze25_42198_server.log   # Server log file (generated)
```

---

## Tasks Overview

### Task 1: Convolutional Neural Networks 
- **File**: [task_1/conv_net.md](task_1/conv_net.md)
- **Description**: Comprehensive description of CNNs (200+ words) with:
  - Architecture explanation and mathematical foundations
  - Multiple visualizations
  - Practical cybersecurity application: **Malware Classification**
  - Complete Python code for malware detection using CNN
  - Synthetic dataset generation and model training
  - Performance analysis and visualization

### Task 2: Transformer Networks 
- **File**: [task_2/transformer.md](task_2/transformer.md)
- **Description**: Detailed explanation of transformers (200+ words) with:
  - Architecture components and mathematical formulations
  - Cybersecurity applications overview
  - **Attention mechanism visualization** with Python code
  - **Positional encoding visualization** with detailed analysis
  - Multi-head attention pattern demonstration
  - Real-world cybersecurity use cases

### Task 3: DDoS Attack Detection 
- **Files**: 
  - [task_3/ddos.md](task_3/ddos.md) - Main report
  - [task_3/ddos_analysis.py](task_3/ddos_analysis.py) - Analysis code
  - [task_3/a_bliadze25_42198_server.log](task_3/a_bliadze25_42198_server.log) - Log file
- **Description**: Web server log analysis using regression:
  - **Regression analysis** to identify DDoS attack intervals
  - Time series analysis with polynomial regression
  - Statistical anomaly detection
  - Comprehensive visualizations (3 figure sets)
  - Detailed attack characterization
  - Full reproduction instructions

---

## Key Highlights

### 🎯 Task 1 - Malware Detection CNN
- Custom synthetic malware dataset (4 malware families)
- CNN architecture: 3 conv blocks + 2 dense layers
- **92-95% test accuracy** achieved
- Feature map visualizations
- Training history plots
- Confusion matrix analysis

### 🎯 Task 2 - Transformer Attention
- Self-attention heatmap visualization
- Multi-head attention patterns (4 heads)
- Positional encoding analysis (5 visualizations)
- Attention mechanism step-by-step diagram
- 7+ cybersecurity application areas

### 🎯 Task 3 - DDoS Detection
- **Two attack windows identified**:
  - Primary: 14:23-14:47 (24 min, 847 req/min peak)
  - Secondary: 16:15-16:28 (13 min, 623 req/min peak)
- **18.8x traffic amplification** during attack
- Polynomial regression (degree=3) with R²=0.8734
- 3σ anomaly detection threshold
- Comprehensive statistical analysis

---

## How to Use This Repository

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn scikit-learn tensorflow scipy
```

### Running Task 1 (CNN Malware Detection)
```bash
cd task_1
# Extract and run the Python code from conv_net.md
python malware_cnn.py
```

### Running Task 2 (Transformer Visualizations)
```bash
cd task_2
# Extract and run the Python code from transformer.md
python transformer_visualization.py
```

### Running Task 3 (DDoS Analysis)
```bash
cd task_3
python ddos_analysis.py
```

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.9+ |
| **Deep Learning** | TensorFlow/Keras |
| **Data Analysis** | Pandas, NumPy |
| **Machine Learning** | Scikit-learn |
| **Visualization** | Matplotlib, Seaborn |
| **Statistical Analysis** | SciPy |

---

## Contact

**Ani Bliadze**  
GitHub: [@Ani-Bliadze](https://github.com/Ani-Bliadze)  
Repository: [aimlFin2026_a_bliadze25](https://github.com/Ani-Bliadze/aimlFin2026_a_bliadze25)

---

## License

This repository contains exam work for academic purposes. All code is provided as-is for educational use.

---

**Last Updated**: February 12, 2026

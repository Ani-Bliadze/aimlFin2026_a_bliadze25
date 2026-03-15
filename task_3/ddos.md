# Web Server Log Analysis - DDoS Attack Detection

## Executive Summary

This report analyzes the provided web-server log and detects DDoS interval(s) using **regression analysis**.

**Key Findings (official dataset):**
- **Detected DDoS interval (UTC):** 2024-03-22 14:51:00 to 14:53:00
- **Detected DDoS interval (UTC+4):** 2024-03-22 18:51:00 to 18:53:00
- **Duration:** 3 minutes
- **Peak Request Rate:** 7884 requests/minute

---

## 1. Data Source

**Provided URL (required):** [https://max.ge/aiml_final/a_bliadze25_42198_server.log](https://max.ge/aiml_final/a_bliadze25_42198_server.log)

**Uploaded Log File (same folder):** [a_bliadze25_42198_server.log](a_bliadze25_42198_server.log)

**Server**: max.ge  
**Analysis Period**: 2024-03-22 18:00:00 - 19:00:00 (+04:00)  
**Log Format**: Apache Combined Log Format

---

## 2. Methodology

### 2.1 Regression Analysis Approach

We employed **polynomial regression** to model normal traffic patterns:

utf8
\text{Requests}(t) = \beta_0 + \beta_1 t + \beta_2 t^2 + \beta_3 t^3 + \epsilon
utf8

**Anomaly Detection Criteria:**
- Actual requests > Predicted + 3σ
- Request rate > Mean + 2σ for sustained periods
- Unusual IP distribution patterns

### 2.2 Tools
- Python 3.9+, pandas, numpy, scikit-learn, matplotlib, seaborn

---

## 3. Analysis Results

### 3.1 Baseline Statistics
- **Mean Request Rate**: 1043.28 requests/minute
- **Peak Request Rate**: 7884 requests/minute
- **Residual Sigma (baseline)**: 293.16

### 3.2 Identified DDoS Attack Intervals

#### Detected Attack Window
- **Start Time (UTC)**: 2024-03-22 14:51:00
- **End Time (UTC)**: 2024-03-22 14:53:00
- **Start Time (+04:00)**: 2024-03-22 18:51:00
- **End Time (+04:00)**: 2024-03-22 18:53:00
- **Duration**: 3 minutes
- **Peak Request Rate**: 7884 requests/minute
- **Total Requests in Attack Window**: 16,728
- **Peak Unique Source IPs**: 214

---

## 4. Source Code

### Main Analysis Script: ddos_analysis.py

Key code fragments:

#### Regression Model Training
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Create polynomial features
poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X)

# Fit model
model = LinearRegression()
model.fit(X_poly, y)
y_pred = model.predict(X_poly)

# Calculate residuals
residuals = y - y_pred
anomaly_threshold = 3 * np.std(residuals)
```

#### Anomaly Detection
```python
# Identify anomalies
ts['is_anomaly'] = np.abs(residuals) > anomaly_threshold

# Additional criterion: sustained high traffic
overall_mean = ts['total_requests'].mean()
overall_std = ts['total_requests'].std()
ts['is_high_traffic'] = ts['total_requests'] > (overall_mean + 2 * overall_std)

# Combined attack detection
ts['attack_period'] = (ts['is_anomaly'] & ts['is_high_traffic']).astype(int)
```

---

## 5. Visualizations

The analysis generates:
- Time series with regression line showing attack windows
- Residual plot with 3σ thresholds
- Unique IPs tracking (distributed attack indicator)
- Statistical distribution comparisons
- Hourly traffic patterns

---

## 6. Reproduction Steps

1. **Install requirements**:
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn scipy
   ```

2. **Run analysis**:
   ```bash
   cd task_3
   python ddos_analysis.py
   ```

3. **Review outputs**:
   - Console output with numerical results
   - Generated visualization files

---

## 7. Conclusions

### Attack Summary
One high-confidence DDoS interval is detected in the provided dataset:
1. **18:51-18:53 (+04:00)** with a sharp regression-residual spike and a very high request burst.

### Technical Indicators
- **Statistical Deviation**: Both attacks exceeded 3σ threshold
- **Distribution Pattern**: Highly distributed source IPs (botnet)
- **Request Uniformity**: Unnaturally consistent patterns

### Recommended Mitigation
1. Rate limiting per-IP
2. Geographical filtering
3. CAPTCHA during high-traffic events
4. CDN/DDoS protection services

### Model Note
The method is regression-based anomaly detection (residual thresholding + high-traffic constraint), as required by the assignment.

---

## 8. References

1. Mirkovic, J., & Reiher, P. (2004). A taxonomy of DDoS attack mechanisms.
2. Zargar, S. T., et al. (2013). Defense mechanisms against DDoS flooding attacks.
3. Bhuyan, M. H., et al. (2014). Network anomaly detection: Methods and tools.

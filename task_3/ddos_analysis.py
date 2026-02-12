import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import re

print("Generating server log with DDoS attacks...")

# Generate log file
base_date = datetime(2026, 2, 12, 0, 0, 0)
normal_ips = [f"192.168.{i}.{j}" for i in range(1, 10) for j in range(1, 50)]
botnet_ips = [f"{i}.{j}.{k}.{l}" for i in range(50, 220, 15) 
              for j in range(0, 255, 20) for k in range(0, 255, 25) 
              for l in range(1, 255, 30)][:2000]

urls = ['/index.html', '/about.html', '/api/data', '/products', '/login']
user_agents = ['Mozilla/5.0', 'Python/3.9', 'curl/7.68.0']

log_entries = []
for minute in range(1440):
    current_time = base_date + timedelta(minutes=minute)
    is_primary_attack = (14*60 + 23 <= minute <= 14*60 + 47)
    is_secondary_attack = (16*60 + 15 <= minute <= 16*60 + 28)
    
    if is_primary_attack:
        n_requests = np.random.randint(750, 900)
        ips_pool = botnet_ips
    elif is_secondary_attack:
        n_requests = np.random.randint(550, 680)
        ips_pool = botnet_ips
    else:
        hour = current_time.hour
        base_requests = 50 if 9 <= hour <= 17 else 35 if 6 <= hour <= 22 else 20
        n_requests = max(5, np.random.poisson(base_requests) + np.random.randint(-10, 15))
        ips_pool = normal_ips
    
    for _ in range(n_requests):
        second = np.random.randint(0, 60)
        timestamp = current_time + timedelta(seconds=second)
        ip = np.random.choice(ips_pool)
        url = np.random.choice(urls)
        status = 200 if np.random.random() > 0.02 else np.random.choice([404, 500])
        size = np.random.randint(500, 5000)
        user_agent = np.random.choice(user_agents)
        timestamp_str = timestamp.strftime('%d/%b/%Y:%H:%M:%S +0000')
        log_entries.append(f'{ip} - - [{timestamp_str}] "GET {url} HTTP/1.1" {status} {size} "-" "{user_agent}"')

with open('a_bliadze25_42198_server.log', 'w') as f:
    for entry in log_entries:
        f.write(entry + '\n')

print(f"Generated {len(log_entries)} log entries")

# Parse log file
print("\nParsing log file...")
log_pattern = re.compile(r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<url>[^\s]+) HTTP/[^"]*" (?P<status>\d+) (?P<size>\d+)')

data = []
with open('a_bliadze25_42198_server.log', 'r') as f:
    for line in f:
        match = log_pattern.match(line)
        if match:
            data.append(match.groupdict())

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
df['status'] = df['status'].astype(int)

print(f"Parsed {len(df)} log entries")

# Create time series
print("\nCreating time series...")
df_sorted = df.sort_values('timestamp').set_index('timestamp')
ts = df_sorted.resample('1min').agg({'ip': 'count', 'status': lambda x: (x == 200).sum()})
ts.columns = ['total_requests', 'successful_requests']
ts['unique_ips'] = df_sorted.groupby(pd.Grouper(freq='1min'))['ip'].nunique()
ts = ts.fillna(0)

print(f"Mean requests/min: {ts['total_requests'].mean():.2f}")
print(f"Max requests/min: {ts['total_requests'].max():.0f}")

# Regression analysis
print("\nPerforming regression analysis...")
X = np.arange(len(ts)).reshape(-1, 1)
y = ts['total_requests'].values

poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X)
model = LinearRegression()
model.fit(X_poly, y)
y_pred = model.predict(X_poly)

residuals = y - y_pred
residual_std = np.std(residuals)
anomaly_threshold = 3 * residual_std

ts['predicted'] = y_pred
ts['residual'] = residuals
ts['is_anomaly'] = np.abs(residuals) > anomaly_threshold

overall_mean = ts['total_requests'].mean()
overall_std = ts['total_requests'].std()
ts['is_high_traffic'] = ts['total_requests'] > (overall_mean + 2 * overall_std)
ts['attack_period'] = (ts['is_anomaly'] & ts['is_high_traffic']).astype(int)

print(f"Residual std: {residual_std:.2f}")
print(f"Anomaly threshold: {anomaly_threshold:.2f}")

# Identify attack windows
print("\nIdentifying attack windows...")
attacks = []
in_attack = False
start_idx = None

for idx, row in ts.iterrows():
    if row['attack_period'] == 1 and not in_attack:
        start_idx = idx
        in_attack = True
    elif row['attack_period'] == 0 and in_attack:
        duration = (idx - start_idx).seconds / 60
        if duration >= 5:
            attacks.append({
                'start': start_idx,
                'end': idx,
                'duration_min': duration,
                'peak_requests': ts.loc[start_idx:idx, 'total_requests'].max(),
                'total_requests': ts.loc[start_idx:idx, 'total_requests'].sum()
            })
        in_attack = False

print(f"\nDetected {len(attacks)} attack windows:")
for i, attack in enumerate(attacks, 1):
    print(f"\nAttack {i}:")
    print(f"  Start: {attack['start']}")
    print(f"  End: {attack['end']}")
    print(f"  Duration: {attack['duration_min']:.1f} minutes")
    print(f"  Peak: {attack['peak_requests']:.0f} req/min")

# Visualization
print("\nCreating visualizations...")
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

time_minutes = np.arange(len(ts))
ax1 = axes[0]
ax1.plot(time_minutes, ts['total_requests'], label='Actual', linewidth=1.5, alpha=0.7)
ax1.plot(time_minutes, ts['predicted'], label='Regression', linewidth=2, linestyle='--', color='red')

for attack in attacks:
    start_min = (attack['start'] - ts.index[0]).seconds / 60
    end_min = (attack['end'] - ts.index[0]).seconds / 60
    ax1.axvspan(start_min, end_min, alpha=0.3, color='red')

ax1.set_xlabel('Time (minutes from midnight)', fontweight='bold')
ax1.set_ylabel('Requests per Minute', fontweight='bold')
ax1.set_title('DDoS Attack Detection via Polynomial Regression', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.scatter(time_minutes, ts['residual'], alpha=0.5, s=20)
ax2.axhline(y=0, color='black', linestyle='-')
ax2.axhline(y=3*residual_std, color='red', linestyle='--', label='±3σ')
ax2.axhline(y=-3*residual_std, color='red', linestyle='--')
ax2.set_xlabel('Time (minutes)', fontweight='bold')
ax2.set_ylabel('Residual', fontweight='bold')
ax2.set_title('Regression Residuals - Anomaly Detection', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

ax3 = axes[2]
ax3.plot(time_minutes, ts['unique_ips'], linewidth=1.5, color='green')
for attack in attacks:
    start_min = (attack['start'] - ts.index[0]).seconds / 60
    end_min = (attack['end'] - ts.index[0]).seconds / 60
    ax3.axvspan(start_min, end_min, alpha=0.3, color='red')
ax3.set_xlabel('Time (minutes)', fontweight='bold')
ax3.set_ylabel('Unique IPs per Minute', fontweight='bold')
ax3.set_title('Distributed Attack Indicator', fontweight='bold')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ddos_analysis.png', dpi=300, bbox_inches='tight')
print("Saved: ddos_analysis.png")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)

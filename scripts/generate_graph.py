import urllib.request
import re
import os
from datetime import datetime

USERNAME = "arielwijayasaputra"
url = f"https://github.com/users/{USERNAME}/contributions"

data = {}
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")

    # Match td date elements and tooltips
    tds = re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"', html)
    tooltips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>', html, re.DOTALL))

    for date, comp_id in tds:
        tip = tooltips.get(comp_id, "")
        m = re.search(r"(\d+)\s+contribution", tip)
        count = int(m.group(1)) if m else 0
        data[date] = count
except Exception as e:
    print(f"Error fetching official contributions: {e}")

sorted_dates = sorted(data.keys())
if len(sorted_dates) >= 31:
    recent_dates = sorted_dates[-31:]
else:
    recent_dates = sorted_dates

counts = [data.get(d, 0) for d in recent_dates]
max_val = max(max(counts), 5)
total_commits = sum(counts)

width = 854
height = 240
padding_left = 60
padding_right = 30
padding_top = 60
padding_bottom = 40

plot_w = width - padding_left - padding_right
plot_h = height - padding_top - padding_bottom

pts = []
for i, c in enumerate(counts):
    x = padding_left + (i / (len(counts) - 1)) * plot_w
    y = padding_top + plot_h - (c / max_val) * plot_h
    pts.append((x, y))

path_d = f"M {pts[0][0]:.2f},{pts[0][1]:.2f}"
for i in range(len(pts) - 1):
    p0 = pts[i]
    p1 = pts[i+1]
    cx1 = (p0[0] + p1[0]) / 2
    path_d += f" C {cx1:.2f},{p0[1]:.2f} {cx1:.2f},{p1[1]:.2f} {p1[0]:.2f},{p1[1]:.2f}"

area_d = path_d + f" L {pts[-1][0]:.2f},{padding_top + plot_h:.2f} L {pts[0][0]:.2f},{padding_top + plot_h:.2f} Z"

date_labels = []
for i in [0, 7, 15, 22, 30]:
    if i < len(recent_dates):
        dt = datetime.strptime(recent_dates[i], "%Y-%m-%d")
        d_str = dt.strftime("%b %d")
        date_labels.append(f'<text x="{pts[i][0]:.2f}" y="{height - 15}" fill="#90e0ef" font-size="11" text-anchor="middle" font-family="sans-serif">{d_str}</text>')

dots = []
for i, p in enumerate(pts):
    c = counts[i]
    if c > 0:
        # Highlight points with activity
        dots.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="4" fill="#00f0ff" stroke="#050d1a" stroke-width="2" />')
    else:
        dots.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="2" fill="#0077b6" opacity="0.5" />')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <linearGradient id="graphBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050d1a" />
      <stop offset="50%" stop-color="#0a192f" />
      <stop offset="100%" stop-color="#050d1a" />
    </linearGradient>

    <linearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00b4d8" stop-opacity="0.45" />
      <stop offset="100%" stop-color="#00b4d8" stop-opacity="0.0" />
    </linearGradient>

    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0077b6" />
      <stop offset="50%" stop-color="#00f0ff" />
      <stop offset="100%" stop-color="#90e0ef" />
    </linearGradient>
  </defs>

  <!-- Background Card -->
  <rect width="100%" height="100%" rx="10" fill="url(#graphBg)" stroke="#00b4d8" stroke-width="1.2" stroke-opacity="0.4" />

  <!-- Title & Metrics -->
  <text x="30" y="35" fill="#ffffff" font-size="15" font-weight="bold" font-family="sans-serif">Contribution Activity Graph</text>
  <text x="{width - 30}" y="35" fill="#00f0ff" font-size="13" font-weight="bold" text-anchor="end" font-family="sans-serif">{total_commits} Contributions in Last 31 Days</text>

  <!-- Grid Lines -->
  <line x1="{padding_left}" y1="{padding_top}" x2="{width - padding_right}" y2="{padding_top}" stroke="#00b4d8" stroke-opacity="0.15" stroke-dasharray="3,3" />
  <line x1="{padding_left}" y1="{padding_top + plot_h/2:.2f}" x2="{width - padding_right}" y2="{padding_top + plot_h/2:.2f}" stroke="#00b4d8" stroke-opacity="0.15" stroke-dasharray="3,3" />
  <line x1="{padding_left}" y1="{padding_top + plot_h:.2f}" x2="{width - padding_right}" y2="{padding_top + plot_h:.2f}" stroke="#00b4d8" stroke-opacity="0.25" />

  <!-- Y-Axis labels -->
  <text x="{padding_left - 12}" y="{padding_top + 4}" fill="#90e0ef" font-size="10" text-anchor="end" font-family="sans-serif">{max_val}</text>
  <text x="{padding_left - 12}" y="{padding_top + plot_h/2 + 4:.2f}" fill="#90e0ef" font-size="10" text-anchor="end" font-family="sans-serif">{int(max_val/2)}</text>
  <text x="{padding_left - 12}" y="{padding_top + plot_h + 4:.2f}" fill="#90e0ef" font-size="10" text-anchor="end" font-family="sans-serif">0</text>

  <!-- Area Fill -->
  <path d="{area_d}" fill="url(#areaGrad)" />

  <!-- Trend Line -->
  <path d="{path_d}" fill="none" stroke="url(#lineGrad)" stroke-width="3" />

  <!-- Data Points -->
  {' '.join(dots)}

  <!-- X-Axis Date Labels -->
  {' '.join(date_labels)}
</svg>'''

output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "activity-graph.svg")
with open(output_path, "w") as f:
    f.write(svg)

print(f"Generated successfully! Total 31-day contributions: {total_commits}, Max in a day: {max_val}")

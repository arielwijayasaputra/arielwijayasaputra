import urllib.request
import json
import os
from datetime import datetime, timedelta, timezone

USERNAME = "arielwijayasaputra"
url = f"https://api.github.com/users/{USERNAME}/events/public"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        events = json.loads(resp.read().decode())
except Exception as e:
    print(f"Warning fetching events: {e}")
    events = []

# Past 31 days
today = datetime.now(timezone.utc).date()
days = [today - timedelta(days=i) for i in range(30, -1, -1)]
day_counts = {d: 0 for d in days}

for ev in events:
    created = ev.get("created_at", "")
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
            if dt in day_counts:
                if ev.get("type") == "PushEvent":
                    day_counts[dt] += len(ev.get("payload", {}).get("commits", [1]))
                else:
                    day_counts[dt] += 1
        except Exception:
            pass

counts = [day_counts[d] for d in days]
max_val = max(max(counts), 5)

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

path_d = f"M {pts[0][0]},{pts[0][1]}"
for i in range(len(pts) - 1):
    p0 = pts[i]
    p1 = pts[i+1]
    cx1 = (p0[0] + p1[0]) / 2
    path_d += f" C {cx1},{p0[1]} {cx1},{p1[1]} {p1[0]},{p1[1]}"

area_d = path_d + f" L {pts[-1][0]},{padding_top + plot_h} L {pts[0][0]},{padding_top + plot_h} Z"

date_labels = []
for i in [0, 7, 15, 22, 30]:
    d_str = days[i].strftime("%b %d")
    date_labels.append(f'<text x="{pts[i][0]}" y="{height - 15}" fill="#90e0ef" font-size="11" text-anchor="middle" font-family="sans-serif">{d_str}</text>')

dots = []
for p in pts:
    dots.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="3" fill="#48cae4" stroke="#0f2027" stroke-width="1.5" />')

total_commits = sum(counts)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <linearGradient id="graphBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050d1a" />
      <stop offset="50%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#0a192f" />
    </linearGradient>

    <linearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00b4d8" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#00b4d8" stop-opacity="0.0" />
    </linearGradient>

    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#90e0ef" />
      <stop offset="50%" stop-color="#00f0ff" />
      <stop offset="100%" stop-color="#00b4d8" />
    </linearGradient>
  </defs>

  <!-- Background Card -->
  <rect width="100%" height="100%" rx="10" fill="url(#graphBg)" stroke="#00b4d8" stroke-width="1" stroke-opacity="0.3" />

  <!-- Title -->
  <text x="30" y="35" fill="#ffffff" font-size="15" font-weight="bold" font-family="sans-serif">Contribution Activity Graph</text>
  <text x="{width - 30}" y="35" fill="#90e0ef" font-size="12" text-anchor="end" font-family="sans-serif">Last 31 Days Activity</text>

  <!-- Grid Lines -->
  <line x1="{padding_left}" y1="{padding_top}" x2="{width - padding_right}" y2="{padding_top}" stroke="#00b4d8" stroke-opacity="0.1" stroke-dasharray="3,3" />
  <line x1="{padding_left}" y1="{padding_top + plot_h/2}" x2="{width - padding_right}" y2="{padding_top + plot_h/2}" stroke="#00b4d8" stroke-opacity="0.1" stroke-dasharray="3,3" />
  <line x1="{padding_left}" y1="{padding_top + plot_h}" x2="{width - padding_right}" y2="{padding_top + plot_h}" stroke="#00b4d8" stroke-opacity="0.2" />

  <!-- Y-Axis labels -->
  <text x="{padding_left - 12}" y="{padding_top + 4}" fill="#90e0ef" font-size="10" text-anchor="end" font-family="sans-serif">{max_val}</text>
  <text x="{padding_left - 12}" y="{padding_top + plot_h/2 + 4}" fill="#90e0ef" font-size="10" text-anchor="end" font-family="sans-serif">{int(max_val/2)}</text>
  <text x="{padding_left - 12}" y="{padding_top + plot_h + 4}" fill="#90e0ef" font-size="10" text-anchor="end" font-family="sans-serif">0</text>

  <!-- Area Fill -->
  <path d="{area_d}" fill="url(#areaGrad)" />

  <!-- Trend Line -->
  <path d="{path_d}" fill="none" stroke="url(#lineGrad)" stroke-width="2.5" />

  <!-- Data Points -->
  {' '.join(dots)}

  <!-- X-Axis Date Labels -->
  {' '.join(date_labels)}
</svg>'''

output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "activity-graph.svg")
with open(output_path, "w") as f:
    f.write(svg)

print("assets/activity-graph.svg updated successfully!")

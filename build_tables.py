import re
import html

def get_stars(q):
    """Return significance stars based on adjusted p-value (q)"""
    if q < 0.001: return "***"
    if q < 0.01:  return "**"
    if q < 0.05:  return "*"
    return ""

def generate_markdown_tables():
    # Read the knitted HTML file
    try:
        with open('step_5_regression.html', 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: 'step_5_regression.html' not found. Please ensure the file is in the exact same directory.")
        return

    # Clean HTML tags to make regex parsing easier
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)

    # 1. Extract all Estimates from the Fixed Effects tables
    # Looks for lines like: node_coverage -0.2681 0.6853 ...
    est_pattern = r"(node_coverage|weighted_node_coverage|edge_coverage|weighted_edge_coverage)\s+(-?\d+\.\d+)"
    estimates = [float(m[1]) for m in re.findall(est_pattern, text)]

    # 2. Extract all adjusted p-values (q-values) printed below each block
    # Looks for arrays like: [1] 1.000 1.000 0.857 1.000
    q_pattern = r"\[1\]\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)"
    q_values =[]
    for match in re.findall(q_pattern, text):
        q_values.extend([float(x) for x in match])

    # 3. Combine Estimate and Stars (e.g., "-0.268" or "*-1.405")
    formatted =[]
    for est, q in zip(estimates, q_values):
        formatted.append(f"{get_stars(q)}{est:.3f}")

    # 4. Group the metrics into chunks of 4 (Node, W_Node, Edge, W_Edge)
    # The R script ran exactly 88 models (22 groups of 4) in a strict order.
    c = [formatted[i:i+4] for i in range(0, len(formatted), 4)]

    if len(c) < 22:
        print("Warning: Parsed data does not contain enough data to build all tables. Output may be incomplete.")
        return

    # ================== BUILD MARKDOWN CONTENT ================== #

    markdown_content = f"""# Replicated Eye-Tracking Call Graph Analysis

### TABLE V: Call Graph Coverage and Summary Quality
| Graph | Study | Node Coverage | Weighted Node Coverage | Edge Coverage | Weighted Edge Coverage |
|-------|-------|---------------|------------------------|---------------|------------------------|
| Caller | Study 1 | {c[3][0]} | {c[3][1]} | {c[3][2]} | {c[3][3]} |
| | Study 2 | {c[9][0]} | {c[9][1]} | {c[9][2]} | {c[9][3]} |
| | Combined | {c[15][0]} | {c[15][1]} | {c[15][2]} | {c[15][3]} |
| Callee | Study 1 | {c[0][0]} | {c[0][1]} | {c[0][2]} | {c[0][3]} |
| | Study 2 | {c[6][0]} | {c[6][1]} | {c[6][2]} | {c[6][3]} |
| | Combined | {c[12][0]} | {c[12][1]} | {c[12][2]} | {c[12][3]} |

### TABLE VI: Callee Graph Coverage and Summary Quality Subscores
| Subscore | Node Coverage | Weighted Node Coverage | Edge Coverage | Weighted Edge Coverage |
|----------|---------------|------------------------|---------------|------------------------|
| Accuracy | {c[18][0]} | {c[18][1]} | {c[18][2]} | {c[18][3]} |
| Conciseness | {c[19][0]} | {c[19][1]} | {c[19][2]} | {c[19][3]} |
| Completeness | {c[20][0]} | {c[20][1]} | {c[20][2]} | {c[20][3]} |
| Clarity | {c[21][0]} | {c[21][1]} | {c[21][2]} | {c[21][3]} |

![Subscore Regression](subscore_reg.png)
*(Note: Make sure `subscore_reg.png` is in the same folder as this markdown file for the image to load properly).*

### TABLE VII: Call Graph Coverage and Confidence
| Graph | Study | Node Coverage | Weighted Node Coverage | Edge Coverage | Weighted Edge Coverage |
|-------|-------|---------------|------------------------|---------------|------------------------|
| Caller | Study 1 | {c[4][0]} | {c[4][1]} | {c[4][2]} | {c[4][3]} |
| | Study 2 | {c[10][0]} | {c[10][1]} | {c[10][2]} | {c[10][3]} |
| | Combined | {c[16][0]} | {c[16][1]} | {c[16][2]} | {c[16][3]} |
| Callee | Study 1 | {c[1][0]} | {c[1][1]} | {c[1][2]} | {c[1][3]} |
| | Study 2 | {c[7][0]} | {c[7][1]} | {c[7][2]} | {c[7][3]} |
| | Combined | {c[13][0]} | {c[13][1]} | {c[13][2]} | {c[13][3]} |

### TABLE VIII: Call Graph Coverage and Absolute Confidence Difference
| Graph | Study | Node Coverage | Weighted Node Coverage | Edge Coverage | Weighted Edge Coverage |
|-------|-------|---------------|------------------------|---------------|------------------------|
| Caller | Study 1 | {c[5][0]} | {c[5][1]} | {c[5][2]} | {c[5][3]} |
| | Study 2 | {c[11][0]} | {c[11][1]} | {c[11][2]} | {c[11][3]} |
| | Combined | {c[17][0]} | {c[17][1]} | {c[17][2]} | {c[17][3]} |
| Callee | Study 1 | {c[2][0]} | {c[2][1]} | {c[2][2]} | {c[2][3]} |
| | Study 2 | {c[8][0]} | {c[8][1]} | {c[8][2]} | {c[8][3]} |
| | Combined | {c[14][0]} | {c[14][1]} | {c[14][2]} | {c[14][3]} |
"""

    # Write the formatted string to a markdown file
    with open('replicated_tables.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("Success! The file 'replicated_tables.md' has been generated.")

if __name__ == "__main__":
    generate_markdown_tables()
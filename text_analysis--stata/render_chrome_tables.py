import os
import subprocess

html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #ffffff;
        display: inline-block;
        padding: 6px;
    }
    table {
        border-collapse: collapse;
        font-size: 13.5px;
        line-height: 1.15;
        color: #111827;
        background: #ffffff;
    }
    th {
        background-color: #007A33;
        color: #ffffff;
        font-weight: 700;
        padding: 8px 16px;
        text-align: center;
        border: none;
    }
    th.left {
        text-align: left;
        padding-left: 12px;
    }
    td {
        padding: 3px 16px;
        text-align: center;
        border: none;
    }
    td.left {
        text-align: left;
        font-weight: 500;
        color: #1f2937;
        padding-left: 12px;
        white-space: nowrap;
    }
    tr.se td {
        padding-top: 0px;
        padding-bottom: 4px;
        color: #6b7280;
        font-size: 12px;
    }
    tr.summary {
        background-color: #f9fafb;
    }
    tr.summary td {
        padding-top: 3.5px;
        padding-bottom: 3.5px;
    }
    tr.summary td.left {
        font-weight: 600;
    }
    tr.summary-border td {
        border-top: 1px solid #d1d5db;
    }
    tr.bottom-border td {
        border-bottom: 1.5px solid #007A33;
    }
    .note {
        padding-top: 8px;
        font-size: 11px;
        color: #6b7280;
        font-style: italic;
        text-align: left;
        padding-left: 12px;
    }
</style>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th class="left">Regressors</th>
                <th>(1)</th>
                <th>(2)</th>
                <th>(3)</th>
                <th>(4)</th>
                <th>(5)</th>
                <th>(6)</th>
            </tr>
        </thead>
        <tbody>
            __ROWS__
        </tbody>
    </table>
    <div class="note">__NOTE__</div>
</body>
</html>
"""

# Logit coefficients data (NO interactions)
rows_logit = [
    ("Coalition Proposal", ["1.101***", "0.597***", "0.701***", "0.680***", "0.721***", "0.734***"], False),
    ("", ["(0.110)", "(0.144)", "(0.196)", "(0.200)", "(0.206)", "(0.212)"], True),
    ("Commitment", ["1.119***", "0.746***", "0.421**", "0.476***", "0.524***", "0.536***"], False),
    ("", ["(0.123)", "(0.137)", "(0.177)", "(0.178)", "(0.183)", "(0.182)"], True),
    ("Payoff Reasoning", ["0.206", "-0.337", "-0.223", "-0.113", "-0.156", "-0.229"], False),
    ("", ["(0.198)", "(0.224)", "(0.270)", "(0.283)", "(0.286)", "(0.295)"], True),
    ("ln(Words + 1)", ["", "0.211***", "0.074", "0.002", "-0.030", "-0.040"], False),
    ("", ["", "(0.077)", "(0.211)", "(0.217)", "(0.218)", "(0.221)"], True),
    ("No. of Messages", ["", "0.080**", "0.090**", "0.098**", "0.101**", "0.105**"], False),
    ("", ["", "(0.032)", "(0.045)", "(0.044)", "(0.043)", "(0.043)"], True),
    ("Sentiment (std)", ["", "", "-0.157", "-0.115", "-0.127", "-0.141"], False),
    ("", ["", "", "(0.118)", "(0.119)", "(0.118)", "(0.122)"], True),
    ("Emotional Tone (std)", ["", "", "0.501***", "0.510***", "0.514***", "0.519***"], False),
    ("", ["", "", "(0.133)", "(0.135)", "(0.137)", "(0.139)"], True),
    ("Authenticity (std)", ["", "", "-0.213**", "-0.276**", "-0.271***", "-0.250**"], False),
    ("", ["", "", "(0.106)", "(0.108)", "(0.105)", "(0.106)"], True),
    ("Analytical Thinking (std)", ["", "", "-0.146", "-0.194*", "-0.178*", "-0.181*"], False),
    ("", ["", "", "(0.103)", "(0.105)", "(0.107)", "(0.110)"], True),
    ("Clout (std)", ["", "", "0.028", "0.029", "0.057", "0.046"], False),
    ("", ["", "", "(0.105)", "(0.105)", "(0.107)", "(0.113)"], True),
    ("Public Treatment", ["", "", "", "-0.010", "0.023", "0.020"], False),
    ("", ["", "", "", "(0.198)", "(0.202)", "(0.207)"], True),
    ("Slacker Treatment", ["", "", "", "-0.803***", "-0.848***", "-0.852***"], False),
    ("", ["", "", "", "(0.192)", "(0.198)", "(0.202)"], True),
]

summary_logit = [
    ("Session Fixed Effects", ["Yes", "Yes", "Yes", "Yes", "Yes", "Yes"]),
    ("Sender Traits", ["No", "No", "No", "No", "Yes", "Yes"]),
    ("Receiver Traits", ["No", "No", "No", "No", "No", "Yes"]),
    ("Observations", ["1,729", "1,729", "805", "805", "804", "803"]),
    ("Pseudo R²", ["0.078", "0.100", "0.054", "0.076", "0.089", "0.110"]),
    ("Log pseudolikelihood", ["-1,083.134", "-1,056.908", "-460.716", "-449.923", "-443.221", "-432.632"]),
    ("Clusters (Groups)", ["481", "481", "388", "388", "388", "388"]),
]

# AME data (NO interactions)
rows_ame = [
    ("Coalition Proposal", ["0.240***", "0.126***", "0.136***", "0.128***", "0.134***", "0.132***"], False),
    ("", ["(0.021)", "(0.030)", "(0.037)", "(0.037)", "(0.037)", "(0.037)"], True),
    ("Commitment", ["0.244***", "0.158***", "0.082**", "0.090***", "0.097***", "0.097***"], False),
    ("", ["(0.024)", "(0.028)", "(0.034)", "(0.033)", "(0.034)", "(0.032)"], True),
    ("Payoff Reasoning", ["0.045", "-0.071", "-0.043", "-0.021", "-0.029", "-0.041"], False),
    ("", ["(0.043)", "(0.047)", "(0.052)", "(0.053)", "(0.053)", "(0.053)"], True),
    ("ln(Words + 1)", ["", "0.045***", "0.014", "0.000", "-0.006", "-0.007"], False),
    ("", ["", "(0.016)", "(0.041)", "(0.041)", "(0.040)", "(0.040)"], True),
    ("No. of Messages", ["", "0.017**", "0.017**", "0.019**", "0.019**", "0.019**"], False),
    ("", ["", "(0.007)", "(0.009)", "(0.008)", "(0.008)", "(0.008)"], True),
    ("Sentiment (std)", ["", "", "-0.030", "-0.022", "-0.024", "-0.025"], False),
    ("", ["", "", "(0.023)", "(0.022)", "(0.022)", "(0.022)"], True),
    ("Emotional Tone (std)", ["", "", "0.097***", "0.096***", "0.095***", "0.094***"], False),
    ("", ["", "", "(0.025)", "(0.025)", "(0.025)", "(0.024)"], True),
    ("Authenticity (std)", ["", "", "-0.041**", "-0.052**", "-0.050***", "-0.045**"], False),
    ("", ["", "", "(0.020)", "(0.020)", "(0.019)", "(0.019)"], True),
    ("Analytical Thinking (std)", ["", "", "-0.028", "-0.037*", "-0.033*", "-0.033*"], False),
    ("", ["", "", "(0.020)", "(0.020)", "(0.020)", "(0.020)"], True),
    ("Clout (std)", ["", "", "0.005", "0.005", "0.011", "0.008"], False),
    ("", ["", "", "(0.020)", "(0.020)", "(0.020)", "(0.020)"], True),
    ("Public Treatment", ["", "", "", "-0.002", "0.004", "0.004"], False),
    ("", ["", "", "", "(0.037)", "(0.037)", "(0.037)"], True),
    ("Slacker Treatment", ["", "", "", "-0.151***", "-0.157***", "-0.154***"], False),
    ("", ["", "", "", "(0.036)", "(0.036)", "(0.035)"], True),
]

summary_ame = [
    ("Session Fixed Effects", ["Yes", "Yes", "Yes", "Yes", "Yes", "Yes"]),
    ("Sender Traits", ["No", "No", "No", "No", "Yes", "Yes"]),
    ("Receiver Traits", ["No", "No", "No", "No", "No", "Yes"]),
    ("Observations", ["1,729", "1,729", "805", "805", "804", "803"]),
    ("Clusters (Groups)", ["481", "481", "388", "388", "388", "388"]),
]

def build_html_rows(rows, summary):
    html_rows = []
    for var, vals, is_se in rows:
        cls = "se" if is_se else ""
        row_str = f'<tr class="{cls}"><td class="left">{var}</td>'
        for v in vals:
            row_str += f'<td>{v}</td>'
        row_str += '</tr>'
        html_rows.append(row_str)
    
    # Summary rows
    for i, (var, vals) in enumerate(summary):
        border_cls = "summary-border" if i == 0 else ""
        bottom_cls = "bottom-border" if i == len(summary) - 1 else ""
        row_str = f'<tr class="summary {border_cls} {bottom_cls}"><td class="left">{var}</td>'
        for v in vals:
            row_str += f'<td>{v}</td>'
        row_str += '</tr>'
        html_rows.append(row_str)
    
    return "\n".join(html_rows)

html_logit_content = html_template.replace("__ROWS__", build_html_rows(rows_logit, summary_logit)).replace("__NOTE__", "Logit coefficients with group-clustered standard errors in parentheses. * p&lt;0.10, ** p&lt;0.05, *** p&lt;0.01")
html_ame_content = html_template.replace("__ROWS__", build_html_rows(rows_ame, summary_ame)).replace("__NOTE__", "Average Marginal Effects (dy/dx) with group-clustered standard errors in parentheses. * p&lt;0.10, ** p&lt;0.05, *** p&lt;0.01")

html_logit_path = r"c:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_logit.html"
html_ame_path = r"c:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_ame.html"

with open(html_logit_path, "w", encoding="utf-8") as f:
    f.write(html_logit_content)

with open(html_ame_path, "w", encoding="utf-8") as f:
    f.write(html_ame_content)

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
pic_dir = r"c:\Users\Donat\communication_coalition_formation\text_analysis--stata\MPPT_Slide\pic"

# Render PNG via Headless Chrome with device-scale-factor=3 for 4K crisp resolution
out_logit_png = os.path.join(pic_dir, "tab_persuasion_logit_6models.png")
out_ame_png = os.path.join(pic_dir, "tab_persuasion_logit_ame_6models.png")

cmd_logit = [
    chrome_exe,
    "--headless",
    "--disable-gpu",
    "--force-device-scale-factor=3",
    "--hide-scrollbars",
    f"--screenshot={out_logit_png}",
    "--window-size=1000,1050",
    html_logit_path
]

cmd_ame = [
    chrome_exe,
    "--headless",
    "--disable-gpu",
    "--force-device-scale-factor=3",
    "--hide-scrollbars",
    f"--screenshot={out_ame_png}",
    "--window-size=1000,1000",
    html_ame_path
]

subprocess.run(cmd_logit, check=True)
subprocess.run(cmd_ame, check=True)
print("Rendered ultra-crisp unbroken tables via Chrome Headless!")

# Auto-crop white borders using PIL
from PIL import Image, ImageChops

def autocrop_image(img_path):
    img = Image.open(img_path).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        # Add small 4px padding
        w, h = img.size
        crop_box = (max(0, bbox[0]-4), max(0, bbox[1]-4), min(w, bbox[2]+4), min(h, bbox[3]+4))
        cropped = img.crop(crop_box)
        cropped.save(img_path, quality=98)
        print(f"Auto-cropped: {img_path} to size {cropped.size}")

autocrop_image(out_logit_png)
autocrop_image(out_ame_png)

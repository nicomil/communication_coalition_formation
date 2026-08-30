import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pic_dir = r"c:\Users\Donat\communication_coalition_formation\text_analysis--stata\MPPT_Slide\pic"
os.makedirs(pic_dir, exist_ok=True)

# 6-Model Logit Coefficients
data_6m_coef = [
    ["Coalition Proposal", "1.098***", "0.595***", "0.715***", "0.695***", "0.728***", "0.741***"],
    ["", "(0.109)", "(0.144)", "(0.195)", "(0.200)", "(0.206)", "(0.212)"],
    ["Commitment", "1.115***", "0.739***", "0.417**", "0.475***", "0.521***", "0.529***"],
    ["", "(0.123)", "(0.137)", "(0.177)", "(0.179)", "(0.184)", "(0.181)"],
    ["Payoff Reasoning", "0.201", "-0.339", "-0.220", "-0.106", "-0.154", "-0.229"],
    ["", "(0.198)", "(0.224)", "(0.268)", "(0.283)", "(0.286)", "(0.296)"],
    ["ln(Words + 1)", "", "0.214***", "0.071", "-0.003", "-0.033", "-0.045"],
    ["", "", "(0.077)", "(0.211)", "(0.217)", "(0.218)", "(0.220)"],
    ["No. of Messages", "", "0.077**", "0.083*", "0.092**", "0.094**", "0.100**"],
    ["", "", "(0.031)", "(0.044)", "(0.043)", "(0.042)", "(0.043)"],
    ["Sentiment (std)", "", "", "-0.149", "-0.107", "-0.121", "-0.136"],
    ["", "", "", "(0.118)", "(0.119)", "(0.118)", "(0.122)"],
    ["Emotional Tone (std)", "", "", "0.495***", "0.506***", "0.510***", "0.513***"],
    ["", "", "", "(0.133)", "(0.135)", "(0.137)", "(0.138)"],
    ["Authenticity (std)", "", "", "-0.232**", "-0.297***", "-0.289***", "-0.266**"],
    ["", "", "", "(0.104)", "(0.107)", "(0.105)", "(0.106)"],
    ["Analytical Thinking (std)", "", "", "-0.147", "-0.197*", "-0.180*", "-0.182"],
    ["", "", "", "(0.104)", "(0.106)", "(0.108)", "(0.111)"],
    ["Clout (std)", "", "", "0.017", "0.019", "0.052", "0.042"],
    ["", "", "", "(0.106)", "(0.106)", "(0.109)", "(0.113)"],
    ["Public Treatment", "", "", "", "0.023", "0.054", "0.048"],
    ["", "", "", "", "(0.198)", "(0.203)", "(0.209)"],
    ["Slacker Treatment", "", "", "", "-0.801***", "-0.847***", "-0.854***"],
    ["", "", "", "", "(0.193)", "(0.200)", "(0.203)"],
    ["Sender Traits", "No", "No", "No", "No", "Yes", "Yes"],
    ["Receiver Traits", "No", "No", "No", "No", "No", "Yes"],
    ["Observations", "1,729", "1,729", "805", "805", "804", "803"],
    ["Pseudo R²", "0.077", "0.099", "0.049", "0.073", "0.086", "0.108"],
    ["Clusters (Groups)", "481", "481", "388", "388", "388", "388"]
]

# 6-Model AME (dy/dx)
data_6m_ame = [
    ["Coalition Proposal", "0.240***", "0.112***", "0.134***", "0.131***", "0.132***", "0.134***"],
    ["", "(0.020)", "(0.026)", "(0.036)", "(0.037)", "(0.037)", "(0.037)"],
    ["Commitment", "0.244***", "0.139***", "0.078**", "0.090***", "0.095***", "0.096***"],
    ["", "(0.024)", "(0.024)", "(0.033)", "(0.033)", "(0.033)", "(0.032)"],
    ["Payoff Reasoning", "0.044", "-0.064", "-0.041", "-0.020", "-0.028", "-0.041"],
    ["", "(0.043)", "(0.042)", "(0.050)", "(0.054)", "(0.052)", "(0.054)"],
    ["ln(Words + 1)", "", "0.040***", "0.013", "-0.001", "-0.006", "-0.008"],
    ["", "", "(0.015)", "(0.040)", "(0.041)", "(0.039)", "(0.040)"],
    ["No. of Messages", "", "0.014**", "0.016*", "0.017**", "0.017**", "0.018**"],
    ["", "", "(0.006)", "(0.008)", "(0.008)", "(0.008)", "(0.008)"],
    ["Sentiment (std)", "", "", "-0.028", "-0.020", "-0.022", "-0.025"],
    ["", "", "", "(0.022)", "(0.022)", "(0.021)", "(0.022)"],
    ["Emotional Tone (std)", "", "", "0.093***", "0.096***", "0.093***", "0.093***"],
    ["", "", "", "(0.025)", "(0.025)", "(0.024)", "(0.024)"],
    ["Authenticity (std)", "", "", "-0.044**", "-0.056***", "-0.053***", "-0.048**"],
    ["", "", "", "(0.020)", "(0.020)", "(0.019)", "(0.019)"],
    ["Analytical Thinking (std)", "", "", "-0.028", "-0.037*", "-0.033", "-0.033"],
    ["", "", "", "(0.020)", "(0.020)", "(0.020)", "(0.020)"],
    ["Clout (std)", "", "", "0.003", "0.004", "0.009", "0.008"],
    ["", "", "", "(0.020)", "(0.020)", "(0.020)", "(0.021)"],
    ["Public Treatment", "", "", "", "0.004", "0.010", "0.009"],
    ["", "", "", "", "(0.037)", "(0.037)", "(0.038)"],
    ["Slacker Treatment", "", "", "", "-0.152***", "-0.154***", "-0.155***"],
    ["", "", "", "", "(0.036)", "(0.036)", "(0.036)"],
    ["Sender Traits", "No", "No", "No", "No", "Yes", "Yes"],
    ["Receiver Traits", "No", "No", "No", "No", "No", "Yes"],
    ["Observations", "1,729", "1,729", "805", "805", "804", "803"],
    ["Clusters (Groups)", "481", "481", "388", "388", "388", "388"]
]

headers_6m = ["Regressors", "(1)", "(2)", "(3)", "(4)", "(5)", "(6)"]

def render_flawless_table(data, col_headers, out_name, col_widths, note_text):
    # Total rows including header and note row
    n_data_rows = len(data)
    n_cols = len(col_headers)
    
    # Calculate tight figure height based on rows
    row_height = 0.28 # inches per row
    fig_height = (n_data_rows + 3) * row_height
    fig_width = 12.0
    
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]) # full canvas, zero padding
    ax.axis('off')
    
    tbl = ax.table(
        cellText=data,
        colLabels=col_headers,
        loc='center',
        colWidths=col_widths,
        cellLoc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 1.30)
    
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_linewidth(0)
        
        # Header formatting
        if r == 0:
            cell.set_facecolor('#007A33') # Tor Vergata green
            cell.set_text_props(weight='bold', color='white', ha='left' if c==0 else 'center')
            cell.set_edgecolor('#007A33')
            cell.set_linewidth(1.0)
        else:
            cell.set_facecolor('#FFFFFF')
            if c == 0:
                cell.set_text_props(ha='left', weight='medium')
            else:
                cell.set_text_props(ha='center')
            
            # Standard error rows
            if r > 0 and r % 2 == 0 and r <= 24:
                cell.set_text_props(color='#555555', size=9)
            
            # Summary / bottom statistics rows
            if r > n_data_rows - 5:
                cell.set_facecolor('#F4F6F4')
                if c == 0:
                    cell.set_text_props(weight='bold', color='#111111')
                else:
                    cell.set_text_props(color='#111111')
    
    # Add note as a bottom cell spanning all columns
    note_cell = tbl.add_cell(n_data_rows + 1, 0, width=sum(col_widths), height=0.035, text=note_text, loc='left')
    note_cell.set_facecolor('#FFFFFF')
    note_cell.set_edgecolor('white')
    note_cell.set_text_props(fontsize=8.5, color='#555555', style='italic', ha='left')
    
    png_path = os.path.join(pic_dir, f"{out_name}.png")
    pdf_path = os.path.join(pic_dir, f"{out_name}.pdf")
    
    plt.savefig(png_path, dpi=300, bbox_inches='tight', pad_inches=0.01, facecolor='white')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', pad_inches=0.01, facecolor='white')
    plt.close()
    print(f"Flawlessly rendered: {png_path}")

render_flawless_table(
    data_6m_coef, headers_6m,
    "tab_persuasion_logit_6models",
    [0.34, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11],
    "Logit coefficients with group-clustered standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01"
)

render_flawless_table(
    data_6m_ame, headers_6m,
    "tab_persuasion_logit_ame_6models",
    [0.34, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11],
    "Average Marginal Effects (dy/dx) with group-clustered standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01"
)

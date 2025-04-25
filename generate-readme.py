import os
#files = [f for  f in os.listdir("examples") if f.endswith(".ipynb")]
#files.sort()
#files
with open("examples/worksheets.txt","r") as f:
    lines = f.readlines()
s = ""
s+= """# worksheets-ode-2025
Worksheets Gewöhnliche Differentialgleichungen SS 2025

## Worksheets
Man beachte, dass Kaggle und Gradient nur funktionieren, wenn man dort eingeloggt ist, da sonst das Notebook nicht auf das Internet zugreifen kann.

<table>
"""
for l in lines:
    (filename,title) = l.strip().split(",")
    s+= '<tr>\n'
    s+= '  <td>\n'
    s+=f'    <a href="/JeremiasE/worksheets-ode-2023/blob/main/examples/{filename}">{title}</a>\n'
    s+= '  </td>\n'
    s+= '  <td>\n'
    s+=f'    <a href="https://mybinder.org/v2/gh/JeremiasE/worksheets-ode-2025/HEAD?labpath=examples%2F{filename}" rel="nofollow">\n'
    s+= '      <img src="https://mybinder.org/badge_logo.svg" alt="Open In MyBinder "   height="22ex">\n'
    s+= '    </a>\n'
    s+= '  </td>\n'
    s+= '  <td>\n'
    s+=f'    <a href="https://colab.research.google.com/github/JeremiasE/worksheets-ode-2025/blob/main/examples/{filename}" rel="nofollow">\n'
    s+='      <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" height="22ex">\n'
    s+= '    </a>\n'
    s+= '  </td>\n'
    s+= '  <td>\n'
    s+= f'   <a href="https://console.paperspace.com/github/JeremiasE/worksheets-ode-2025/blob/main/examples/{filename}">\n'
    s+= '      <img src="https://assets.paperspace.io/img/gradient-badge.svg" alt="Run on Gradient"/>\n'
    s+= '    </a>\n'
    s+= '  </td>\n'
    s+= '  <td>\n'
    s+=f'    <a href="https://kaggle.com/kernels/welcome?src=https://github.com/JeremiasE/worksheets-ode-2025/blob/main/examples/{filename}" rel="nofollow">\n'
    s+='      <img src="https://kaggle.com/static/images/open-in-kaggle.svg" alt="Open in Kaggle" height="22ex">\n'
    s+= '    </a>\n'
    s+= '  </td>\n'
    s+= '</tr>\n'
s+="""</table>
"""
print(s)

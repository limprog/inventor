import sqlite3
import os
from io import BytesIO, StringIO
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jinja2
import pdfkit

def report():
    plt.close('all')
    conn = sqlite3.connect(os.path.join('database/data.db'))
    products = pd.read_sql_query("SELECT * FROM products", conn)
    storage_pd = pd.read_sql_query("SELECT * FROM storage", conn)
    conn.close()
    product_pies = []
    storage_pies = []
    for type in products.type.unique():
        type_products = products[products['type']==type]
        plt.pie(type_products["count"], labels=type_products["storage"])
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)  # rewind to beginning of file
        figdata_png = base64.b64encode(figfile.getvalue()).decode('utf8')
        product_pies.append([type, figdata_png])
        plt.clf()
    for storage in products.storage.unique():
        storage_products = products[products["storage"] == storage]
        # storage_products["percent"] = (storage_products["count"] * 100) / storage_products["count"].sum()
        plt.pie(storage_products["count"], labels=storage_products["type"])
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)  # rewind to beginning of file
        figdata_png = base64.b64encode(figfile.getvalue()).decode('utf8')
        storage_pies.append([storage, figdata_png])
        plt.clf()
    storage_pd["fullness"] = 100-storage_pd["сapacity"]*100/storage_pd["сapacity2"]
    sns.barplot(data=storage_pd, x="name", y="fullness")
    figfile = BytesIO()
    sns.set(style="darkgrid")
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    storage_png = base64.b64encode(figfile.getvalue()).decode('utf8')
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("templates/report.html")
    output_text = template.render(product_pies=product_pies,
                                  storage_pies=storage_pies,
                                  storage_png=storage_png)
    html_file = StringIO(output_text)
    # html_file = open("temp_test/test1.html", 'w')
    # html_file.write(output_text)
    # html_file.close()
    options = {
        'page-size': 'Letter',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    pdfkit.from_file(html_file, "temp/report.pdf", options=options)
    return 200


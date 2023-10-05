# Modified from https://pypi.org/project/pretty-html-table/
def build_table(
        df,
        change_color=False,
        font_size='medium', 
        font_family='Arial', 
        text_align='left', 
        width='auto', 
        index=False, 
        odd_bg_color=None,
        border_bottom_color=None,
        escape=True,
        padding="5px 20px 5px 5px",
        float_format=None
    ):

    # Set color
    color, border_bottom, odd_background_color, header_background_color = '#FFFFFF', '2px solid #305496', '#D9E1F2', '#305496'

    if odd_bg_color:
        odd_background_color = odd_bg_color

    if border_bottom_color:
        border_bottom = border_bottom_color 

    df_html_output = df.iloc[[0]].to_html(
        na_rep="", 
        index=index, 
        border=0, 
        escape=escape, 
        float_format=float_format,
    )
    # change format of header
    if index:
        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + header_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';color: ' + color
                                                + ';text-align: ' + text_align
                                                + ';border-bottom: ' + border_bottom
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">', len(df.columns)+1)

        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + odd_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';text-align: ' + text_align
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

    else:
        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + header_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';color: ' + color
                                                + ';text-align: ' + text_align
                                                + ';border-bottom: ' + border_bottom
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

    #change format of table
    df_html_output = df_html_output.replace('<td>'
                                            ,'<td style = "background-color: ' + odd_background_color
                                            + ';font-family: ' + font_family
                                            + ';font-size: ' + str(font_size)
                                            + ';text-align: ' + text_align
                                            + ';padding: ' + padding
                                            + ';width: ' + str(width) + '">')
    body = """<p>""" + format(df_html_output)

    a = 1
    while a != len(df):
        df_html_output = df.iloc[[a]].to_html(na_rep = "", index = index, header = False, escape=escape)
            
        # change format of index
        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + odd_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';text-align: ' + text_align
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

        #change format of table
        df_html_output = df_html_output.replace('<td>'
                                                ,'<td style = "background-color: ' + odd_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';text-align: ' + text_align
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

        body = body + format(df_html_output)
        a += 1

    body = body + """</p>"""

    body = body.replace("""</td>
    </tr>
  </tbody>
</table>
            <table border="1" class="dataframe">
  <tbody>
    <tr>""","""</td>
    </tr>
    <tr>""").replace("""</td>
    </tr>
  </tbody>
</table><table border="1" class="dataframe">
  <tbody>
    <tr>""","""</td>
    </tr>
    <tr>""")

    # Change color for detailed attendance table
    if change_color:
        body = body.replace(r"\n'", "").split("<tr>")
        body_res = []
        for item in body:
            if "Absent" in item or "Vắng" in item:
                body_res.append(item.replace("#D9E1F2", "#FAA0A0"))
            elif "On time" in item or "Đúng giờ" in item:
                body_res.append(item.replace("#D9E1F2", "#DAF7A6"))
            elif "Late" in item or "Muộn" in item:
                body_res.append(item.replace("#D9E1F2", "#FFE4B5"))
            else:
                body_res.append(item)
        return "<tr>".join(body_res)
    
    return body.replace(r"\n'", "")
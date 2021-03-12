import os
import pandas as pd

base_project_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def make_table(df, total_levels):
    html_tables = {}
    for level in reversed(range(total_levels)):
        html_text = ''
        for section, sub_df in df.groupby(level=level - 1):
            # Remove specific test text from DocText for a header
            title_text_list = sub_df['DocText'].iloc[0].split(":")[0:-1]
            title_text = ':'.join(title_text_list) if \
                len(title_text_list) > 0 else \
                sub_df['DocText'].iloc[0]
            html_text += '<h4>' + title_text + "</h4>"
            sub_df = sub_df.unstack(level=-1).reset_index(drop=True).stack()
            # Retrieve specific function text
            sub_df['DocTextParse'] = sub_df["DocText"].str.extract('.*:(.*)$')
            sub_df['DocText'] = sub_df[['FileName', 'FunctionName', 'DocTextParse']]\
                .apply(lambda x: x[2] if not pd.isnull(x[2]) else ' - '.join([x[0], x[1]]), axis=1)
            # format
            sub_df.drop(['DocTextParse', 'FileName', 'FunctionName'], axis=1, inplace=True)
            sub_df.rename(columns={
                "DocText": "Test",
                "TimeStamp": "Last Check",
                "FunctionStatus": "Status"
            }, inplace=True)
            html_text += sub_df.to_html(index=False) + '\n'
            df = df.drop(section, level=level - 1)
            html_tables[section] = html_text
    return html_tables


def main():
    df = pd.read_csv(
        os.path.join(base_project_path, "logs", "test.log"),
        header=None,
        names=["TimeStamp", "DocText", "FileName", "FunctionName", "FunctionStatus"])
    # Get latest function return
    df = df\
        .sort_values(['TimeStamp'], ascending=True)\
        .groupby(['DocText', 'FileName', 'FunctionName'])\
        .last()\
        .reset_index()
    section_split_df = df['DocText'].str.split(':', expand=True)
    df = pd.concat([df, section_split_df], axis=1)
    # section split columns are ascending integers
    df = df.set_index(section_split_df.columns.tolist())
    html_text = make_table(df, total_levels=len(section_split_df.columns.tolist()))
    sections = sorted([i for i in html_text.keys()])
    # Push the general section to the top
    if "General" in sections:
        sections.remove("General")
    sections.insert(0, "General")
    # create html file and save to docs static folder.
    with open(os.path.join(base_project_path, "docs", "_static", "testing_output.html"), 'w') as f:
        f.write("""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Test Status</title>
        """)
        with open(os.path.join(base_project_path, "docs", "_static", "testing_notes.html"), 'r') as f2:
            notes_data = f2.read()
        f.write(notes_data)
        for section in sections:
            if section in html_text.keys():
                f.write(html_text[section])
        f.write("""
            </head>
            <body>
        """)
    return


if __name__ == "__main__":
    main()

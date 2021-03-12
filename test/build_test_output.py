import os
import pandas as pd

base_project_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def make_table(df, total_levels):
    html_tables = {}
    df[['DocSection', 'DocText']] = df["DocText"].str.rsplit(":", 1, expand=True)
    for section, sub_df in df.groupby(['DocSection']):
        sub_df.drop(['DocSection'], axis=1, inplace=True)
        html_text = ''
        html_text += '<h4>' + section.replace(":", " : ") + "</h4>"
        sub_df.rename(columns={
            "DocText": "Test",
            "TimeStamp": "Last Check",
            "FunctionStatus": "Status"
        }, inplace=True)
        html_text += sub_df.to_html(index=False) + '\n'
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
    # df = pd.concat([df, section_split_df], axis=1)
    # section split columns are ascending integers
    # df = df.set_index(section_split_df.columns.tolist())
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

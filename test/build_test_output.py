import os
from pprint import pprint
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
        for section, sub_df in df.groupby(level=level):
            title_text_list = sub_df['DocText'].iloc[0].split(":")[0:-1]
            title_text = ':'.join(title_text_list) if len(title_text_list) > 0 else sub_df['DocText'].iloc[0]
            html_text += '<h4>' + title_text + "</h4>" + '\n'
            sub_df = sub_df.unstack(level=-1).reset_index(drop=True).stack()
            sub_df['DocTextParse'] = sub_df["DocText"].str.extract('.*:(.*)$')
            sub_df['DocText'] = sub_df[['DocText', 'DocTextParse']]\
                .apply(lambda x: x[1] if not pd.isnull(x[1]) else x[0], axis=1)
            sub_df.drop(['DocTextParse'], axis=1, inplace=True)
            html_text += sub_df.to_html(index=False) + '\n'
            df = df.drop(section, level=level)
            html_tables[section] = html_text
    return html_tables


def main():
    df = pd.read_csv(os.path.join(base_project_path, "logs", "test.log"))
    # Get latest function return
    df = df\
        .sort_values(['TimeStamp'], ascending=True)\
        .groupby(['DocText', 'FileName', 'FunctionName'])\
        .last()\
        .reset_index()
    df = pd.concat([df, df['DocText'].str.split(':', expand=True)], axis=1)
    section_levels = df.shape[1] - 4
    print(section_levels)
    df = df.set_index([0,1,2])
    # sys.exit()
    pprint(df, width=150)
    html_text = make_table(df, total_levels=3)
    sections = sorted([i for i in html_text.keys()])
    with open(os.path.join(base_project_path, "docs", "_static", "testing_output.html"), 'w') as f:
        for section in sections:
            f.write(html_text[section])
    return


if __name__ == "__main__":
    main()
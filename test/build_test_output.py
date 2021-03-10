import os
import pandas as pd

base_project_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def main():
    with open(os.path.join(base_project_path, "logs", "test.log"), 'r') as f:
        data = f.read()
    df = pd.read_csv(data)
    print(df)
    return


if __name__ == "__main__":
    main()
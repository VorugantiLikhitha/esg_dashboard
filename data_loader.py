import pandas as pd
import glob
import os

def load_emissions_data():
    all_files = glob.glob('data/ghgp_data_20[0-9][0-9].xlsx')
    all_files = sorted(all_files)
    print(f"Found {len(all_files)} files...")
    dfs = []

    for file in all_files:
        year = int(os.path.basename(file).split('_')[2].split('.')[0])
        print(f"Loading {year}...")

        sheet_names_to_try = [
            'Direct Point Emitters',
            'Direct Emitters',
            'Point Emitters'
        ]

        df = None
        for sheet_name in sheet_names_to_try:
            try:
                df = pd.read_excel(file, sheet_name=sheet_name, header=3)
                break
            except:
                continue

        if df is None:
            xl = pd.ExcelFile(file)
            print(f"  Sheets in {year}: {xl.sheet_names}")
            df = pd.read_excel(file, sheet_name=xl.sheet_names[0], header=3)

        cols_needed = {
            'Facility Id': 'facility_id',
            'Facility Name': 'facility_name',
            'City': 'city',
            'State': 'state',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Industry Type (sectors)': 'industry_sector',
            'Total reported direct emissions': 'total_emissions',
            'CO2 emissions (non-biogenic) ': 'co2_emissions',
            'Methane (CH4) emissions ': 'ch4_emissions',
            'Nitrous Oxide (N2O) emissions ': 'n2o_emissions',
        }

        available = {k: v for k, v in cols_needed.items() if k in df.columns}
        df_clean = df[list(available.keys())].copy()
        df_clean.columns = list(available.values())
        df_clean['year'] = year

        numeric_cols = ['total_emissions', 'co2_emissions',
                        'ch4_emissions', 'n2o_emissions']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        df_clean = df_clean.dropna(subset=['total_emissions'])
        dfs.append(df_clean)

    df_all = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal records: {len(df_all)}")
    print(f"Years: {sorted(df_all['year'].unique())}")
    return df_all


def load_trends_data():
    df = pd.read_excel(
        'data/ghgp_data_by_year_2023.xlsx',
        sheet_name='Direct Point Emitters',
        header=3
    )
    year_cols = [col for col in df.columns if 'Total reported' in str(col)]
    keep_cols = ['Facility Name', 'State',
                 'Latest Reported Industry Type (sectors)'] + year_cols
    df_trends = df[keep_cols].copy()
    df_trends.columns = (['facility_name', 'state', 'industry_sector'] +
                         [str(col)[:4] for col in year_cols])
    return df_trends


def get_summary_stats(df):
    return {
        'total_facilities': df['facility_id'].nunique(),
        'total_emissions': df['total_emissions'].sum(),
        'top_state': df.groupby('state')['total_emissions'].sum().idxmax(),
        'top_industry': df.groupby('industry_sector')['total_emissions'].sum().idxmax(),
        'avg_emissions': df['total_emissions'].mean(),
        'years_covered': sorted(df['year'].unique().tolist())
    }
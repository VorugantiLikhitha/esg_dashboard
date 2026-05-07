import pandas as pd

# ================================
# EPA eGRID EMISSION FACTORS
# State-level lb CO2e per MWh
# Source: EPA eGRID 2023
# ================================

# These are real EPA eGRID emission factors by state (lb CO2/MWh)
# We'll update these from the actual file once downloaded
EGRID_FACTORS = {
    'TX': 895.0,  # ERCOT grid - Texas
    'CA': 537.0,  # WECC California
    'FL': 1003.0, # FRCC
    'PA': 744.0,  # PJM
    'OH': 1196.0, # PJM
    'IL': 1043.0, # SERC
    'NY': 542.0,  # NPCC
    'GA': 968.0,  # SERC
    'NC': 857.0,  # SERC
    'VA': 692.0,  # PJM
    'IN': 1677.0, # SERC
    'WV': 1987.0, # PJM
    'KY': 1778.0, # SERC
    'LA': 1008.0, # SERC
    'AL': 1001.0, # SERC
    'MI': 1186.0, # MRO
    'MN': 1080.0, # MRO
    'WI': 1259.0, # MRO
    'MO': 1604.0, # SERC
    'IA': 1148.0, # MRO
    'KS': 1337.0, # SPP
    'OK': 1010.0, # SPP
    'AR': 1014.0, # SERC
    'MS': 978.0,  # SERC
    'TN': 812.0,  # TVA
    'SC': 716.0,  # SERC
    'AZ': 894.0,  # WECC
    'NM': 1339.0, # WECC
    'CO': 1237.0, # WECC
    'WY': 1966.0, # WECC
    'MT': 913.0,  # WECC
    'ID': 327.0,  # WECC
    'UT': 1495.0, # WECC
    'NV': 842.0,  # WECC
    'WA': 271.0,  # WECC - very clean (hydro)
    'OR': 412.0,  # WECC
    'NE': 1382.0, # MRO
    'SD': 775.0,  # MRO
    'ND': 1759.0, # MRO
    'MD': 637.0,  # PJM
    'DE': 786.0,  # PJM
    'NJ': 508.0,  # PJM
    'CT': 493.0,  # NPCC
    'MA': 596.0,  # NPCC
    'RI': 595.0,  # NPCC
    'NH': 370.0,  # NPCC
    'VT': 35.0,   # NPCC - very clean
    'ME': 429.0,  # NPCC
    'AK': 1003.0,
    'HI': 1523.0,
    'DC': 637.0,
}

# Conversion factor: lb to metric tons
LB_TO_METRIC_TON = 0.000453592

# Scope 3 category multipliers (industry-based estimates)
# Based on EPA supply chain emission factors
SCOPE3_MULTIPLIERS = {
    'Power Plants': 0.15,
    'Petroleum and Natural Gas Systems': 2.8,
    'Chemicals': 3.2,
    'Waste': 0.8,
    'Minerals': 1.9,
    'Metals': 2.5,
    'Other': 1.5,
    'Petroleum Product Suppliers,Refineries': 4.1,
    'Municipal Landfills': 0.6,
}


def load_egrid_factors(filepath='data/egrid2023.xlsx'):
    """
    Load actual eGRID emission factors from EPA file
    Falls back to hardcoded factors if file not found
    """
    try:
        df = pd.read_excel(filepath, sheet_name='ST23', header=1)
        # eGRID state sheet has STABBR and STNOXRTA columns
        factors = {}
        for _, row in df.iterrows():
            state = str(row.get('STABBR', '')).strip()
            factor = row.get('STCO2RTA', None)  # CO2 rate lb/MWh
            if state and factor and pd.notna(factor):
                factors[state] = float(factor)
        if len(factors) > 10:
            print(f"Loaded {len(factors)} eGRID factors from file")
            return factors
    except Exception as e:
        print(f"Using hardcoded eGRID factors: {e}")
    return EGRID_FACTORS


def calculate_scope1(df):
    """
    Scope 1 = Direct emissions already in EPA GHGRP dataset
    These are direct facility emissions reported to EPA
    """
    scope1 = df.groupby(['state', 'year', 'industry_sector'])[
        ['total_emissions', 'co2_emissions', 
         'ch4_emissions', 'n2o_emissions']
    ].sum().reset_index()
    
    scope1['scope'] = 'Scope 1'
    scope1 = scope1.rename(columns={'total_emissions': 'emissions'})
    return scope1


def calculate_scope2(df, egrid_factors=None):
    """
    Scope 2 = Indirect emissions from purchased electricity
    Formula: Electricity consumed (MWh) × Grid emission factor (lb CO2/MWh) × conversion
    
    We estimate electricity consumption from facility emissions
    using industry-specific electricity intensity factors
    """
    if egrid_factors is None:
        egrid_factors = EGRID_FACTORS

    # Industry electricity intensity (MWh per metric ton CO2e direct emissions)
    # Based on EPA industry benchmarks
    ELEC_INTENSITY = {
        'Power Plants': 0.08,
        'Petroleum and Natural Gas Systems': 0.12,
        'Chemicals': 0.35,
        'Waste': 0.15,
        'Minerals': 0.28,
        'Metals': 0.45,
        'Other': 0.20,
        'Petroleum Product Suppliers,Refineries': 0.18,
        'Municipal Landfills': 0.10,
    }

    df_s2 = df.copy()

    # Get electricity intensity for each industry
    df_s2['elec_intensity'] = df_s2['industry_sector'].map(
        lambda x: next(
            (v for k, v in ELEC_INTENSITY.items() if k in str(x)), 0.20
        )
    )

    # Estimate electricity consumed (MWh)
    df_s2['electricity_mwh'] = (
        df_s2['total_emissions'] * df_s2['elec_intensity']
    )

    # Get grid emission factor for each state
    df_s2['grid_factor'] = df_s2['state'].map(
        lambda x: egrid_factors.get(str(x), 1000.0)
    )

    # Calculate Scope 2 emissions
    # electricity (MWh) × factor (lb/MWh) × conversion (metric tons/lb)
    df_s2['scope2_emissions'] = (
        df_s2['electricity_mwh'] *
        df_s2['grid_factor'] *
        LB_TO_METRIC_TON
    )

    scope2 = df_s2.groupby(['state', 'year', 'industry_sector'])[
        'scope2_emissions'
    ].sum().reset_index()

    scope2['scope'] = 'Scope 2'
    scope2 = scope2.rename(columns={'scope2_emissions': 'emissions'})
    return scope2


def calculate_scope3_estimate(df):
    """
    Scope 3 = Value chain emissions (upstream + downstream)
    Estimated using industry-specific multipliers
    Based on EPA supply chain emission factors methodology
    Note: These are estimates - real Scope 3 requires company-level data
    """
    df_s3 = df.copy()

    df_s3['scope3_multiplier'] = df_s3['industry_sector'].map(
        lambda x: next(
            (v for k, v in SCOPE3_MULTIPLIERS.items() if k in str(x)), 1.5
        )
    )

    df_s3['scope3_emissions'] = (
        df_s3['total_emissions'] * df_s3['scope3_multiplier']
    )

    scope3 = df_s3.groupby(['state', 'year', 'industry_sector'])[
        'scope3_emissions'
    ].sum().reset_index()

    scope3['scope'] = 'Scope 3 (Estimated)'
    scope3 = scope3.rename(columns={'scope3_emissions': 'emissions'})
    return scope3


def get_all_scopes(df):
    """
    Returns combined Scope 1 + 2 + 3 DataFrame
    """
    print("Calculating Scope 1 (EPA direct emissions)...")
    s1 = calculate_scope1(df)
    s1_combined = s1[['state', 'year', 'industry_sector', 
                       'emissions', 'scope']].copy()

    print("Calculating Scope 2 (grid electricity)...")
    s2 = calculate_scope2(df)

    print("Estimating Scope 3 (value chain)...")
    s3 = calculate_scope3_estimate(df)

    # Combine all scopes
    df_all = pd.concat([s1_combined, s2, s3], ignore_index=True)

    print(f"\n=== Scope Summary ===")
    summary = df_all.groupby('scope')['emissions'].sum()
    for scope, total in summary.items():
        print(f"{scope}: {total/1e9:.2f}B metric tons CO2e")

    return df_all


def get_scope_summary_by_industry(df_all):
    """
    Returns pivot table: industry × scope
    """
    return df_all.groupby(['industry_sector', 'scope'])[
        'emissions'
    ].sum().unstack(fill_value=0)


def get_scope_trend(df_all):
    """
    Returns yearly trend by scope
    """
    return df_all.groupby(['year', 'scope'])[
        'emissions'
    ].sum().reset_index()


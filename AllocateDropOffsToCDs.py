import pandas as pd


nyc_cd_stats_df = pd.read_csv('static/CommunityDistrictProfilePopulationStats.csv')

# Choose Allocation Method
population_per_allocation = False
total_sites = 170

# Calculate total population reported on Community District Profiles.
# Note that it adds up to 9.3 million, which is an overestimate.
total_nyc_population = sum(pop for pop in list(nyc_cd_stats_df['pop_estimate_acs']))
normalized_nyc_population = 8600000
nyc_cd_stats_df['pop_nrml'] = (nyc_cd_stats_df['pop_estimate_acs'] * (normalized_nyc_population / total_nyc_population))


if population_per_allocation:
    nyc_cd_stats_df['DropOffAllocation'] = round(nyc_cd_stats_df['pop_nrml'] / population_per_allocation)
    nyc_cd_stats_df['pop_per_drop'] = nyc_cd_stats_df['pop_nrml'] / nyc_cd_stats_df['DropOffAllocation']

else:
    nyc_cd_stats_df['DropOffAllocation'] = round(total_sites*(nyc_cd_stats_df['pop_nrml']/normalized_nyc_population))
    nyc_cd_stats_df['pop_per_drop'] = nyc_cd_stats_df['pop_nrml'] / nyc_cd_stats_df['DropOffAllocation']

    if total_sites < int(sum(nyc_cd_stats_df['DropOffAllocation'])):
        nyc_cd_stats_df = nyc_cd_stats_df.sort_values(['pop_per_drop'], ascending=True).reset_index()
        diff = int(sum(nyc_cd_stats_df['DropOffAllocation'])) - total_sites
        for i in range(diff):
            nyc_cd_stats_df.loc[i, 'DropOffAllocation'] -= 1
    elif total_sites > int(sum(nyc_cd_stats_df['DropOffAllocation'])):
        nyc_cd_stats_df = nyc_cd_stats_df.sort_values(['pop_per_drop'], ascending=False).reset_index()
        diff = total_sites - int(sum(nyc_cd_stats_df['DropOffAllocation']))
        for i in range(diff):
            nyc_cd_stats_df.loc[i, 'DropOffAllocation'] += 1
    nyc_cd_stats_df['pop_per_drop'] = nyc_cd_stats_df['pop_nrml'] / nyc_cd_stats_df['DropOffAllocation']

print(nyc_cd_stats_df)
print("Total FSDOs allocated:", nyc_cd_stats_df['DropOffAllocation'].sum())

nyc_cd_stats_df.to_csv('static/CommunityDistrictProfilePopulationStats.csv')

# Vietnam Weather Data Analysis

## Objectives of this analysis
This article aims to answer the following questions:

- What are the overall characteristics of weather in Vietnam?
- Are the regions very different from one another?
- How do the differences appear across **regions**, **time**, and **terrain**?
- Which forms of extreme weather stand out?
- How does weather variability differ by region, and what about dual-risk days?
# 1. Understand the dataset before analyzing

### What does this dataset contain?
- **Each row** is weather data for **one location on one day**
- **Each column** is one attribute, for example: temperature, rainfall, humidity, UV index, wind, region, terrain...

### What needs to be done
Before analyzing, we should always:
1. Load the data into Python
2. View the first few rows
3. Check for missing data, duplicate data, and unusual data
4. Standardize some columns so the analysis becomes easier

```python
# Load the dataset
def load_data(file_path):
    return pd.read_csv(file_path)

data_path = Path('df_weather.csv')
df_weather = load_data(data_path)
```

### Important column groups

1) Location information group
- `location.name`: province/city name
- `location.region`: region
- `location.terrain`: terrain type
- `location.lat`, `location.lon`: latitude and longitude

2) Time group
- `date`: observation date
- `month`: month (created from the `date` column)

3) Main weather indicator group
- `day.avgtemp_c`: average daily temperature
- `day.totalprecip_mm`: total daily precipitation
- `day.avghumidity`: average humidity
- `day.maxwind_kph`: maximum wind speed
- `day.uv`: UV index

4) Forecast-related group
- `day.daily_chance_of_rain`: forecast chance of rain
- `day.daily_will_it_rain`: whether it actually rained or not

> We can consider the 5 most important indicators in this article to be: **temperature, rainfall, humidity, wind, and UV**.
### Detailed meaning of the columns in the `df_weather` DataFrame

| Column Name                  | Data Type     | Description                                                           |
| :--------------------------- | :------------ | :-------------------------------------------------------------------- |
| `location.name`              | `object`      | Location name (province/city).                                        |
| `location.region`            | `object`      | Geographic region of the location.                                    |
| `location.terrain`           | `object`      | Terrain type of the location (for example: plain, mountain, coastal). |
| `location.country`           | `object`      | Country of the location (in this case, Vietnam).                      |
| `location.lat`               | `float64`     | Latitude of the location.                                             |
| `location.lon`               | `float64`     | Longitude of the location.                                            |
| `date`                       | `datetime64`  | Weather forecast date.                                                |
| `date_epoch`                 | `int64`       | Time in Epoch format (seconds since 01/01/1970 UTC).                  |
| `day.maxtemp_c`              | `float64`     | Maximum temperature of the day (°C).                                  |
| `day.maxtemp_f`              | `float64`     | Maximum temperature of the day (°F).                                  |
| `day.mintemp_c`              | `float64`     | Minimum temperature of the day (°C).                                  |
| `day.mintemp_f`              | `float64`     | Minimum temperature of the day (°F).                                  |
| `day.avgtemp_c`              | `float64`     | Average temperature of the day (°C).                                  |
| `day.avgtemp_f`              | `float64`     | Average temperature of the day (°F).                                  |
| `day.maxwind_mph`            | `float64`     | Maximum wind speed of the day (miles/hour).                           |
| `day.maxwind_kph`            | `float64`     | Maximum wind speed of the day (km/hour).                              |
| `day.totalprecip_mm`         | `float64`     | Total daily precipitation (mm).                                       |
| `day.totalprecip_in`         | `float64`     | Total daily precipitation (inch).                                     |
| `day.totalsnow_cm`           | `float64`     | Total daily snowfall (cm).                                            |
| `day.avgvis_km`              | `float64`     | Average visibility of the day (km).                                   |
| `day.avgvis_miles`           | `float64`     | Average visibility of the day (miles).                                |
| `day.avghumidity`            | `int64`       | Average humidity of the day (%).                                      |
| `day.daily_will_it_rain`     | `int64`       | Whether it rained on that day (1 = Yes, 0 = No).                      |
| `day.daily_chance_of_rain`   | `int64`       | Chance of rain for that day (%).                                      |
| `day.condition.text`         | `object`      | Weather condition description (for example: "Sunny", "Partly cloudy"). |
| `day.condition.icon`         | `object`      | Link to the weather condition icon.                                   |
| `day.condition.code`         | `int64`       | Weather condition code.                                               |
| `day.uv`                     | `float64`     | UV index.                                                             |
| `astro.sunrise`              | `object`      | Sunrise time.                                                         |
| `astro.sunset`               | `object`      | Sunset time.                                                          |
| `astro.moonrise`             | `object`      | Moonrise time.                                                        |
| `astro.moonset`              | `object`      | Moonset time.                                                         |
| `astro.moon_phase`           | `object`      | Moon phase.                                                           |
| `astro.moon_illumination`    | `int64`       | Moon illumination (%).                                                |

These columns provide a comprehensive view of weather conditions at different locations across Vietnam, including information on temperature, humidity, wind, precipitation, visibility, and astronomical factors.
# 2. Check data quality

This is an extremely important step, because if the data has errors and we do not check it first, our conclusions will no longer be accurate.

### What should we check?
- **Missing values**: blank cells / missing data
- **Duplicate rows**: repeated rows
- **Outlier**: values that differ too much from most of the data

### Why is it necessary?
- Missing data can distort average calculations
- Duplicate data can cause one location to be counted twice
- In weather data, unusual cases such as sudden heavy rain are natural, but they may also be data-entry errors.

```
# Data quality audit

audit_df = df_weather.copy()
audit_df['date'] = pd.to_datetime(audit_df['date'], errors='coerce')

missing_by_col = audit_df.isna().sum().sort_values(ascending=False)
duplicate_rows = int(audit_df.duplicated().sum())

# Outlier detection using IQR method
numeric_cols = ['day.avgtemp_c', 'day.totalprecip_mm', 'day.maxwind_kph', 'day.avghumidity', 'day.uv']
outlier_summary = []
for col in numeric_cols:
    q1, q3 = audit_df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outlier_rate = ((audit_df[col] < lower) | (audit_df[col] > upper)).mean() * 100
    outlier_summary.append((col, q1, q3, iqr, outlier_rate))
outlier_df = pd.DataFrame(outlier_summary, columns=['feature', 'q1', 'q3', 'iqr', 'outlier_rate_pct'])

# Label consistency checks
region_values = sorted(audit_df['location.region'].dropna().unique())
terrain_values = sorted(audit_df['location.terrain'].dropna().unique())

print('=== Data Quality Audit ===')
print(f'Total rows: {len(audit_df):,}')
print(f'Number of completely duplicated rows: {duplicate_rows}')
print('\nTop 10 columns with the most missing values:')
display(missing_by_col.head(10).to_frame('missing_count'))

print('\nOutlier rate by IQR (%):')
display(outlier_df.sort_values('outlier_rate_pct', ascending=False))

print('\nRegion labels (location.region):')
print(region_values)
print('\nTerrain labels (location.terrain):')
print(terrain_values)
```

**Quick check results**

- **Total rows:** 26,018
- **Number of completely duplicated rows:** 252
- **Missing data in the main columns:** None

**Top 10 columns with the most missing values:**

|             |    missing_count |
|:-------------------|------:|
| location.name | 0 |
| location.region | 0 |
| location.terrain | 0 |
| location.country | 0 |
| location.lat | 0 |
| location.lon | 0 |
| date | 0 |
| date_epoch | 0 |
| day.maxtemp_c | 0 |
| day.maxtemp_f | 0 |


**Outlier rate by IQR (%)**

| feature            |    q1 |   q3 |   iqr |   outlier_rate_pct |
|:-------------------|------:|-----:|------:|-------------------:|
| day.totalprecip_mm |  0.01 |  8.3 |  8.29 |               8.6  |
| day.uv             |  6    |  7   |  1    |               6.84 |
| day.avgtemp_c      | 22.8  | 28.1 |  5.3  |               2.56 |
| day.avghumidity    | 70    | 85   | 15    |               1.52 |
| day.maxwind_kph    | 10.8  | 19.1 |  8.3  |               1.03 |

**Comments:**

- The dataset is large in scale (around 26k rows), and there is no missing data in the main columns used for modeling and analysis.
- There are some fully duplicated rows (about 252 rows). If we want a more sensitive analysis, we need to remove them.
- **Outliers in precipitation and UV**: this is reasonable, because weather naturally has days with extremely heavy rain or very strong sunshine.

Terminology:

- ***IQR (Interquartile Range)**: the interquartile range, often used to detect outliers.*
- ***Outlier**: a data point that lies far away from the rest.*
# 3. Clean and prepare the data

After checking, we need to prepare the data so that it becomes easier to analyze.

- Fix the corrupted region label so region names are written consistently
- Convert the `date` column to datetime so it is easier to filter by time
- Create an additional `month` column for seasonal analysis
- Build summary tables by **region** and **month** to draw trend charts across the year

```
# 0. Fix data issues
df_weather['location.region'] = df_weather['location.region'].replace('Tr [*]ung du và miền núi Bắc Bộ', 'Trung du và miền núi Bắc Bộ')

# 1. Convert the 'date' column in df_weather to datetime objects
df_weather['date'] = pd.to_datetime(df_weather['date'])

# 2. Extract the month from the 'date' column and store it in a new column called 'month'
df_weather['month'] = df_weather['date'].dt.month

# 3. Create a new DataFrame called monthly_weather_summary by grouping df_weather
# by 'location.region' and 'month'. Calculate the mean of 'day.avgtemp_c' and
# 'day.totalprecip_mm' for each group. Reset the index of the resulting DataFrame.
monthly_weather_summary = df_weather.groupby(['location.region', 'month'])[['day.avgtemp_c', 'day.totalprecip_mm']].mean().reset_index()

# 4. Define a list named desired_region_order
desired_region_order = [
    'Trung du và miền núi Bắc Bộ',
    'Đồng Bằng Sông Hồng',
    'Bắc Trung Bộ và Duyên hải miền Trung',
    'Tây Nguyên',
    'Đông Nam Bộ',
    'Đồng Bằng Sông Cửu Long'
]
```

# 4. Basic descriptive analysis

The goal is to answer: **What is Vietnam's weather generally like?**

We will use:
- Averages
- Proportions
- Charts
- Group comparisons

This style of analysis is simple, but it helps us see the overall big picture of Vietnam's weather.
## 4.1. The overall picture by region

In this section, we take the averages of 3 main indicators:
- Temperature
- Precipitation
- Humidity
```
# 1. Calculate regional averages
regional_averages = df_weather.groupby('location.region')[['day.avgtemp_c', 'day.totalprecip_mm', 'day.avghumidity']].mean().reset_index()
regional_averages.rename(columns={'day.avgtemp_c': 'avg_temp_c', 'day.totalprecip_mm': 'avg_precip_mm', 'day.avghumidity': 'avg_humidity'}, inplace=True)

# 2. Calculate overall averages
overall_averages = df_weather[['day.avgtemp_c', 'day.totalprecip_mm', 'day.avghumidity']].mean().to_frame().T
overall_averages['location.region'] = 'Nationwide'
overall_averages.rename(columns={'day.avgtemp_c': 'avg_temp_c', 'day.totalprecip_mm': 'avg_precip_mm', 'day.avghumidity': 'avg_humidity'}, inplace=True)

# Ensure column order is consistent before concatenation
overall_averages = overall_averages[regional_averages.columns]

# 3. Concatenate the DataFrames
all_averages = pd.concat([regional_averages, overall_averages], ignore_index=True)

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Define common x-labels for all subplots
x_labels = all_averages['location.region'].unique()

# Subplot 1: Average Temperature
sns.barplot(x='location.region', y='avg_temp_c', data=all_averages, palette='plasma', ax=axes[0], hue='location.region', legend=False)
axes[0].set_title('Average temperature (°C) by region and nationwide')
axes[0].set_xlabel('Region')
axes[0].set_ylabel('Average temperature (°C)')
axes[0].set_xticks(range(len(x_labels)))
axes[0].set_xticklabels(x_labels, rotation=45, ha='right')
axes[0].grid(axis='y', linestyle='--', alpha=0.7)

# Subplot 2: Average Precipitation
sns.barplot(x='location.region', y='avg_precip_mm', data=all_averages, palette='coolwarm', ax=axes[1], hue='location.region', legend=False)
axes[1].set_title('Average precipitation (mm) by region and nationwide')
axes[1].set_xlabel('Region')
axes[1].set_ylabel('Average precipitation (mm)')
axes[1].set_xticks(range(len(x_labels)))
axes[1].set_xticklabels(x_labels, rotation=45, ha='right')
axes[1].grid(axis='y', linestyle='--', alpha=0.7)

# Subplot 3: Average Humidity
sns.barplot(x='location.region', y='avg_humidity', data=all_averages, palette='viridis', ax=axes[2], hue='location.region', legend=False)
axes[2].set_title('Average humidity (%) by region and nationwide')
axes[2].set_xlabel('Region')
axes[2].set_ylabel('Average humidity (%)')
axes[2].set_xticks(range(len(x_labels)))
axes[2].set_xticklabels(x_labels, rotation=45, ha='right')
axes[2].grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
```

![01_regional_overview.png](/static/uploads/20260323_002313_d296d689.png)


*Three average charts by region and nationwide: temperature, precipitation, and humidity.*

**Comments**: 
- Across Vietnam's geographic regions, the weather is generally hot, rainy, and humid, creating a muggy feeling that matches the nature of a tropical climate: all regions have an average temperature above 20°C, average daily precipitation above 5 mm (that is, more than 1500 mm/year), and humidity above 70%.
- Looking at all three charts above, we can see that the differences in average temperature, humidity, and precipitation between regions are not large. This is further confirmed when we compare the relationship between geographic coordinates and weather indicators.
## 4.2. Differences across space and time

There are two important ideas here:

**By geographic position**  
We examine whether latitude and longitude are related to temperature and precipitation.

- If the correlation is weak → the weather between places is not very different just because of coordinates
- If the correlation is clear → geographic position has a significant effect

**By time of year**  
We group the data by **month** to see:
- Which month is hottest
- Which month is rainiest
- Whether each region has a similar or different seasonal pattern

**Terminology:**
- ***Correlation**: the extent to which two variables change together.*
- ***Pivot table**: a summary table that reshapes data into a form that is easier to read and plot.*
- ***Seasonality**: a pattern that repeats by season or by month.*
### 4.2.1. Spatial variation by geographic position
```
selected_columns = ['location.lat', 'location.lon', 'day.avgtemp_c', 'day.totalprecip_mm']
df_correlation = df_weather[selected_columns].copy()
df_correlation.dropna(inplace=True)

correlation_matrix = df_correlation.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Correlation matrix among latitude, longitude, average temperature, and precipitation')
plt.show()
```

![02_correlation_lat_lon_weather.png](/static/uploads/20260323_002632_78c45bc7.png)

*Correlation matrix among latitude, longitude, average temperature, and precipitation.*

**Comments**: 
- We can see that geographic coordinates have a **weak correlation** with weather indicators, meaning that weather characteristics are fairly uniform and do not differ too much between regions. There is, however, a negative correlation between latitude and average temperature (-0.4), showing that as latitude increases (farther from the equator), average temperature tends to decrease.
- But when we look across time, the geographic regions show clear differences in how weather is expressed. The chart below shows the annual changes in temperature and precipitation for each region:

```
# 1. Create a pivot table named temp_pivot
temp_pivot = monthly_weather_summary.pivot_table(
    index='location.region',
    columns='month',
    values='day.avgtemp_c',
    observed=False
)

# 2. Reorder the rows of temp_pivot
temp_pivot_reordered = temp_pivot.reindex(desired_region_order)

# 3. Create a pivot table named precip_pivot
precip_pivot = monthly_weather_summary.pivot_table(
    index='location.region',
    columns='month',
    values='day.totalprecip_mm',
    observed=False
)

# 4. Reorder the rows of precip_pivot
precip_pivot_reordered = precip_pivot.reindex(desired_region_order)

# 5. Create a figure with two subplots
fig, axes = plt.subplots(2, 1, figsize=(10, 8)) # 2 rows, 1 column
plt.subplots_adjust(hspace=0.2)

# 6. Top heatmap: Monthly Average Temperature
sns.heatmap(
    temp_pivot_reordered,
    cmap='coolwarm',
    annot=True,
    fmt=".1f",
    linewidths=.5,
    square=True,
    annot_kws={'fontsize': 8},
    cbar_kws={"shrink": 0.5},
    ax=axes[0]
)
axes[0].set_title('Monthly Average Temperature (°C) by Region')
axes[0].set_xlabel('Month')
axes[0].set_ylabel('Region')

# 7. Bottom heatmap: Monthly Average Precipitation
sns.heatmap(
    precip_pivot_reordered,
    cmap='Blues',
    annot=True,
    fmt=".1f",
    linewidths=.5,
    square=True,
    annot_kws={'fontsize': 8},
    cbar_kws={"shrink": 0.5},
    ax=axes[1]
)
axes[1].set_title('Monthly Average Precipitation (mm) by Region')
axes[1].set_xlabel('Month')
axes[1].set_ylabel('Region')

# 8. Adjust layout to prevent overlapping titles/labels
plt.tight_layout()

# 9. Display the plot
plt.show()
```


![03_monthly_temp_precip_by_region.png](/static/uploads/20260323_002845_551ccdae.png)

*Average monthly temperature and average monthly precipitation by region.*

**Analysis of the Monthly Average Temperature by Region chart:**

*   **General trend**: Most regions have high temperatures, peaking in the middle of the year (April - August) and reaching the lowest level in the early and late months of the year (December - February), clearly reflecting a seasonal cycle.
*   **Mekong Delta and Southeast**: Maintain stable high temperatures throughout the year, with less seasonal variation than other regions, and average temperatures usually above 25°C. Temperatures peak around April-May.
*   **North Central and South Central Coast**: Show clear seasonal temperature variation. Temperatures are lowest in winter and gradually increase into summer, peaking in June-July.
*   **Northern Midlands and Mountains, Red River Delta**: Show the largest temperature gap between winter and summer. Winter (December - February) is quite cold, especially in the Northern Midlands and Mountains, while summer (June - August) becomes hot. The Northern Midlands and Mountains usually have the lowest winter temperatures in the country.
*   **Central Highlands**: Have a milder climate than other regions, with less drastic variation, though temperatures still tend to rise in the dry season and decrease slightly in the rainy season.

**Analysis of the Monthly Average Precipitation by Region chart:**

*   **General trend**: Most regions have a clear rainy season concentrated in the middle and later months of the year (May - October), and a dry season in the early months.
*   **Mekong Delta and Southeast**: Have a long rainy season, with the highest precipitation around September-October. The dry season lasts from December to April.
*   **North Central and South Central Coast**: Precipitation is unevenly distributed. This region is often affected by storms and tropical depressions, causing heavy rain in the later months of the year (September - November), and sometimes off-season rainfall.
*   **Northern Midlands and Mountains, Red River Delta**: Heavy rain is concentrated in summer (June - September), especially in July-August. This is also the storm and flood season in northern Vietnam.
*   **Central Highlands**: Have a clear rainy season from May to October, with rainfall peaking around August-September. The dry season is very distinct, with extremely low rainfall from December to April.

**Conclusion**
*   While northern geographic regions have two clearly different thermal regimes during the year—hot in summer and autumn, cold in spring and winter—the south stays hot year-round, with little temperature difference.
*   The hottest period of the year in the south coincides with the end of the dry season, while in the north it coincides with the rainy season. This creates two typical climate patterns: in the south, a sub-equatorial climate with rainy and dry seasons; in the north, a monsoon climate with cold dry winters and hot humid summers.
*   The rainy season is not the same across regions.
*   Even within one country, Vietnam's monthly weather rhythm shows quite clear regional differentiation.
### 4.2.2. Variation across time

This section does not directly talk about rain or temperature, but it helps us understand that:
- Weather indicators do not stay fixed over time
- Many climate phenomena are influenced by annual cycles

```
# 1. Prepare the data
df = df_weather.copy()
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month

# Function to convert AM/PM time to decimal hours
def time_to_hours(time_str):
    try:
        return pd.to_datetime(time_str, format='%I:%M %p').hour + \
               pd.to_datetime(time_str, format='%I:%M %p').minute / 60
    except:
        return None

# 2. Calculate duration values (unit: hours)
# Day length = Sunset - Sunrise
df['day_length'] = df['astro.sunset'].apply(time_to_hours) - df['astro.sunrise'].apply(time_to_hours)


# 3. Group by month
monthly_astro = df.groupby('month').agg({
    'day_length': 'mean',
}).sort_index()

# 4. Draw the chart
plt.figure(figsize=(12, 6))

plt.plot(monthly_astro.index, monthly_astro['day_length'],
         marker='o', linewidth=3, color='#f39c12', label='Day length (sunlight duration)')

# 5. Refine the chart

plt.xlabel('Month', fontsize=12)
plt.ylabel('Hours', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.figtext(0.5, 0.01, "Change in daylight duration by month",
            ha="center", fontsize=15, bbox={"facecolor":"orange", "alpha":0.1, "pad":5})
plt.subplots_adjust(bottom=0.7)

# 6. Add annotation about the "long day, short night" phenomenon
plt.annotate('Longest day (summer solstice)', xy=(6, monthly_astro['day_length'].max()),
             xytext=(7, monthly_astro['day_length'].max()+0.2),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.tight_layout()
plt.show()
```

![04_day_length_by_month.png](/static/uploads/20260323_002949_5fd431e8.png)
*Change in day length by month.*

**Comments**: 
- Day length increases from the beginning of the year and peaks around June (the summer solstice), then gradually decreases toward the end of the year. This clearly reflects the nature of a country in the Northern Hemisphere such as Vietnam, and also highlights a very characteristic temporal pattern: the days become longer toward mid-year and shorter toward the year's end.

## 4.3. Differences by terrain

Terrain has a strong influence on:
- Temperature
- Rainfall
- Wind
- Day-night temperature range

```
# 1. Prepare the data
df = df_weather.copy()

# 2. Calculate average values by terrain type (location.terrain)
terrain_stats = df.groupby('location.terrain').agg({
    'day.avgtemp_c': 'mean',
    'day.totalprecip_mm': 'mean'
}).sort_values('day.avgtemp_c')

# 3. Initialize the chart
fig, ax1 = plt.subplots(figsize=(10, 6))

# First y-axis: Average precipitation (bar)
color_rain = '#3498db'
ax1.bar(terrain_stats.index, terrain_stats['day.totalprecip_mm'], color=color_rain, alpha=0.6, label='Average precipitation (mm)')
ax1.set_xlabel('Terrain type', fontsize=12)
ax1.set_ylabel('Average precipitation (mm)', color=color_rain, fontsize=12)
ax1.tick_params(axis='y', labelcolor=color_rain)

# Second y-axis: Average temperature (line)
ax2 = ax1.twinx()
color_temp = '#e74c3c'
ax2.plot(terrain_stats.index, terrain_stats['day.avgtemp_c'], color=color_temp, marker='o', linewidth=3, label='Average temperature (°C)')
ax2.set_ylabel('Average temperature (°C)', color=color_temp, fontsize=12)
ax2.tick_params(axis='y', labelcolor=color_temp)

# 4. Customize title and grid
plt.title('Comparison of average temperature and precipitation by terrain type', fontsize=14, pad=20)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Add legend for both axes
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='upper left')

plt.tight_layout()
plt.show()
```
![05_weather_by_terrain.png](/static/uploads/20260323_003050_59a6460e.png)

*Comparison of average temperature and average precipitation by terrain type.*

**Comments**: 
- Mountainous areas have noticeably lower average temperature and precipitation than the other two terrain types, showing that the weather there tends to be cooler and more comfortable.
- Coastal areas and plains do not differ too much in weather indicators, showing a fairly uniform climate character.
# 5. Extreme weather analysis

After understanding the general picture, we move on to a slightly more difficult part:
**days with severe weather**.

This section focuses on 4 questions:
1. What level is the UV index in Vietnam usually at?
2. Are moderate and heavy rains common?
3. Does heavy rain often come with strong wind?
4. How does the day-night temperature range differ across terrain types?

Terminology:
- **UV index**: the intensity of ultraviolet radiation from the sun.
- **Temperature range**: the difference between the highest and lowest temperatures in a day.
- **Scatter plot**: a point chart used to observe the relationship between two variables.
- **Boxplot**: a chart used to observe data distribution and spread.
## 5.1. Outstanding extreme expressions

In this section, we successively examine:
- UV levels
- Rain intensity
- The relationship between rain and wind
- The day-night temperature range

```
# 1. Prepare data from df_weather
df = df_weather.copy()

def classify_uv(uv):
    if uv <= 2: return '0-2 (Low)'
    elif 3 <= uv <= 5: return '3-5 (Moderate)'
    elif 6 <= uv <= 7: return '6-7 (High)'
    elif 8 <= uv <= 10: return '8-10 (Very high)'
    else: return '11+ (Extreme)'

df['uv_rank'] = df['day.uv'].apply(classify_uv)
uv_counts = df['uv_rank'].value_counts()

# Reorder by severity level
order = ['0-2 (Low)', '3-5 (Moderate)', '6-7 (High)', '8-10 (Very high)', '11+ (Extreme)']
uv_counts = uv_counts.reindex([r for r in order if r in uv_counts.index]).fillna(0)

# Notes on danger level
descriptions = {
    '0-2 (Low)': 'Low risk',
    '3-5 (Moderate)': 'Can cause harm, protection is recommended',
    '6-7 (High)': 'High risk, sunburn after about 30 minutes',
    '8-10 (Very high)': 'Very high risk, sun protection is necessary',
    '11+ (Extreme)': 'Extremely dangerous, should stay indoors'
}

# 2. Set up colors
colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c', '#9b59b6']

# 3. Draw the chart
fig, ax = plt.subplots(figsize=(10, 10)) # Increase height to leave room for the legend below

# Draw a pie chart (full circle)
wedges, texts, autotexts = ax.pie(
    uv_counts,
    labels=None,
    autopct=lambda p: '{:.1f}%'.format(p) if p > 0 else '',
    startangle=140,
    colors=colors[:len(uv_counts)],
    pctdistance=0.7,
    textprops={'fontsize': 12, 'weight': 'bold', 'color': 'white'}
)

# Move labels < 1% to the outside
total = uv_counts.sum()
for i, p in enumerate((uv_counts / total) * 100):
    if 0 < p < 1:
        angle = (wedges[i].theta2 + wedges[i].theta1) / 2.
        x = 1.2 * np.cos(np.deg2rad(angle))
        y = 1.2 * np.sin(np.deg2rad(angle))
        autotexts[i].set_position((x, y))
        autotexts[i].set_color('black')

# 4. Add legend below the chart
legend_labels = [f"{k}: {descriptions[k]}" for k in uv_counts.index]
ax.legend(
    wedges,
    legend_labels,
    title="UV Index & Danger Level",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.05), # Push below the chart
    ncol=1, # You can change to 2 columns if you want
    fontsize=11,
    frameon=True
)

plt.title('Share of daily UV index levels in Vietnam', fontsize=16, pad=30)
plt.axis('equal')

# Adjust spacing so the legend is not cut off when saving/displaying
plt.tight_layout()
plt.subplots_adjust(bottom=0.25)

plt.show()
```

![06_uv_levels_distribution.png](/static/uploads/20260323_003142_109ff4a5.png)

*Proportion of UV index levels by day in Vietnam.*

**Comments**: 
- More than 80% of the days in the year in Vietnam have UV levels from high to very high, bringing many health risks, especially sunburn and skin cancer. Therefore, everyone should protect themselves when going outside.

```


# 1. Prepare data from df_weather
df = df_weather.copy()
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month

# 2. Define the list of moderate/heavy rain conditions
heavy_rain_list = [
    'Moderate or heavy rain shower', 'Moderate rain at times',
    'Heavy rain at times', 'Moderate or heavy rain with thunder',
    'Torrential rain shower', 'Moderate rain', 'Heavy rain'
]

# 3. Classify and group by month
# Total number of rainy days (regardless of intensity)
total_rainy = df[df['day.daily_will_it_rain'] == 1].groupby('month').size()

# Number of moderate and heavy rainy days
heavy_rainy = df[
    (df['day.daily_will_it_rain'] == 1) &
    (df['day.condition.text'].str.strip().isin(heavy_rain_list))
].groupby('month').size()

# Combine into a DataFrame and sort by month so the line looks smooth
df_area = pd.DataFrame({
    'Total rainy days': total_rainy,
    'Moderate/heavy rainy days': heavy_rainy
}).fillna(0).sort_index()

# 4. Draw the area chart (Stacked Area Chart)
plt.figure(figsize=(12, 6))

# Draw an unstacked area chart to make the difference clearer
plt.fill_between(df_area.index, df_area['Total rainy days'], color="skyblue", alpha=0.4, label='Total rainy days')
plt.plot(df_area.index, df_area['Total rainy days'], color="Slateblue", alpha=0.6, linewidth=2)

plt.fill_between(df_area.index, df_area['Moderate/heavy rainy days'], color="navy", alpha=0.5, label='Moderate/heavy rainy days')
plt.plot(df_area.index, df_area['Moderate/heavy rainy days'], color="navy", alpha=0.6, linewidth=2)

# Format the chart
plt.title('Rainy days by month in Vietnam', fontsize=15, pad=20)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of days', fontsize=12)
plt.xticks(df_area.index) # Show all months present in the data
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper left')

plt.tight_layout()
plt.show()
```

![07_rainy_days_by_month.png](/static/uploads/20260323_003215_c1f2366a.png)

*Rainy days by month and the moderate/heavy-rain portion.*

**Comments**: 
- Rain in Vietnam is mainly moderate and heavy rain (throughout most of the year, moderate/heavy rainy days account for about one-half to two-thirds of all rainy days). This shows the harsh nature of the weather for human life.

```
# 2. Set up the interface
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 8))

# 3. Draw a scatter plot categorized by terrain
scatter = sns.scatterplot(
    data=df,
    x='day.maxwind_kph',
    y='day.totalprecip_mm',
    hue='location.terrain',    # Color by terrain type
    style='location.terrain',  # Different markers for easier reading
    s=100,                     # Point size
    alpha=0.7,
    palette='viridis'          # Modern color palette
)

# 4. Draw the overall trend line (regression line) for the full dataset
sns.regplot(
    data=df,
    x='day.maxwind_kph',
    y='day.totalprecip_mm',
    scatter=False,             # Do not redraw the scatter points
    color='red',
    label='Overall trend'
)

# 5. Format the chart
plt.title('Correlation between maximum wind speed and precipitation by terrain type in Vietnam', fontsize=16, pad=20)
plt.xlabel('Maximum wind speed (km/h)', fontsize=12)
plt.ylabel('Total precipitation (mm)', fontsize=12)
plt.legend(title='Terrain type', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
```
![08_wind_precip_scatter_by_terrain.png](/static/uploads/20260323_003303_e7a5645a.png)

*Correlation between maximum wind speed and precipitation, categorized by terrain type.*

**Comments**: 
- At the same time, weather tends to evolve in the direction that heavier rain comes with stronger wind, though this trend is not very strong. Most rain in plains and mountainous areas does not come with strong wind. But in coastal areas, these two phenomena have a clearer correlation, highlighting that this is the region most exposed to natural disasters in the country.

```
# 2. Calculate the daily temperature range
df['temp_range'] = df['day.maxtemp_c'] - df['day.mintemp_c']

# 3. Draw the boxplot
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

# Draw a boxplot categorized by terrain
ax = sns.boxplot(
    data=df,
    x='location.terrain',
    y='temp_range',
    palette='Set2',
    linewidth=1.5,
    fliersize=5 # Size of outlier markers
)

# 4. Customize the chart
plt.title('Daily temperature range across terrain types', fontsize=15, pad=20)
plt.xlabel('Terrain type', fontsize=12)
plt.ylabel('Temperature range (°C)', fontsize=12)

# Add sample size notes to make the chart more credible
counts = df.groupby('location.terrain').size()
for i, label in enumerate(ax.get_xticklabels()):
    terrain_type = label.get_text()
    ax.text(i, ax.get_ylim()[1]*0.05, f'n={counts[terrain_type]}',
            ha='center', size='small', color='black', weight='semibold')

plt.tight_layout()
plt.show()
```

![09_daily_temp_range_by_terrain.png](/static/uploads/20260323_003416_295716ea.png)

*Day-night temperature range across terrain types.*

**Comments**: 
- However, in mountainous areas, the harshness of the weather appears through another factor: the difference between daytime and nighttime temperature is extremely large, and the temperature range is much wider than in the other two areas, requiring people to adapt more strongly.
# 6. Advanced analysis

In this section, we further analyze weather variability by region and dual-risk days.
## 6.1. Weather variability by region

Average indicators only tell us the typical level, but sometimes the more important thing is **variability**.

For example:
- Two regions may both have an average temperature of 26°C
- But one region is stable year-round, while the other swings between very cold and very hot

Meaning:
- Large variability → stronger weather changes
- Small variability → more stable weather

Terminology
- **Standard deviation**: how much the data fluctuates around the average.
- **IQR**: the spread of the central part of the data.

```
# Prepare the data
ext_df = df_weather.copy()
ext_df['date'] = pd.to_datetime(ext_df['date'])
ext_df['month'] = ext_df['date'].dt.month

# 1) VARIABILITY BY REGION: standard deviation and IQR
variability = (
    ext_df.groupby('location.region')
    .agg(
        temp_std=('day.avgtemp_c', 'std'),
        rain_std=('day.totalprecip_mm', 'std'),
        humidity_std=('day.avghumidity', 'std'),
        temp_q1=('day.avgtemp_c', lambda s: s.quantile(0.25)),
        temp_q3=('day.avgtemp_c', lambda s: s.quantile(0.75)),
        rain_q1=('day.totalprecip_mm', lambda s: s.quantile(0.25)),
        rain_q3=('day.totalprecip_mm', lambda s: s.quantile(0.75))
    )
    .reset_index()
)

variability['temp_iqr'] = variability['temp_q3'] - variability['temp_q1']
variability['rain_iqr'] = variability['rain_q3'] - variability['rain_q1']

print('Table of weather variability by region:')
display(
    variability[[
        'location.region', 'temp_std', 'temp_iqr', 'rain_std', 'rain_iqr', 'humidity_std'
    ]].sort_values('rain_std', ascending=False)
)

# Quick visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

sns.barplot(
    data=variability.sort_values('temp_std', ascending=False),
    x='location.region', y='temp_std', palette='rocket', ax=axes[0], hue='location.region', legend=False
)
axes[0].set_title('Standard deviation of average temperature by region')
axes[0].set_xlabel('Region')
axes[0].set_ylabel('Temperature std (°C)')
axes[0].tick_params(axis='x', rotation=35)

sns.barplot(
    data=variability.sort_values('rain_std', ascending=False),
    x='location.region', y='rain_std', palette='Blues', ax=axes[1], hue='location.region', legend=False
)
axes[1].set_title('Standard deviation of precipitation by region')
axes[1].set_xlabel('Region')
axes[1].set_ylabel('Rain std (mm)')
axes[1].tick_params(axis='x', rotation=35)

plt.tight_layout()
plt.show()
```
**Weather variability table by region**

| location.region                      |   temp_std |   temp_iqr |   rain_std |   rain_iqr |   humidity_std |
|:-------------------------------------|-----------:|-----------:|-----------:|-----------:|---------------:|
| Bắc Trung Bộ và Duyên hải miền Trung |       3.64 |        5.2 |      16.05 |       6.55 |           8.17 |
| Đồng Bằng Sông Hồng                  |       4.63 |        7.4 |      14.96 |       6.9  |          11.73 |
| Trung du và miền núi Bắc Bộ          |       5.09 |        7.5 |      13.48 |       7.53 |          14.14 |
| Đồng Bằng Sông Cửu Long              |       1.81 |        2.6 |       9.2  |      10.3  |           9.31 |
| Đông Nam Bộ                          |       1.94 |        2.9 |       9.04 |       9.38 |          10.65 |
| Tây Nguyên                           |       2.88 |        3.9 |       8.22 |       8.2  |          11.82 |


![10_weather_variability_by_region.png](/static/uploads/20260323_003602_5c2068e9.png)

*Weather variability in temperature and precipitation by region.*

**Comments:**

**1) Temperature variability (temp_std, temp_iqr)**
- `Trung du và miền núi Bắc Bộ` has the highest temperature variability (`std` about 5.09, `IQR` about 7.5), reflecting very clear seasonality and a large temperature gap between times of the year.
- `Đồng Bằng Sông Hồng` comes second (`std` about 4.63, `IQR` about 7.4), consistent with colder winters and hot humid summers.
- `Đông Nam Bộ` and `Đồng Bằng Sông Cửu Long` have the lowest variability (`std` below 2.0), showing a more stable thermal background throughout the year.

**2) Rainfall variability (rain_std, rain_iqr)**
- `Bắc Trung Bộ và Duyên hải miền Trung` has the highest `rain_std` (about 16.05), meaning there are many months/clusters of days with very different rainfall levels (dry and extremely wet periods alternating).
- `Đồng Bằng Sông Hồng` and `Trung du và miền núi Bắc Bộ` also have high rainfall variability (`std` about 14.96 and 13.48), showing a pronounced rainy-season character.
- `Tây Nguyên` has the lowest `rain_std` among the 6 regions (about 8.22). It still has a clear rainy season, but with less spread in extremes than the central regions.

**3) Meaning**
- Regions with high variability need more flexible seasonal adaptation strategies (agriculture, drainage systems, heat-health planning).
- Regions with low variability are more suitable for longer-term stable production planning.

## 6.2. Dual-risk days

This section creates 2 types of risk days:
- **Hot weather + high UV**
- **Heavy rain + strong wind**

The main purpose is to suggest:
- Which areas need more attention to heat-related health risks
- Which areas need more attention to natural-disaster risks

**Terminology:**
- **Threshold**: a cutoff level used to define something as “high”.
- **Percentile**: for example, 90% means belonging to the top 10% of the data.

```
# 2) DUAL RISK: hot weather + high UV, heavy rain + strong wind
risk_df = ext_df.copy()

# Thresholds based on percentiles to fit this specific dataset
hot_threshold = risk_df['day.maxtemp_c'].quantile(0.90)
rain_threshold = risk_df['day.totalprecip_mm'].quantile(0.90)
wind_threshold = risk_df['day.maxwind_kph'].quantile(0.90)

risk_df['risk_hot_uv'] = (risk_df['day.maxtemp_c'] >= hot_threshold) & (risk_df['day.uv'] >= 8)
risk_df['risk_rain_wind'] = (risk_df['day.totalprecip_mm'] >= rain_threshold) & (risk_df['day.maxwind_kph'] >= wind_threshold)

risk_summary_region = (
    risk_df.groupby('location.region')[['risk_hot_uv', 'risk_rain_wind']]
    .mean()
    .mul(100)
    .reset_index()
)

print('Percentage (%) of dual-risk days by region:')
display(risk_summary_region.sort_values('risk_rain_wind', ascending=False))

# Top provinces with the highest dual risks
top_hot_uv = (
    risk_df.groupby('location.name')['risk_hot_uv'].mean().mul(100)
    .sort_values(ascending=False).head(10)
)
top_rain_wind = (
    risk_df.groupby('location.name')['risk_rain_wind'].mean().mul(100)
    .sort_values(ascending=False).head(10)
)

print('\nTop 10 provinces - hot weather + high UV risk (% of days):')
display(top_hot_uv)
print('Top 10 provinces - heavy rain + strong wind risk (% of days):')
display(top_rain_wind)

# Heatmap by region
heatmap_data = risk_summary_region.set_index('location.region')[['risk_hot_uv', 'risk_rain_wind']]

plt.figure(figsize=(8, 4.5))
sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd', linewidths=0.5)
plt.title('Percentage of dual-risk days by region (%)')
plt.xlabel('Risk type')
plt.ylabel('Region')
plt.tight_layout()
plt.show()
```

**Percentage of dual-risk days by region**

| location.region                      |   risk_hot_uv |   risk_rain_wind |
|:-------------------------------------|--------------:|-----------------:|
| Bắc Trung Bộ và Duyên hải miền Trung |         10.12 |             2.11 |
| Đồng Bằng Sông Hồng                  |          6.87 |             1.52 |
| Đồng Bằng Sông Cửu Long              |         13.19 |             1.43 |
| Đông Nam Bộ                          |         18.72 |             1.33 |
| Trung du và miền núi Bắc Bộ          |          3.94 |             0.5  |
| Tây Nguyên                           |          7.55 |             0.39 |

**Top 10 provinces with hot weather + high UV risk**

```text
location.name
Bình Dương         25.181598
Đồng Nai           25.181598
TP. Hồ Chí Minh    25.181598
Tây Ninh           23.728814
Quảng Ngãi         23.244552
Vĩnh Long          17.917676
An Giang           17.433414
Long An            17.191283
Bến Tre            17.191283
Tiền Giang         17.191283
Name: risk_hot_uv, dtype: float64
```

**Top 10 provinces with heavy rain + strong wind risk**

```text
location.name
Kiên Giang         7.021792
Quảng Bình         5.326877
Ninh Thuận         3.874092
Bà Rịa-Vũng Tàu    3.631961
Phú Yên            3.389831
Bình Định          3.389831
Hà Tĩnh            2.905569
Nghệ An            2.663438
Cà Mau             2.179177
Tây Ninh           2.179177
Name: risk_rain_wind, dtype: float64
```

![11_dual_risk_days_by_region.png](/static/uploads/20260323_003758_f5b64932.png)
*Percentage of dual-risk days by region.*

**Comments:**

**1) Hot weather + high UV risk stands out more than heavy rain + strong wind risk**
- The highest `risk_hot_uv` rate appears in `Đông Nam Bộ` (about 18.7%), followed by `Đồng Bằng Sông Cửu Long` (about 13.2%) and `Bắc Trung Bộ và Duyên hải miền Trung` (about 10.1%).
- The `risk_rain_wind` rate is generally much lower across all regions (highest is about 2.1% in `Bắc Trung Bộ và Duyên hải miền Trung`).

**2) Priority provinces to monitor**
- Notable hot + high UV group: `Bình Dương`, `Đồng Nai`, `TP. Hồ Chí Minh`, `Tây Ninh`, `Quảng Ngãi`.
- Notable heavy rain + strong wind group: `Kiên Giang`, `Quảng Bình`, `Ninh Thuận`, `Bà Rịa-Vũng Tàu`, `Phú Yên`, `Bình Định`.

**3) Meaning of the spatial distribution**
- The `Đông Nam Bộ` cluster and part of the `Đồng Bằng Sông Cửu Long` face greater pressure from hot weather and strong UV, consistent with the stable high-temperature background observed earlier.
- Rain-wind risk is concentrated along the coast, reflecting the influence of marine circulation, monsoon flow, and strong disturbance events.

# 7. Conclusion

From the analyses above, we can draw 3 main ideas:

- Vietnam's weather is generally clearly tropical: hot, humid, and rainy.
- The differences between regions are not large at the average level, but when viewed by **month**, **terrain**, and **extreme intensity**, there is quite clear differentiation.
- Some notable risks are intense sunshine/high UV and seasonal heavy rain events, showing the need for adaptation by region and by time.

In short, the data shows that Vietnam's weather has both a nationwide unity and important spatial-temporal differences. This is a good foundation for extending the work toward forecasting analysis and practical applications.

# 8. Predicting Rain or No Rain: Exploring the Power of Random Forest 🌧️

Weather forecasting is always a classic and fascinating topic. How can we use seemingly quiet indicators such as temperature, wind speed, or humidity to accurately predict whether dark clouds will actually bring rain?

Next, I will guide you step by step to build a machine learning system that predicts whether it will rain or not based on the presented dataset, using one of the sharpest algorithms: **Random Forest**.

---

## 8.1. Problem formulation

The main objective of this problem is very close to real life: build a Machine Learning model that can answer the question, "Will it rain on that day or not?"

In mathematical terms, we are looking for a function $f(X) = y$. In this case:
* **Input (X - Features):** specific weather parameters of a day. Based on the initial analysis, the most influential factors include:
  * Average temperature (`day.avgtemp_c`)
  * Maximum wind speed (`day.maxwind_kph`)
  * Precipitation (`day.totalprecip_mm`)
  * Average humidity (`day.avghumidity`)
  * UV index (`day.uv`)
* **Output (y - Target):** a binary variable representing whether it rains or not:
  * `1`: Rain
  * `0`: No Rain

---

## 8.2. The Random Forest algorithm: Strength from a “forest of decisions”


![random_forest_diagram.png](/static/uploads/20260322_235601_c6b19a73.png)

<br>*Random Forest illustration (Image generated by Gemini)*

**Random Forest** is an algorithm from the Ensemble Learning family, famous for its impressive accuracy and strong resistance to overfitting. The essence of the model can be summarized by the philosophy: *"The wisdom of the crowd."*

Instead of trusting a single Decision Tree, which can easily lean toward memorizing the original dataset, Random Forest creates a "forest" containing hundreds or even thousands of independent decision trees. Each tree produces its own prediction independently.

At the end, **Majority Voting** is applied: the result reported by the majority of the trees becomes the final output of the algorithm.
This model is very robust thanks to two debiasing techniques:
- **Bagging (Bootstrap Aggregating):** the trees are trained on random subsets of the data.
- **Feature Randomness:** the number of features considered at each split node is also chosen randomly, making the forest highly diverse.

---

## 8.3. Model training  

Once we start coding, the training process goes through very logical stages:

**Step 1: Clean the data and select features**  
We extract exactly 5 columns considered as Input and 1 column as Output. Noisy or missing rows are removed using `.dropna()` to ensure the training set remains complete.

**Step 2: Split the dataset (Train / Test Split)**  
Apply an `80/20` split:
- **80%** of the data is used for the Random Forest model to “learn” the patterns.
- The remaining **20%** is kept aside as the model's “final exam.”

**Step 3: Initialize and fit the model**  
Call the `RandomForestClassifier` model from the powerful Scikit-learn ecosystem. We use `n_estimators=100`, which means 100 individual decision trees work together to make predictions.  
With just the command `rf_model.fit(X_train, y_train)`, the model starts digesting the data and learning the weather patterns.

---

## 8.4. Evaluation

Now comes the most exciting part. We bring out the 20% test set (data the model has never seen before) to “grade” it. The result is truly impressive: accuracy reaches an extremely high **0.9996** — meaning it is remarkably close to a perfect 100%.

To visualize this more clearly, you can look at the **Confusion Matrix** below. The chart shows that the model does an excellent job separating the two classes, "Rain" and "No Rain." The prediction error rates — False Positives (no rain but predicted rain) and False Negatives (rain but predicted no rain) — are reduced to almost zero.

![confusion_matrix_rf.png](/static/uploads/20260322_235625_dd9c1dee.png)


Another "strong piece of evidence" of Random Forest's capability is the **ROC Curve**. The ROC curve hugs the upper-left corner of the chart, which means the AUC (area under the curve) also approaches 1.0. Put simply, the closer ROC/AUC is to 1.0, the sharper the model is at separating the two weather states.


![roc_curve_rf.png](/static/uploads/20260322_235636_c113499f.png)


---

## 8.5. Real-world example test

Now imagine you need a quick forecast for tomorrow based on the expected weather information:
- Average temperature: `32.5°C`
- Maximum wind speed: `12 km/h`
- Measured precipitation: `5.2 mm`
- Average humidity: `85%` (Quite muggy!)
- UV level: `4.0`

Immediately pass this set of parameters into `rf_model.predict()` to get the classification output, and `rf_model.predict_proba()` to measure confidence.

**And here is the result:**
> --- MODEL TEST RESULT ---  
> Prediction: **IT WILL RAIN 🌧️**  
> Model confidence: **98.00%**  

A very confident prediction. Indeed, with signs such as a relatively low UV level, existing precipitation, and very high humidity, Random Forest quickly captures what the sky is likely to do.

See you in the next ML article. Support the post if you find it offers useful insights!

📌 **Source Code & Dataset:** [Kaggle Notebook - Vietnam Weather Data Analysis and Rain](https://www.kaggle.com/code/thanhkieuvo/blog2-vietnam-weather-data-analysis-and-rain/edit)

""" I, Ali Abubaker 000857347, certify that this material is my original work. I have not shared this file. No other person's work has been used without due acknowledgement."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
def assign_stress_level(x):
    if x in [1, 2]:return 'Low Stress'
    elif x in [3, 4, 5]:return 'Hi Stress'
    return None
def calculate_group_stats(group):
    total_weighted_cigs = group['Weighted_Cigs'].sum()
    total_weight = group['WTS_M'].sum()
    avg_cigs = total_weighted_cigs / total_weight
    return {'total_weighted_cigs': total_weighted_cigs, 'total_weight': total_weight, 'Avg_Cigs': avg_cigs}
def calculate_ci(group):
    n = len(group)
    weighted_mean = np.sum(group['SMK_045'] * group['WTS_M']) / np.sum(group['WTS_M'])
    weighted_variance = np.sum(group['WTS_M'] * (group['SMK_045'] - weighted_mean) ** 2) / np.sum(group['WTS_M'])
    weighted_se = np.sqrt(weighted_variance / n)
    ci = weighted_se * stats.t.ppf(0.9, n - 1)
    return {'Avg_Cigs_ci': weighted_mean, 'CI': ci}
def assign_gender_stress(row):
    gender = 'Male' if row['DHH_SEX'] == 1 else 'Female'
    return f"{gender} {row['Stress_Level']}"
# Load and preprocess data
df = pd.read_csv('pumf_cchs.csv')
df = df[(df['SMK_045'] > 0) & (df['SMK_045'] <= 25)]
df['Stress_Level'] = df['GEN_020'].apply(assign_stress_level)
df = df.dropna(subset=['Stress_Level'])
df['Weighted_Cigs'] = df['SMK_045'] * df['WTS_M']
# Group data and calculate statistics
grouped = []
for (age, sex, stress), group in df.groupby(['DHHGAGE', 'DHH_SEX', 'Stress_Level']):
    group_stats = calculate_group_stats(group)
    ci = calculate_ci(group)
    grouped.append({'DHHGAGE': age, 'DHH_SEX': sex, 'Stress_Level': stress, **group_stats, **ci})
grouped = pd.DataFrame(grouped)
# Map age groups and assign colors
age_groups = {1: '12 to 17', 2: '18 to 34', 3: '35 to 49', 4: '50 to 64', 5: '65 and older'}
grouped['Age_Group'] = grouped['DHHGAGE'].map(age_groups)
color_map = {'Male Low Stress': 'cyan', 'Female Low Stress': 'pink', 'Male Hi Stress': 'cyan', 'Female Hi Stress': 'pink'}
grouped['Gender_Stress'] = grouped.apply(assign_gender_stress, axis=1)
grouped['Color'] = grouped['Gender_Stress'].map(color_map)
# Plotting
age_positions = np.arange(len(age_groups)) * 5
bar_order = ['Male Low Stress', 'Female Low Stress', 'Male Hi Stress', 'Female Hi Stress']
fig, ax = plt.subplots(figsize=(8, 6))# Adjusted to 800x600 pixels
bar_width = 0.7
for age_group in age_groups:
    subset = grouped[grouped['DHHGAGE'] == age_group]
    for i in range(len(bar_order)):
        gender_stress = bar_order[i]
        data = subset[subset['Gender_Stress'] == gender_stress]
        if not data.empty:
            color = data['Color'].iloc[0] if pd.notna(data['Color'].iloc[0]) else 'gray'
            x_position = age_positions[age_group - 1] + i * (bar_width + 0.1)
            hatch = 'O' if 'Hi Stress' in gender_stress else None
            ci_value = data['CI'].iloc[0]
            ax.bar(x_position, data['Avg_Cigs'].iloc[0], yerr=ci_value, width=bar_width, color=color, hatch=hatch, label=gender_stress if age_group == 1 else "", edgecolor='gray', capsize=2)
ax.set_xticks(age_positions + (bar_width + 0.1) * 1.5)
ax.set_xticklabels([age_groups[age] for age in age_groups], fontsize=12)
ax.set_xlabel('Age of Smoker', fontsize=18)
ax.set_ylabel('Number of Cigarettes per Day', fontsize=16)
ax.set_title('Daily Smokers, Age + Gender + Stress vs.\nCigarettes Smoked / Day, 80% Confidence Intervals', fontsize=15, fontweight='bold')
ax.set_ylim(0, 25)
ax.set_yticks([0, 5, 10, 15, 20, 25])
ax.legend(fontsize=12, title='Gender and Stress Level', title_fontsize=12)
plt.savefig('smoking_plot.png', dpi=100, bbox_inches='tight')
plt.show()


# Answer to Question 1:
# Because there is more variability in the data due to a smaller sample size, the confidence intervals for the 12–17 age group are large.
# Answer to Question 2:
#The evidence suggests that people with high levels of stress do not always smoke more than people with low levels of stress. Since the error bars overlap, there is no statistically significant difference.
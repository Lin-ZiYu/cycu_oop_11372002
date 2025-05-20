import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv('20250520/midterm_scores.csv')

# Subjects to plot
subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']

# Define bins: 0-9, 10-19, ..., 90-100
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
bin_labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]

# Calculate the frequency of scores in each bin for each subject
bin_counts = {subject: pd.cut(df[subject], bins=bins, labels=bin_labels).value_counts(sort=False) for subject in subjects}

# Prepare data for plotting
x = np.arange(len(bin_labels))  # the label locations
width = 0.12  # the width of the bars
multiplier = 0

# Define Morandi color palette
morandi_colors = ['#7ab8cc', '#8fbc8f',  '#e6c3c3', '#00808c', '#eee8aa', '#b0c4de', '#d8bfd8',]

fig, ax = plt.subplots(figsize=(12, 8), layout='constrained')

# Plot each subject's data
for subject, counts, color in zip(subjects, bin_counts.values(), morandi_colors):
    offset = width * multiplier
    rects = ax.bar(x + offset, counts, width, label=subject, color=color)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Number of Students')
ax.set_title('Score Distribution by Subject')
ax.set_xticks(x + width * (len(subjects) - 1) / 2, bin_labels)
ax.legend(loc='upper right', ncols=2)
ax.set_ylim(0, max(max(counts) for counts in bin_counts.values()) + 5)

# Save the figure as a PNG file
plt.savefig('score_distribution_morandi.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

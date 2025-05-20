import pandas as pd

# Load CSV data
df = pd.read_csv('20250520/midterm_scores.csv')

# Subjects to check
subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']

# Count the number of failing grades (< 60) for each student
df['FailingSubjects'] = (df[subjects] < 60).sum(axis=1)

# Filter students with more than 4 failing grades
students_with_many_fails = df[df['FailingSubjects'] >= 4]

# Save the filtered data to a new CSV file
output_file = '20250520/dropout_students.csv'
students_with_many_fails.to_csv(output_file, index=False)

print("Students with more than 5 failing grades:")
print(students_with_many_fails[['Name', 'StudentID', 'FailingSubjects']])
print(f"Data has been saved to {output_file}")



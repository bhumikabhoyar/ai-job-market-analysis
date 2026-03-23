import pandas as pd
import ast
import sqlite3
import matplotlib.pyplot as plt
from collections import Counter

# ✅ Load dataset
df = pd.read_csv('gsearch_jobs.csv')

# ✅ Select columns
df = df[['title', 'company_name', 'location', 'salary_avg', 'schedule_type', 'work_from_home', 'description_tokens']]

# ✅ Clean data
df = df.dropna(subset=['title', 'description_tokens'])
df['salary_avg'] = df['salary_avg'].fillna(0)
df = df.drop_duplicates()
df = df.reset_index(drop=True)

# 🔥 IMPORTANT FIX (string → list)
df['description_tokens'] = df['description_tokens'].apply(ast.literal_eval)

# ================= SQL PART ================= #
# ✅ Create copy for SQL
df_sql = df.copy()

# Convert list → string only for SQL
df_sql['description_tokens'] = df_sql['description_tokens'].astype(str)

# Store in SQLite
conn = sqlite3.connect('jobs.db')
df_sql.to_sql('jobs', conn, if_exists='replace', index=False)

print("Data stored in SQLite successfully")


# ✅ SQL Query
cursor = conn.cursor()

query = """
SELECT title, COUNT(*) as count
FROM jobs
GROUP BY title
ORDER BY count DESC
LIMIT 5;
"""

cursor.execute(query)

results = cursor.fetchall()

print("\nTop Job Titles:")
for row in results:
    print(row)

query_salary = """
SELECT title, AVG(salary_avg) as avg_salary
FROM jobs
WHERE salary_avg > 0
GROUP BY title
ORDER BY avg_salary DESC
LIMIT 5;
"""

cursor.execute(query_salary)

results = cursor.fetchall()

print("\nTop Paying Job Roles:")
for row in results:
    print(row)

query_remote = """
SELECT work_from_home, COUNT(*) as count
FROM jobs
GROUP BY work_from_home;
"""

cursor.execute(query_remote)

results = cursor.fetchall()

print("\nRemote vs Onsite Jobs:")
for row in results:
    print(row)

# ================= SKILL ANALYSIS ================= #

# Extract skills
all_skills = []

for skills in df['description_tokens']:
    all_skills.extend(skills)

# Count skills
skill_count = Counter(all_skills)
top_skills = skill_count.most_common(10)

print("\nTop Skills:", top_skills)

# ================= VISUALIZATION ================= #

skills = [item[0] for item in top_skills]
counts = [item[1] for item in top_skills]

plt.figure()
plt.bar(skills, counts)

plt.xlabel("Skills")
plt.ylabel("Demand Count")
plt.title("Top 10 In-Demand Skills")
plt.xticks(rotation=45)

plt.show()


df.to_csv('final_jobs_data.csv', index=False)
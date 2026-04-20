import sqlite3

conn = sqlite3.connect("cctv.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM events")
cursor.execute("DELETE FROM plates")
cursor.execute("DELETE FROM alerts")

conn.commit()
conn.close()

print("✅ Database cleared (records only)")

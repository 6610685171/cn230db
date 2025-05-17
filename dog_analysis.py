import requests
import sqlite3

# 1. ดึงข้อมูลจาก TheDogAPI
url = 'https://api.thedogapi.com/v1/breeds'
response = requests.get(url)
data = response.json()

# 2. เชื่อมต่อ SQLite
conn = sqlite3.connect('dogs.db')
cursor = conn.cursor()

# 3. สร้างตาราง breeds
cursor.execute('''
CREATE TABLE IF NOT EXISTS breeds (
    breed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    breed_name TEXT,
    breed_group TEXT,
    life_expectancy INTEGER,
    origin TEXT,
    weight_range TEXT,
    height_range TEXT,
    temperament TEXT
)
''')

# 4. ลบข้อมูลเก่า (ถ้ามี) แล้วเพิ่มข้อมูลใหม่
cursor.execute("DELETE FROM breeds")
for breed in data:
    breed_name = breed.get('name', '')
    breed_group = breed.get('breed_group', '')
    life_expectancy = None
    if 'life_span' in breed and breed['life_span']:
        try:
            life_expectancy = int(breed['life_span'].split(' ')[0])
        except:
            pass
    origin = breed.get('origin', '')
    weight_range = breed.get('weight', {}).get('imperial', '')
    height_range = breed.get('height', {}).get('imperial', '')
    temperament = breed.get('temperament', '')

    cursor.execute('''
        INSERT INTO breeds (breed_name, breed_group, life_expectancy, origin,
                            weight_range, height_range, temperament)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (breed_name, breed_group, life_expectancy, origin, weight_range, height_range, temperament))

conn.commit()

# -----------------------------------------
# 5. การวิเคราะห์ข้อมูล
# -----------------------------------------
print("การวิเคราะห์ข้อมูลพันธุ์สุนัขจาก TheDogAPI")

# ------------------------------------------------------
# 🔸 หมวดน้ำหนัก (Weight Analysis)
# ------------------------------------------------------
print("\n🔸 หมวดน้ำหนัก (Weight Analysis)")

# 5.1 พันธุ์สุนัขที่น้ำหนักเฉลี่ยมากที่สุด
print("\n🐶 พันธุ์สุนัขที่น้ำหนักเฉลี่ยมากที่สุด:")
cursor.execute('''
SELECT breed_name, weight_range,
    (CAST(substr(weight_range, 1, instr(weight_range, '-') - 1) AS FLOAT) +
     CAST(substr(weight_range, instr(weight_range, '-') + 1) AS FLOAT)) / 2 AS avg_weight
FROM breeds
WHERE weight_range LIKE '%-%'
GROUP BY breed_name
ORDER BY avg_weight DESC
LIMIT 5;
''')
for row in cursor.fetchall():
    print(f"- {row[0]}: น้ำหนักเฉลี่ย {row[2]:.1f} ปอนด์")

# 5.2 พันธุ์สุนัขที่น้ำหนักเฉลี่ยน้อยที่สุด
print("\n🐶 พันธุ์สุนัขที่น้ำหนักเฉลี่ยน้อยที่สุด:")
cursor.execute('''
SELECT breed_name, weight_range,
    (CAST(substr(weight_range, 1, instr(weight_range, '-') - 1) AS FLOAT) +
     CAST(substr(weight_range, instr(weight_range, '-') + 1) AS FLOAT)) / 2 AS avg_weight
FROM breeds
WHERE weight_range LIKE '%-%'
GROUP BY breed_name
ORDER BY avg_weight ASC
LIMIT 5;
''')
for row in cursor.fetchall():
    print(f"- {row[0]}: น้ำหนักเฉลี่ย {row[2]:.1f} ปอนด์")

# 5.3 จัดกลุ่มสุนัขตามขนาด
print("\n📊 การจัดกลุ่มพันธุ์สุนัขตามน้ำหนัก (Small → Medium → Large):")
cursor.execute('''
SELECT breed_name, weight_range,
    CASE
        WHEN ((CAST(substr(weight_range, 1, instr(weight_range, '-') - 1) AS FLOAT) +
               CAST(substr(weight_range, instr(weight_range, '-') + 1) AS FLOAT)) / 2) < 20 THEN 'ขนาดเล็ก (Small)'
        WHEN ((CAST(substr(weight_range, 1, instr(weight_range, '-') - 1) AS FLOAT) +
               CAST(substr(weight_range, instr(weight_range, '-') + 1) AS FLOAT)) / 2) < 50 THEN 'ขนาดกลาง (Medium)'
        ELSE 'ขนาดใหญ่ (Large)'
    END AS size_category
FROM breeds
WHERE weight_range LIKE '%-%'
GROUP BY breed_name
ORDER BY
    CASE
        WHEN ((CAST(substr(weight_range, 1, instr(weight_range, '-') - 1) AS FLOAT) +
               CAST(substr(weight_range, instr(weight_range, '-') + 1) AS FLOAT)) / 2) < 20 THEN 1
        WHEN ((CAST(substr(weight_range, 1, instr(weight_range, '-') - 1) AS FLOAT) +
               CAST(substr(weight_range, instr(weight_range, '-') + 1) AS FLOAT)) / 2) < 50 THEN 2
        ELSE 3
    END, breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]}: อยู่ในกลุ่ม {row[2]}")

# ------------------------------------------------------
# 🔸 หมวดอายุขัย (Life Expectancy)
# ------------------------------------------------------
print("\n🔸 หมวดอายุขัย (Life Expectancy)")

# 5.4 พันธุ์สุนัขที่มีอายุเฉลี่ยต่ำสุด
print("\n📉 พันธุ์สุนัขที่มีอายุเฉลี่ยต่ำสุด:")
cursor.execute('''
SELECT breed_name, life_expectancy
FROM breeds
WHERE life_expectancy IS NOT NULL
ORDER BY life_expectancy
LIMIT 5;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} : อายุเฉลี่ย {row[1]:.1f} ปี")

# 5.5 พันธุ์สุนัขที่มีอายุเฉลี่ยสูงสุด
print("\n⏳ พันธุ์สุนัขที่มีอายุเฉลี่ยสูงสุด:")
cursor.execute('''
SELECT breed_name, life_expectancy
FROM breeds
WHERE life_expectancy IS NOT NULL
ORDER BY life_expectancy DESC
LIMIT 5;
''')
for row in cursor.fetchall():
    print(f"- {row[0] or 'ไม่ระบุ'} : อายุเฉลี่ย {row[1]:.1f} ปี")

# 5.6 พันธุ์สุนัขที่มีอายุเฉลี่ยมากกว่า 12 ปี
print("\n📈 พันธุ์สุนัขที่มีอายุเฉลี่ยมากกว่า 12 ปี:")
cursor.execute('''
SELECT breed_name, life_expectancy
FROM breeds
WHERE life_expectancy > 12
ORDER BY life_expectancy DESC;
''')
for row in cursor.fetchall():
    print(f"- {row[0]}: อายุเฉลี่ย {row[1]} ปี")

# ------------------------------------------------------
# 🔸 หมวดนิสัย (Temperament-based Analysis)
# ------------------------------------------------------
print("\n🔸 หมวดนิสัย (Temperament-based Analysis)")

# 5.7 สุนัขที่ฉลาดและต้องการความท้าทาย
print("\n1️⃣ สุนัขที่ฉลาดและต้องการความท้าทาย:")
cursor.execute('''
    SELECT breed_name, temperament
    FROM breeds
    WHERE temperament LIKE '%Intelligent%' OR temperament LIKE '%Alert%' OR temperament LIKE '%Responsive%'
    ORDER BY breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} อุปนิสัย: {row[1]}")
# print("\n1️⃣ สุนัขที่ฉลาดและตอบสนองดี:")
# for dog in cursor.fetchall():
#     print(f"🐶 {dog[0]}")


# 5.8 สุนัขที่มีพลังงานสูง
print("\n2️⃣ สุนัขที่มีพลังงานสูง:")
cursor.execute('''
    SELECT breed_name, temperament
    FROM breeds
    WHERE temperament LIKE '%Energetic%' OR temperament LIKE '%Active%' OR temperament LIKE '%High-spirited%'
    ORDER BY breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} อุปนิสัย: {row[1]}")

# 5.9 สุนัขที่เหมาะกับชีวิตในเมืองและคอนโด
print("\n3️⃣ สุนัขที่เหมาะกับชีวิตในเมืองและคอนโด:")
cursor.execute('''
    SELECT breed_name, weight_range, temperament
    FROM breeds
    WHERE (temperament LIKE '%Calm%' OR temperament LIKE '%Quiet%' OR temperament LIKE '%Docile%')
    AND (
        CASE
            WHEN INSTR(weight_range, '-') > 0
            THEN CAST(SUBSTR(weight_range, 1, INSTR(weight_range, '-') - 1) AS INT)
            ELSE NULL
        END
    ) < 20
    ORDER BY breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} น้ำหนัก {row[1]} ปอนด์ อุปนิสัย: {row[2]}")

# 5.10 สุนัขที่อารมณ์ดีและเหมาะกับครอบครัว
print("\n4️⃣ สุนัขที่อารมณ์ดีและเหมาะกับครอบครัว:")
cursor.execute('''
    SELECT breed_name, temperament
    FROM breeds
    WHERE temperament LIKE '%Friendly%' OR temperament LIKE '%Gentle%' OR temperament LIKE '%Affectionate%' OR temperament LIKE '%Loving%'
    ORDER BY breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} อุปนิสัย: {row[1]}")

# 5.11 สุนัขที่ดูแลไม่ยุ่งยากและไม่ต้องการกิจกรรมมาก
print("\n5️⃣ สุนัขที่ดูแลไม่ยุ่งยากและไม่ต้องการกิจกรรมมาก:")
cursor.execute('''
    SELECT breed_name, temperament
    FROM breeds
    WHERE temperament LIKE '%Easygoing%' OR temperament LIKE '%Adaptable%' OR temperament LIKE '%Lazy%'
    ORDER BY breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} อุปนิสัย: {row[1]}")

# 5.12 สุนัขที่ขี้เล่นและเป็นมิตรกับทุกคน
print("\n6️⃣ สุนัขที่ขี้เล่นและเป็นมิตรกับทุกคน:")
cursor.execute('''
    SELECT breed_name, temperament
    FROM breeds
    WHERE temperament LIKE '%Playful%' OR temperament LIKE '%Sociable%' OR temperament LIKE '%Extroverted%'
    ORDER BY breed_name;
''')
for row in cursor.fetchall():
    print(f"- {row[0]} อุปนิสัย: {row[1]}")

# 6. ปิดการเชื่อมต่อฐานข้อมูล
conn.close()
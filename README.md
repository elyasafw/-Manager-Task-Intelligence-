# Intelligence Task Manager

### תיאור המערכת:  
**מערכת ניהול משימות סוכנים מנוהלת בבסיס נתונים MySQL עם טבלאות:**  
**1. agents**  
**2. missions**  

**המערכת אחראית על ניהול חלוקת המשימות לפי רמת הסוכן עם ניהול מלא של עדכון סוכנים ומשימות שינויי סטטוס משימה ואינדיקציות מלאות בזמן אמת.**  

## מבנה תיקיות:  
```text
intelligence-task-manager/
├── database/
│   ├── db_connection.py
│   ├── agent_db.py
│   └── mission_db.py
├── README.md
├── requirements.txt
└── .gitignore
```

## מבנה טבלאות הנתונים:  
### טבלת agents:  
id | name | specialty | is_active | completed_missions | failed_missions | agent_rank
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
INT PK AUTO_INCREMENT | VARCHAR(50) | VARCHAR(50) | BOOLEAN DEFAULT TRUE | INT DEFAULT 0 | INT DEFAULT 0 | ENUM(Junior / Senior / Commander)  

### טבלת missions:  
id | title | description | location | difficulty | importance | status | risk_level | assigned_agent_id
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
INT PK AUTO_INCREMENT | VARCHAR(100) | TEXT | VARCHAR(50) | INT CHECK(difficulty BETWEEN 1 AND 10) | INT CHECK(difficulty BETWEEN 1 AND 10) | VARCHAR(30) DEFAULT NEW | VARCHAR(30) | INT DEFAULT NULL  

## חוקי המערכת:  
1.	שדה rank חייב להיות Junior / Senior / Commander — כל ערך אחר זורק שגיאה.
2.	שדות difficulty ו-importance חייבים להיות בין 1 ל-10 — אחרת שגיאה.
3.	שדה risk_level מחושב אוטומטית בעת יצירת משימה — המשתמש לא שולח אותו.
4.	סוכן עם is_active=False לא יכול לקבל משימות.
5.	סוכן לא יכול להחזיק יותר מ-3 משימות פתוחות (ASSIGNED / IN_PROGRESS) במקביל.
6.	אם risk_level=CRITICAL — רק סוכן בדרגת Commander יכול לקבל את המשימה.
7.	ניתן לשייך רק משימה בסטטוס NEW. לאחר שיוך: status=ASSIGNED.
8.	ניתן להתחיל רק משימה בסטטוס ASSIGNED. לאחר: status=IN_PROGRESS.
9.	ניתן לסיים רק משימה. IN_PROGRESS  ולשנות לסטטוס failed or completed
10.	ניתן לבטל רק משימה בסטטוס NEW או ASSIGNED — אחרת שגיאה.

## מחלקות  
### מחלקת DB_connection:  
**מחלקה המנהלת את יצירת החיבור לשרת ה SQL ואת היצירה והחיבור למסד הנתונים והטבלאות**  
תפקיד | מתודה
| :---: | :---: |
get_connection() | מחזירה חיבור פעיל ל MySQL
create_database() |	יוצרת את Intelligence_db אם לא קיים
create_tables() | יוצרת את שתי הטבלאות אם לא קיימות

### מחלקת AgentDB:  
**מחלקה האחראית על כל פעולות SQL מול טבלת agents**  
תפקיד | מתודה
| :---: | :---: |
create_agent(data) | יוצרת סוכן חדש ומחזירה את האובייקט של הסוכן
get_all_agents() | מחזירה רשימת כל הסוכנים
get_agent_by_id(id)	| מחזירה סוכן אחד לפי ID, או None
update_agent(id, data) | UPDATE לכל השורה (אין אפשרות לשנות id)
deactivate_agent(id) | מגדירה מצב סוכן ללא פעיל
increment_completed(id) | מעדכן את כמות המשימות שהושלמו 
increment_failed(id) | מעדכן את כמות המשימות שנכשלו
get_agent_performance(id) | מחזירה מילון עם המפתחות: completed, failed, total, success_rate
count_active_agents() | מחזירה את מספר הסוכנים הפעילים 

### מחלקת MissionDB:  
**מחלקה האחראית על כל פעולות SQL מול טבלת missions**  
תפקיד | מתודה
| :---: | :---: |
מתודה	תפקיד
create_mission(data) | יצירת משימה חדשה ומחזירה את כל האובייקט
get_all_missions() | מחזירה את כל המשימות
get_mission_by_id(id) | מחזירה משימה אחת לפי ID, או None
assign_mission(m_id, a_id) | משייכת משימה לסוכן
update_mission_status(id, status) | משמשת לכל שינוי סטטוס
get_open_missions_by_agent(id) | מחזירה משימות ASSIGNED/IN_PROGRESS של סוכן
count_all_missions() | סה"כ משימות
count_by_status(status) | סופרת לפי סטטוס מסוים
count_open_missions() | סופרת משימות פתוחות
count_critical_missions() | סופרת משימות CRITICAL
get_top_agent() | הסוכן עם completed_missions הגבוה ביותר  

## הוראות התקנה והרצה  

### התקנה:  
**יצירת קונטיינר Docker ומסד נתונים ב SQL**  
```bash
    docker run -d --name intelligence-mysql -e MYSQL_ROOT_PASSWORD=1234 \
    -e MYSQL_DATABASE=Intelligence_db -p 3306:3306 mysql:8.0
```
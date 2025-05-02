from pysqlcipher3 import dbapi2 as sqlcipher
import time
import uuid
import os
import data

db = None
DB_PATH = os.path.join(data.DATA_DIR, "meti.db")

def databaseExists():
    return os.path.isfile(DB_PATH)

def createDatabase(password):
    global db
    db = sqlcipher.connect(DB_PATH)
    db.row_factory = dictFactory
    db.execute(f"pragma key='{password}'")
    db.execute("pragma foreign_keys = ON")
    with open(os.path.join(data.DATA_DIR, "schema.sql")) as schema:
        db.executescript(schema.read())
    return True

def dictFactory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def decryptDatabase(password):
    global db
    if not db:
        db = sqlcipher.connect(DB_PATH)
        db.row_factory = dictFactory
    try:
        db.execute(f"pragma key='{password}'")
        getProjects()
        return True
    except BaseException as x:
        print(x)
        return False

def createProject(name, is_template):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into projects values (?, ?, ?, ?)', (id, name, is_template, int(time.time())))
    db.commit()
    return id

def getProjects():
    global db
    return db.execute('select * from projects order by last_accessed desc ;').fetchall()

def getLastAccessedProject():
    global db
    return db.execute('select * from projects order by last_accessed desc limit 1;').fetchone()

def updateLastAccessedProject(id):
    global db
    db.execute('update projects set last_accessed = ? where id = ?', (int(time.time()),id))
    db.commit()

def getProjectChecklists(project_id):
    global db
    checklists = db.execute('select * from checklists where project_id = ?', (project_id,)).fetchall()
    for checklist in checklists:
        checklist["checks"] = getChecks(checklist["template_id"])
        checklist["title"] = getChecklistTemplate(checklist["template_id"])["title"]

    return checklists

def getChecks(template_id):
    global db
    return db.execute('select content, position from checks where template_id = ? order by position', (template_id,)).fetchall()

def getChecklistTemplate(id):
    global db
    return db.execute('select * from checklist_templates where id = ?', (id,)).fetchone()

def createChecklistTemplate(title):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into checklist_templates values (?, ?)', (id, title))
    db.commit()
    return id

def createCheck(template_id, content, position):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into checks values (?, ?, ?, ?)', (id, template_id, content, position))
    db.commit()
    return id

def createChecklist(checklist):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into checklists values (?, ?, ?, ?, ?, ?, ?)', (id, checklist["template_id"], checklist["project_id"], checklist["parent_id"], checklist["state"], checklist["position_x"], checklist["position_y"]))
    db.commit()
    return id


def updateChecklist(checklist):
    global db
    db.execute('update checklists set template_id = ?, project_id = ?, parent = ?, state = ?, position_x = ?, position_y = ? where id = ?', (checklist["template_id"], checklist["project_id"], checklist["parent_id"], checklist["state"], checklist["position_x"], checklist["position_y"], id))
    db.commit()

def updateChecklistState(id, state):
    global db
    db.execute('update checklists set state = ? where id = ?', (state, id))
    db.commit()

def updateChecklistPosition(id, new_x, new_y):
    global db
    db.execute('update checklists set position_x = ?, position_y = ? where id = ?', (new_x, new_y, id))
    db.commit()

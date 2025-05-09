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
        return False

def createProject(title, is_template):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into projects values (?, ?, ?, ?, ?, ?, ?)', (id, title, is_template, int(time.time()), None, None, False))
    db.commit()
    return id

def getProjects():
    global db
    return db.execute('select * from projects where is_template != true order by last_accessed desc;').fetchall()

def getLastAccessedProject():
    global db
    return db.execute('select * from projects order by last_accessed desc limit 1;').fetchone()

def updateLastAccessedProject(id):
    global db
    db.execute('update projects set last_accessed = ? where id = ?', (int(time.time()),id))
    db.commit()

def updateProjectView(id, x, y):
    global db
    db.execute('update projects set view_x = ?, view_y = ? where id = ?', (x, y, id))
    db.commit()

def updateProjectZoomedOut(id, zoomed_out):
    global db
    db.execute('update projects set zoomed_out = ? where id = ?', (zoomed_out, id))
    db.commit()

def getProjectChecklists(project_id):
    global db
    checklists = db.execute('select * from checklists where project_id = ?', (project_id,)).fetchall()
    for checklist in checklists:
        checklist["checks"] = getChecks(checklist["id"])

    return checklists

def getProjectTemplates():
    global db
    return db.execute('select * from projects where is_template = true order by last_accessed desc;').fetchall()

def getChecklistTemplates():
    global db
    templates = db.execute('select * from checklist_templates').fetchall()
    for template in templates:
        template["checks"] = getTemplateChecks(template["id"])

    return templates

def getChecklistTemplate(id):
    global db
    return db.execute('select * from checklist_templates where id = ?', (id,)).fetchone()

def createChecklistTemplate(title):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into checklist_templates values (?, ?)', (id, title))
    db.commit()
    return id

def getChecklist(id):
    global db
    return db.execute('select * from checklists where id = ?', (id,)).fetchone()

def createChecklist(checklist):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into checklists values (?, ?, ?, ?, ?, ?, ?)', (id, checklist["template_id"], checklist["project_id"], checklist["parent_id"], checklist["title"], checklist["position_x"], checklist["position_y"]))
    db.commit()
    return id

def updateChecklist(checklist):
    global db
    db.execute('update checklists set template_id = ?, project_id = ?, parent_id = ?, title = ?, position_x = ?, position_y = ? where id = ?', (checklist["template_id"], checklist["project_id"], checklist["parent_id"], checklist["title"], checklist["position_x"], checklist["position_y"], id))
    db.commit()

def updateChecklistPosition(id, new_x, new_y):
    global db
    db.execute('update checklists set position_x = ?, position_y = ? where id = ?', (new_x, new_y, id))
    db.commit()

def updateChecklistTitle(id, title):
    global db
    db.execute('update checklists set title = ? where id = ?', (title, id))
    db.commit()

def setTemplateForChecklist(id, template_id):
    global db
    db.execute('update checklists set template_id = ? where id = ?', (template_id, id))
    db.commit()

def deleteChecklist(id):
    global db
    db.execute('delete from checklists where id = ?', (id,))
    db.execute('delete from checks where checklist_id = ?', (id,))
    db.commit()

def getChecks(checklist_id):
    global db
    return db.execute('select * from checks where checklist_id = ? order by position', (checklist_id,)).fetchall()

def updateCheckState(id, state):
    global db
    db.execute('update checks set state = ? where id = ?', (state, id))
    db.commit()

def createCheck(checklist_id, content, state, position):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into checks values (?, ?, ?, ?, ?)', (id, checklist_id, content, state, position))
    db.commit()
    return id

def updateCheck(id, content, state, position):
    global db
    db.execute('update checks set content = ?, state = ?, position = ? where id = ?', (content, state, position, id))
    db.commit()
    return id

def deleteCheck(id):
    global db
    db.execute('delete from checks where id = ?', (id,))
    db.commit()

def createTemplateCheck(template_id, content, position):
    global db
    id = str(uuid.uuid4())
    db.execute('insert into template_checks values (?, ?, ?, ?)', (id, template_id, content, position))
    db.commit()
    return id

def getTemplateChecks(template_id):
    global db
    return db.execute('select * from template_checks where template_id = ? order by position', (template_id,)).fetchall()

def updateTemplateChecklist(id, title):
    global db
    db.execute('update checklist_templates set title = ? where id = ?', (title, id))
    db.commit()

def updateTemplateCheck(id, content, position):
    global db
    db.execute('update template_checks set content = ?, position = ? where id = ?', (content, position, id))
    db.commit()
    return id

def deleteTemplateCheck(id):
    global db
    db.execute('delete from template_checks where id = ?', (id,))
    db.commit()

def deleteTemplateChecks(template_id):
    global db
    db.execute('delete from template_checks where template_id = ?', (template_id,))
    db.commit()

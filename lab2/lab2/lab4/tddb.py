# -*- coding: utf-8 -*-

import psycopg2 as db

import telephonedir

def createConn():
  conn = db.connect(host='localhost', database="telephonedir1", user="postgres")
  db.threadsafety=2
  curs = conn.cursor()
  return (db, conn, curs)

def closeConn(db, conn, curs):
  conn.close()

def save(telephoneDir):
  db, conn, curs = createConn()

  sql1 = "INSERT INTO Подразделения VALUES (DEFAULT, %s, %s) RETURNING кодПодразделения"
  sql2 = "INSERT INTO Сотрудники VALUES (%s, %s, %s, %s, %s) RETURNING кодСотрудника"
  subdivisions, collaborators = {}, {}
  def insert(subdivision, key):
    curs.execute(sql1, (subdivision.name, key))
    key = curs.fetchone()[0]
    for c in subdivision.collaborators:
      curs.execute(sql2, (c.code, key, c.family, c.name, c.patronym))
      collaborators[c] = curs.fetchone()[0]
    for s in subdivision.subdivisions:
      insert(s, key)

  try:
    insert(telephoneDir.subdivision, None)
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  sql = "INSERT INTO ТелефоновТипы VALUES (DEFAULT, %s) RETURNING кодТелефонаТип"
  telephoneTypes = {}
  try:
    for t in telephoneDir.telephones.telephoneTypes:
      curs.execute(sql, (t.name,))
      telephoneTypes[t] = curs.fetchone()[0]
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  sql = "INSERT INTO Телефоны VALUES (DEFAULT, %s, %s) RETURNING кодТелефона"
  telephones = {}
  try:
    for t in telephoneDir.telephones:
      curs.execute(sql, (telephoneTypes[t.type], t.number))
      telephones[t] = curs.fetchone()[0]
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  sql = "INSERT INTO ТелефонныйСправочник VALUES (DEFAULT, %s, %s)"
  try:
    for r in telephoneDir:
      curs.execute(sql, (telephones[r.telephone], collaborators[r.collaborator]))
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  closeConn(db, conn, curs)

def load():
  db, conn, curs = createConn()

  sql = """
SELECT
  кодПодразделения,
  название,
  кодГоловногоПодраз
FROM
  Подразделения"""
  subdivisions, subdivisionOwners = {}, {}
  try:
    curs.execute(sql)
    for rec in curs.fetchall():
      s = telephonedir.Subdivision(rec[1])
      subdivisions[rec[0]] = s
      subdivisionOwners[s] = rec[2]
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()
  for s, i in subdivisionOwners.iteritems():
    if i:
      subdivisions[i].subdivisions.add(s)
    else:
      subdivision = s

  sql = """
SELECT
  кодСотрудника,
  кодПодразделения,
  фамилия,
  имя,
  отчество
FROM
  Сотрудники"""
  collaborators = {}
  try:
    curs.execute(sql)
    for rec in curs.fetchall():
      c = telephonedir.Collaborator(rec[0], rec[2], rec[3], rec[4])
      collaborators[rec[0]] = c
      subdivisions[rec[1]].add(c)
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  sql = """
SELECT
  кодТелефонаТип,
  название
FROM
  ТелефоновТипы"""
  telephoneTypes = {}
  try:
    curs.execute(sql)
    for rec in curs.fetchall():
      telephoneTypes[rec[0]] = telephonedir.TelephoneType(rec[1])
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  sql = """
SELECT
  кодТелефона,
  кодТелефонаТип,
  номер
FROM
  Телефоны"""
  telephones = {}
  try:
    curs.execute(sql)
    for rec in curs.fetchall():
      telephones[rec[0]] = telephonedir.Telephone(rec[2], telephoneTypes[rec[1]])
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  telephoneDir = telephonedir.TelephoneDir(telephonedir.Telephones(telephonedir.TelephoneTypes()), subdivision)
  for t in telephoneTypes.itervalues():
    telephoneDir.telephones.telephoneTypes.add(t)
  for t in telephones.itervalues():
    telephoneDir.telephones.add(t)

  sql = """
SELECT
  кодТелефона,
  кодСотрудника
FROM
  ТелефонныйСправочник"""
  try:
    curs.execute(sql)
    for rec in curs.fetchall():
      telephoneDir.add(telephonedir.TelephoneRecord(telephones[rec[0]], collaborators[rec[1]]))
  except db.DatabaseError, x:
    print x
    conn.rollback()
  else:
    conn.commit()

  closeConn(db, conn, curs)

  return telephoneDir

if __name__ == '__main__':
  telephoneDir = load()

  for s in telephoneDir.subdivision.iterSubdivision():
    if s.name == 'помощник проректора':
      for r in telephoneDir:
        if r.collaborator in s and r.collaborator.family.find('ск') >= 0:
          print r.telephone.number, "%s %s. %s."% \
                (r.collaborator.family, r.collaborator.name[:2], r.collaborator.patronym[:2])
      break

  for s in telephoneDir.subdivision.iterSubdivision():
    if s.name == 'зав. кафедрой':
      for r in telephoneDir:
        if r.collaborator in s and r.collaborator.family.find('сс') >= 0:
          print r.telephone.number, "%s %s. %s."% \
                (r.collaborator.family, r.collaborator.name[:2], r.collaborator.patronym[:2])
      break

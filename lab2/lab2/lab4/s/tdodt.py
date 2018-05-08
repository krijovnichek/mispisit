# -*- coding: utf-8 -*-

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

def save(telephoneDir, subdivision=0, collaborator=None, number=None, telephoneType=None):
  collaborators = list(sorted(telephoneDir.subdivision))
  subdivisions = list(sorted(telephoneDir.subdivision.iterSubdivision()))
  telephoneTypes = list(sorted(telephoneDir.telephones.telephoneTypes))

  s = subdivisions[subdivision]
  lambdaSubdivision = lambda rec: rec.collaborator in s

  if not collaborator:
    lambdaCollaborator = lambda rec: True
  else:
    l = len(collaborator)
    lambdaCollaborator = lambda rec: str(rec.collaborator)[0:l] == collaborator

  if not number:
    lambdaNumber = lambda rec: True
  else:
    l = len(number)
    lambdaNumber = lambda rec: str(rec.telephone.number)[0:l] == number

  if not telephoneType:
    lambdaTelephoneType = lambda rec: True
  else:
    t = telephoneTypes[telephoneType]
    lambdaTelephoneType = lambda rec: rec.telephone.type == t

    root = Template(file=os.path.join(os.curdir, 'index.tmpl'))

  telephoneDir = filter(lambda telephone: lambdaSubdivision(telephone) and \
                                          lambdaCollaborator(telephone) and \
                                          lambdaNumber(telephone) and \
                                          lambdaTelephoneType(telephone), sorted(telephoneDir))

  textdoc = OpenDocumentText()

  tablecontents = Style(name="Table Contents", family="paragraph")
  tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
  textdoc.styles.addElement(tablecontents)

  textdoc.text.addElement(P(stylename=tablecontents,text=s.name.decode("utf-8")))

  style2 = Style(name="style2", family="table-column")
  style2.addElement(TableColumnProperties(columnwidth="2cm"))
  textdoc.automaticstyles.addElement(style2)

  table = Table(name=u"Телефонный справочник")
  table.addElement(TableColumn(numbercolumnsrepeated=3,stylename=style2))

  def row(rec):
    tr = TableRow()
    table.addElement(tr)
    for r in rec:
      tc = TableCell()
      tr.addElement(tc)
      p = P(stylename=tablecontents,text=r)
      tc.addElement(p)

  for rec in telephoneDir:
    row((str(rec.collaborator).decode("utf-8"), rec.telephone.number, rec.telephone.type.name.decode("utf-8")))

  textdoc.text.addElement(table)
  textdoc.save("telephonedir.odt")

if __name__ == '__main__':
  import tdcsv

  telephoneDir = tdcsv.load()
  save(telephoneDir, collaborator="М", subdivision=2)

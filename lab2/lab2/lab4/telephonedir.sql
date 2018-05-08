CREATE TABLE Подразделения (
  кодПодразделения   SERIAL PRIMARY KEY,
  название           TEXT,
  кодГоловногоПодраз INTEGER REFERENCES Подразделения(кодПодразделения) DEFAULT NULL,
  UNIQUE(название, кодГоловногоПодраз)
);

CREATE TABLE Сотрудники (
  кодСотрудника    INTEGER PRIMARY KEY,
  кодПодразделения INTEGER REFERENCES Подразделения(кодПодразделения) DEFAULT NULL,
  фамилия          TEXT,
  имя              TEXT,
  отчество         TEXT
);

CREATE TABLE ТелефоновТипы (
  кодТелефонаТип SERIAL PRIMARY KEY,
  название       TEXT,
  UNIQUE(название)
);

CREATE TABLE Телефоны (
  кодТелефона    SERIAL PRIMARY KEY ,
  кодТелефонаТип INTEGER REFERENCES ТелефоновТипы(кодТелефонаТип),
  номер          TEXT
);

CREATE TABLE ТелефонныйСправочник (
  кодЗаписи     SERIAL PRIMARY KEY,
  кодТелефона   INTEGER REFERENCES Телефоны(кодТелефона),
  кодСотрудника INTEGER REFERENCES Сотрудники(кодСотрудника),
  UNIQUE(кодТелефона, кодСотрудника)
);

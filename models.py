import base64
from typing import Optional, List
# from bcrypt import hashpw, gensalt, checkpw
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Column, Time, Date, ForeignKey, Integer, Text, func, and_
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
# from pandas import date_range
from views import app
import os

# app.config["SQLALCHEMY_DATABASE_URI"] = (
#         f"postgresql://{os.getenv('postgres')}:{os.getenv('postgres')}@{os.getenv('db:5432')}/{os.getenv('TRBD')}"
#     )
app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:postgres@localhost:5432/TRBD"
    )

db = SQLAlchemy()

class City(db.Model):
    __tablename__ = 'City'
    __table_args__ = {'schema': 'public'}

    ID_City = Column(Integer, primary_key=True, default=1)
    City = Column(Text, nullable=False)


class Park(db.Model):
    __tablename__ = 'Park'
    __table_args__ = {'schema': 'public'}

    ID_Park = Column(Integer, primary_key=True)
    ID_City = Column(Integer, ForeignKey('public.City.ID_City'))
    Street = Column(Text, nullable=False)
    House_Number = Column(Integer, nullable=False)
    Start_Time = Column(Time, nullable=False)
    End_Time = Column(Time, nullable=False)
    city = relationship('City', backref='parks')


class Employee(db.Model):
    __tablename__ = 'Employee'
    __table_args__ = {'schema': 'public'}

    ID_Employee = Column(Integer, primary_key=True)
    ID_Park = Column(Integer, ForeignKey('public.Park.ID_Park'))
    Emp_Surname = Column(Text, nullable=False)
    Emp_Name = Column(Text, nullable=False)
    Emp_Patr = Column(Text)
    Passport = Column(Text, nullable=False)
    INN = Column(BigInteger, nullable=False)
    park = relationship('Park', backref='employees')


class Fuel_Type(db.Model):
    __tablename__ = 'Fuel_Type'
    __table_args__ = {'schema': 'public'}

    ID_Fuel = Column(Integer, primary_key=True)
    Fuel = Column(Text, nullable=False)


class Transmission(db.Model):
    __tablename__ = 'Transmission'
    __table_args__ = {'schema': 'public'}

    ID_Transm = Column(Integer, primary_key=True)
    Transm = Column(Text, nullable=False)


class Brand(db.Model):
    __tablename__ = 'Brand'
    __table_args__ = {'schema': 'public'}

    ID_Brand = Column(db.Integer, primary_key=True)
    Brand = Column(db.String(100), nullable=False)


class Model(db.Model):
    __tablename__ = 'Model'
    __table_args__ = {'schema': 'public'}

    ID_Model = Column(Integer, primary_key=True)
    Model = Column(Text, nullable=False)
    ID_Brand = Column(Integer, ForeignKey('public.Brand.ID_Brand'))
    brand = relationship('Brand', backref='models')


class Auto(db.Model):
    __tablename__ = 'Auto'
    __table_args__ = {'schema': 'public'}

    ID_Auto = Column(Integer, primary_key=True)
    ID_Brand = Column(Integer, ForeignKey('public.Brand.ID_Brand'))
    ID_Model = Column(Integer, ForeignKey('public.Model.ID_Model'))
    ID_Fuel = Column(Integer, ForeignKey('public.Fuel_Type.ID_Fuel'))
    ID_Transm = Column(Integer, ForeignKey('public.Transmission.ID_Transm'))
    ID_Park = Column(Integer, ForeignKey('public.Park.ID_Park'))
    Rent_Price = Column(Integer, nullable=False)
    Year = Column(Integer, nullable=False)
    Fuel_Consumption = Column(Integer, nullable=False)
    brand = relationship('Brand', backref='autos')
    model = relationship('Model', backref='autos')
    fuel_type = relationship('Fuel_Type', backref='autos')
    transmission = relationship('Transmission', backref='autos')
    park = relationship('Park', backref='autos')


class Client(db.Model):
    __tablename__ = 'Client'
    __table_args__ = {'schema': 'public'}

    ID_Client = Column(Integer, primary_key=True)
    Cli_Surn = Column(Text, nullable=False)
    Cli_Name = Column(Text, nullable=False)
    Cli_Patr = Column(Text, nullable=False)
    License = Column(Text, nullable=False)
    Expirience = Column(Integer, nullable=False)
    Phone_Number = Column(Text, nullable=False)
    Date_of_Birth = Column(Date, nullable=False)


class Rent_Status(db.Model):
    __tablename__ = 'Rent_Status'
    __table_args__ = {'schema': 'public'}

    ID_Status = Column(Integer, primary_key=True)
    Status = Column(Text, nullable=False)


class Rent(db.Model):
    __tablename__ = 'Rent'
    __table_args__ = {'schema': 'public'}

    ID_Rent = Column(Integer, primary_key=True)
    ID_Client = Column(Integer, ForeignKey('public.Client.ID_Client'))
    ID_Employee = Column(Integer, ForeignKey('public.Employee.ID_Employee'))
    ID_Auto = Column(Integer, ForeignKey('public.Auto.ID_Auto'))
    ID_Status = Column(Integer, ForeignKey('public.Rent_Status.ID_Status'))
    Start_Date = Column(Date, nullable=False)
    End_Date = Column(Date, nullable=False)
    Rent_Price = Column(Integer, nullable=False)
    Pledge = Column(Integer, nullable=False)
    client = relationship('Client', backref='rents')
    employee = relationship('Employee', backref='rents')
    auto = relationship('Auto', backref='rents')
    status = relationship('Rent_Status', backref='rents')

def get_brands() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Brand.ID_Brand.label('№'),
            Brand.Brand.label('Марка')
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_models() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Model.ID_Model.label('№'),
            Brand.Brand.label('Марка'),
            Model.Model.label('Модель')
        ).join(Brand, Brand.ID_Brand == Model.ID_Brand)
    data_dicts = [row._asdict() for row in data]
    
    return data_dicts

def get_fuel() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Fuel_Type.ID_Fuel.label('№'),
            Fuel_Type.Fuel.label('Топливо')
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_transm() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Transmission.ID_Transm.label('№'),
            Transmission.Transm.label('Трансмиссия')
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_rentStat() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Rent_Status.ID_Status.label('№'),
            Rent_Status.Status.label('Статус')
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_city() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            City.ID_City.label('№'),
            City.City.label('Город')
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_parks() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Park.ID_Park.label('ID'),
            City.City.label('Город'),
            Park.Street.label('Улица'),
            Park.House_Number.label('Номер дома'),
            Park.Start_Time.label('Время начала работы'),
            Park.End_Time.label('Время окончания работы')
        ).join(City, Park.ID_City == City.ID_City)
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_employee() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
            Employee.ID_Employee.label('ID'),
            Employee.Emp_Surname.label('Фамилия'),
            Employee.Emp_Name.label('Имя'),
            Employee.Emp_Patr.label('Отчество'),
            Employee.Passport.label('Паспорт'),
            Employee.INN.label('ИНН'),
            City.City.label('Город парка'),
            Park.Street.label('Улица парка'),
            Park.House_Number.label('Номер дома')
        ).join(
            Park, Employee.ID_Park == Park.ID_Park
        ).join(
            City, Park.ID_City == City.ID_City
        )
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_auto() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
        Auto.ID_Auto.label('ID'),
        Brand.Brand.label('Марка'),
        Model.Model.label('Модель'),
        Fuel_Type.Fuel.label('Топливо'),
        Transmission.Transm.label('Трансмиссия'),
        Auto.Rent_Price.label('Цена аренды'),
        Auto.Year.label('Год производства'),
        City.City.label('Город парка'),
        Park.Street.label('Улица'),
        Park.House_Number.label('Номер дома'),
        Auto.Fuel_Consumption.label('Расход топлива')
    ).join(
        Park, Auto.ID_Park == Park.ID_Park
    ).join(
        City, City.ID_City == Park.ID_City
    ).join(
        Brand, Auto.ID_Brand == Brand.ID_Brand
    ).join(
        Model, Auto.ID_Model == Model.ID_Model
    ).join(
        Transmission, Auto.ID_Transm == Transmission.ID_Transm
    ).join(
        Fuel_Type, Auto.ID_Fuel == Fuel_Type.ID_Fuel
    )
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_client() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
        Client.ID_Client.label('ID'),
        Client.Cli_Surn.label('Фамилия'),
        Client.Cli_Name.label('Имя'),
        Client.Cli_Patr.label('Отчество'),
        Client.License.label('ВУ'),
        Client.Expirience.label('Стаж'),
        Client.Phone_Number.label('Номер телефона'),
        Client.Date_of_Birth.label('Дата рождения')
    )
    data_dicts = [row._asdict() for row in data]
    return data_dicts

def get_rent() -> list[dict[str, int|str]]:
    with Session(db.engine) as session:
        data = session.query(
        Rent.ID_Rent.label('ID'),
        func.coalesce(Rent.ID_Employee).label('Номер сотрудника'),
        func.coalesce(Employee.Emp_Surname).label('Фамилия сотрудника'),
        func.coalesce(Rent.ID_Client).label('Номер клиента'),
        func.coalesce(Client.Cli_Surn).label('Фамилия клиента'),
        func.coalesce(Auto.ID_Auto).label('Номер автомобиля'),
        func.coalesce(Brand.Brand).label('Марка'),
        func.coalesce(Model.Model).label('Модель'),
        Rent.Start_Date.label('Дата начала аренды'),
        Rent.End_Date.label('Дата окончания аренды'),
        Rent.Rent_Price.label('Стоимость аренды'),
        Rent.Pledge.label('Залог'),
        Rent_Status.Status.label('Статус аренды')
    ).join(
        Rent_Status, Rent.ID_Status == Rent_Status.ID_Status
    ).outerjoin(
        Employee, Rent.ID_Employee == Employee.ID_Employee
    ).outerjoin(
        Client, Rent.ID_Client == Client.ID_Client
    ).outerjoin(
        Auto, Rent.ID_Auto == Auto.ID_Auto
    ).outerjoin(
        Brand, Auto.ID_Brand == Brand.ID_Brand
    ).outerjoin(
        Model, Auto.ID_Model == Model.ID_Model
    )
    data_dicts = [row._asdict() for row in data]
    return data_dicts

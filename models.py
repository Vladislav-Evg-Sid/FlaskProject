import base64
from typing import Optional, List
# from bcrypt import hashpw, gensalt, checkpw
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Column, Time, Date, ForeignKey, Integer, Text, func, and_
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from sqlalchemy.exc import IntegrityError
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

    ID_City = Column(Integer, primary_key=True, autoincrement=True)
    City = Column(Text, nullable=False)


class Park(db.Model):
    __tablename__ = 'Park'
    __table_args__ = {'schema': 'public'}

    ID_Park = Column(Integer, primary_key=True, autoincrement=True)
    ID_City = Column(Integer, ForeignKey('public.City.ID_City'))
    Street = Column(Text, nullable=False)
    House_Number = Column(Integer, nullable=False)
    Start_Time = Column(Time, nullable=False)
    End_Time = Column(Time, nullable=False)
    city = relationship('City', backref='parks')


class Employee(db.Model):
    __tablename__ = 'Employee'
    __table_args__ = {'schema': 'public'}

    ID_Employee = Column(Integer, primary_key=True, autoincrement=True)
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

    ID_Fuel = Column(Integer, primary_key=True, autoincrement=True)
    Fuel = Column(Text, nullable=False)


class Transmission(db.Model):
    __tablename__ = 'Transmission'
    __table_args__ = {'schema': 'public'}

    ID_Transm = Column(Integer, primary_key=True, autoincrement=True)
    Transm = Column(Text, nullable=False)


class Brand(db.Model):
    __tablename__ = 'Brand'
    __table_args__ = {'schema': 'public'}

    ID_Brand = Column(Integer, primary_key=True, autoincrement=True)
    Brand = Column(db.String(100), nullable=False)


class Model(db.Model):
    __tablename__ = 'Model'
    __table_args__ = {'schema': 'public'}

    ID_Model = Column(Integer, primary_key=True, autoincrement=True)
    Model = Column(Text, nullable=False)
    ID_Brand = Column(Integer, ForeignKey('public.Brand.ID_Brand'))
    brand = relationship('Brand', backref='models')


class Auto(db.Model):
    __tablename__ = 'Auto'
    __table_args__ = {'schema': 'public'}

    ID_Auto = Column(Integer, primary_key=True, autoincrement=True)
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

    ID_Client = Column(Integer, primary_key=True, autoincrement=True)
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

    ID_Status = Column(Integer, primary_key=True, autoincrement=True)
    Status = Column(Text, nullable=False)


class Rent(db.Model):
    __tablename__ = 'Rent'
    __table_args__ = {'schema': 'public'}

    ID_Rent = Column(Integer, primary_key=True, autoincrement=True)
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


def get_rep_autoList():
    columns = ['Номер парка', 'Город', 'Улица', 'Номер дома',
               'Номер автомобиля', 'Марка', 'Модель']
    with Session(db.engine) as session:
        data = session.query(
            Park.ID_Park.label(columns[0]),
            City.City.label(columns[1]),
            Park.Street.label(columns[2]),
            Park.House_Number.label(columns[3]),
            Auto.ID_Auto.label(columns[4]),
            Brand.Brand.label(columns[5]),
            Model.Model.label(columns[6])
        ).join(
            City, Park.ID_City == City.ID_City
        ).join(
            Auto, Auto.ID_Park == Park.ID_Park
        ).join(
            Brand, Auto.ID_Brand == Brand.ID_Brand
        ).join(
            Model, Auto.ID_Model == Model.ID_Model
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_rep_rentByClient():
    columns = ["Номер клиента", "Фамилия", "Имя", "Отчество",
               "Дата начала аренды", "Дата окончания аренды",
               "Марка автомобиля", "Модель автомобиля"]
    with Session(db.engine) as session:
        data = session.query(
            Client.ID_Client.label(columns[0]),
            Client.Cli_Surn.label(columns[1]),
            Client.Cli_Name.label(columns[3]),
            Rent.Start_Date.label(columns[4]),
            Rent.End_Date.label(columns[5]),
            Brand.Brand.label(columns[6]),
            Model.Model.label(columns[7])
        ).join(
            Rent, Rent.ID_Client == Client.ID_Client
        ).join(
            Auto, Auto.ID_Auto == Rent.ID_Auto
        ).join(
            Brand, Auto.ID_Brand == Brand.ID_Brand
        ).join(
            Model, Auto.ID_Model == Model.ID_Model
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_rep_rentStat():
    columns = ["Номер аренды", "Номер автомобиля", "Марка", "Модель",
               "Номер сотрудника", "Фамилия сотрудника",
               "Номер клиента", "Фамилия клиента"]
    with Session(db.engine) as session:
        data = session.query(
            Rent.ID_Rent.label(columns[0]),
            Auto.ID_Auto.label(columns[1]),
            Brand.Brand.label(columns[2]),
            Model.Model.label(columns[3]),
            Employee.ID_Employee.label(columns[4]),
            Employee.Emp_Surname.label(columns[5]),
            Client.ID_Client.label(columns[6]),
            Client.Cli_Surn.label(columns[7])
        ).join(
            Auto, Auto.ID_Auto == Rent.ID_Auto
        ).join(
            Brand, Auto.ID_Brand == Brand.ID_Brand
        ).join(
            Model, Auto.ID_Model == Model.ID_Model
        ).join(
            Employee, Employee.ID_Employee == Rent.ID_Employee
        ).join(
            Client, Client.ID_Client == Rent.ID_Client
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns


def get_brands():
    columns = ['№', 'Марка']
    with Session(db.engine) as session:
        data = session.query(
            Brand.ID_Brand.label(columns[0]),
            Brand.Brand.label(columns[1])
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_models():
    columns = ['№', 'Марка', 'Модель']
    with Session(db.engine) as session:
        data = session.query(
            Model.ID_Model.label(columns[0]),
            Brand.Brand.label(columns[1]),
            Model.Model.label(columns[2])
        ).join(Brand, Brand.ID_Brand == Model.ID_Brand)
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_fuel():
    columns = ['№', 'Топливо']
    with Session(db.engine) as session:
        data = session.query(
            Fuel_Type.ID_Fuel.label(columns[0]),
            Fuel_Type.Fuel.label(columns[1])
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_transm():
    columns = ['№', 'Трансмиссия']
    with Session(db.engine) as session:
        data = session.query(
            Transmission.ID_Transm.label(columns[0]),
            Transmission.Transm.label(columns[1])
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_rentStat():
    columns = ['№', 'Статус']
    with Session(db.engine) as session:
        data = session.query(
            Rent_Status.ID_Status.label(columns[0]),
            Rent_Status.Status.label(columns[1])
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_city():
    columns = ['№', 'Город']
    with Session(db.engine) as session:
        data = session.query(
            City.ID_City.label(columns[0]),
            City.City.label(columns[1])
        ).all()
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_parks():
    columns = ['ID', 'Город', 'Улица', 'Номер дома', 'Время начала работы', 'Время окончания работы']
    with Session(db.engine) as session:
        data = session.query(
            Park.ID_Park.label(columns[0]),
            City.City.label(columns[1]),
            Park.Street.label(columns[2]),
            Park.House_Number.label(columns[3]),
            Park.Start_Time.label(columns[4]),
            Park.End_Time.label(columns[5])
        ).join(
            City, Park.ID_City == City.ID_City
        )
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_employee():
    columns = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Паспорт', 'ИНН',
               'Город парка', 'Улица парка', 'Номер дома']
    with Session(db.engine) as session:
        data = session.query(
            Employee.ID_Employee.label(columns[0]),
            Employee.Emp_Surname.label(columns[1]),
            Employee.Emp_Name.label(columns[2]),
            Employee.Emp_Patr.label(columns[3]),
            Employee.Passport.label(columns[4]),
            Employee.INN.label(columns[5]),
            City.City.label(columns[6]),
            Park.Street.label(columns[7]),
            Park.House_Number.label(columns[8])
        ).join(
            Park, Employee.ID_Park == Park.ID_Park
        ).join(
            City, Park.ID_City == City.ID_City
        )
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_auto():
    columns = ['ID', 'Марка', 'Модель', 'Топливо', 'Трансмиссия',
               'Цена аренды', 'Год производства', 'Город парка',
               'Улица', 'Номер дома', 'Расход топлива']
    with Session(db.engine) as session:
        data = session.query(
        Auto.ID_Auto.label(columns[0]),
        Brand.Brand.label(columns[1]),
        Model.Model.label(columns[2]),
        Fuel_Type.Fuel.label(columns[3]),
        Transmission.Transm.label(columns[4]),
        Auto.Rent_Price.label(columns[5]),
        Auto.Year.label(columns[6]),
        func.coalesce(City.City).label(columns[7]),
        func.coalesce(Park.Street).label(columns[8]),
        func.coalesce(Park.House_Number).label(columns[9]),
        Auto.Fuel_Consumption.label(columns[10])
    ).outerjoin(
        Park, Auto.ID_Park == Park.ID_Park
    ).outerjoin(
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
    return data_dicts, columns

def get_client():
    columns = ['ID', 'Фамилия', 'Имя', 'Отчество', 'ВУ',
               'Стаж', 'Номер телефона', 'Дата рождения']
    with Session(db.engine) as session:
        data = session.query(
        Client.ID_Client.label(columns[0]),
        Client.Cli_Surn.label(columns[1]),
        Client.Cli_Name.label(columns[2]),
        Client.Cli_Patr.label(columns[3]),
        Client.License.label(columns[4]),
        Client.Expirience.label(columns[5]),
        Client.Phone_Number.label(columns[6]),
        Client.Date_of_Birth.label(columns[7])
    )
    data_dicts = [row._asdict() for row in data]
    return data_dicts, columns

def get_rent():
    columns = ['ID', 'Номер сотрудника', 'Фамилия сотрудника',
               'Номер клиента', 'Фамилия клиента', 'Номер автомобиля',
               'Марка', 'Модель', 'Дата начала аренды', 'Дата окончания аренды',
               'Стоимость аренды', 'Залог', 'Статус аренды']
    with Session(db.engine) as session:
        data = session.query(
        Rent.ID_Rent.label(columns[0]),
        func.coalesce(Rent.ID_Employee).label(columns[1]),
        func.coalesce(Employee.Emp_Surname).label(columns[2]),
        func.coalesce(Rent.ID_Client).label(columns[3]),
        func.coalesce(Client.Cli_Surn).label(columns[4]),
        func.coalesce(Auto.ID_Auto).label(columns[5]),
        func.coalesce(Brand.Brand).label(columns[6]),
        func.coalesce(Model.Model).label(columns[7]),
        Rent.Start_Date.label(columns[8]),
        Rent.End_Date.label(columns[9]),
        Rent.Rent_Price.label(columns[10]),
        Rent.Pledge.label(columns[11]),
        Rent_Status.Status.label(columns[12])
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
    return data_dicts, columns


def delete_data(table_name, id_row) -> str:
    if table_name == 'аренды':
        data = Rent.query.get(id_row)
    elif table_name == 'марка автомобиля':
        data = Brand.query.get(id_row)
    elif table_name == 'модель автомобиля':
        data = Model.query.get(id_row)
    elif table_name == 'тип топлива автомобиля':
        data = Fuel_Type.query.get(id_row)
    elif table_name == 'трансмиссия автомобиля':
        data = Transmission.query.get(id_row)
    elif table_name == 'статус аренды':
        data = Rent_Status.query.get(id_row)
    elif table_name == 'города':
        data = City.query.get(id_row)
    elif table_name == 'парки':
        data = Park.query.get(id_row)
    elif table_name == 'сотрудники':
        data = Employee.query.get(id_row)
    elif table_name == 'автомобили':
        data = Auto.query.get(id_row)
    elif table_name == 'клиенты':
        data = Client.query.get(id_row)
    else: data = False
    
    try:
        if data:
            db.session.delete(data)
            db.session.commit()
            return 'Запись удалена', True
        else:
            return 'Ошибка!\nЗапись не обнаружена!', False
    except IntegrityError:
        return 'Невозможно удалить запись. В других таблицах есть зависимые элементы', True


def create_newRow(table_name, data):
    with Session(db.engine) as session:
        if table_name == 'марка автомобиля':
            Id = session.query(func.max(Brand.ID_Brand)).scalar()
            obj = Brand(ID_Brand=Id+1, Brand=data[1])
        elif table_name == 'модель автомобиля':
            Id = session.query(func.max(Model.ID_Model)).scalar()
            obj = Model(ID_Model=Id+1, ID_Brand=data[1], Model=data[2])
        elif table_name == 'тип топлива автомобиля':
            Id = session.query(func.max(Fuel_Type.ID_Fuel)).scalar()
            obj = Fuel_Type(ID_Fuel=Id+1, Fuel=data[1])
        elif table_name == 'трансмиссия автомобиля':
            Id = session.query(func.max(Transmission.ID_Transm)).scalar()
            obj = Transmission(ID_Transm=Id+1, Transm=data[1])
        elif table_name == 'статус аренды':
            Id = session.query(func.max(Rent_Status.ID_Status)).scalar()
            obj = Rent_Status(ID_Status=Id+1, Status=data[1])
        elif table_name == 'города':
            Id = session.query(func.max(City.ID_City)).scalar()
            obj = City(ID_City=Id+1, City=data[1])
        elif table_name == 'парки':
            Id = session.query(func.max(Park.ID_Park)).scalar()
            obj = Park(ID_Park=Id+1, ID_City=data[1], Street=data[2], House_Number=data[3],
                       Start_Time=data[4], End_Time=data[5])
        elif table_name == 'сотрудники':
            Id = session.query(func.max(Employee.ID_Employee)).scalar()
            obj = Employee(ID_Employee=Id+1, ID_Park=data[6], Emp_Surname=data[1], Emp_Name=data[2],
                       Emp_Patr=data[3], Passport=data[4], INN=data[5])
        elif table_name == 'автомобили':
            Id = session.query(func.max(Auto.ID_Auto)).scalar()
            obj = Auto(ID_Auto=Id+1, ID_Brand=data[1], ID_Model=data[2], ID_Fuel=data[3],
                       ID_Transm=data[4], ID_Park=data[7], Rent_Price=data[5], Year=data[6],
                       Fuel_Consumption=data[10])
        elif table_name == 'клиенты':
            Id = session.query(func.max(Client.ID_Client)).scalar()
            obj = Client(ID_Client=Id+1, Cli_Surn=data[1], Cli_Name=data[2], Cli_Patr=data[3],
                         License=data[4], Expirience=data[5], Phone_Number=data[6], Date_of_Birth=data[7])
        elif table_name == 'аренды':
            Id = session.query(func.max(Rent.ID_Rent)).scalar()
            obj = Rent(ID_Rent=Id+1, ID_Client=data[1], ID_Employee=data[3], ID_Auto=data[5],
                       ID_Status=data[12], Start_Date=data[8], End_Date=data[9],
                       Rent_Price=data[10], Pledge=data[11])
    db.session.add(obj)
    db.session.commit()


def edit_data(table_name, data):
    if table_name == 'марка автомобиля':
        obj = Brand.query.get(data[0])
        if obj:
            obj.Brand=data[1]
        else: return True, 'Запись не найдена'
    elif table_name == 'модель автомобиля':
        obj = Model.query.get(data[0])
        if obj:
            obj.ID_Brand=data[1]
            obj.Model=data[2]
        else: return True, 'Запись не найдена'
    elif table_name == 'тип топлива автомобиля':
        obj = Fuel_Type.query.get(data[0])
        if obj:
            obj.Fuel=data[1]
        else: return True, 'Запись не найдена'
    elif table_name == 'трансмиссия автомобиля':
        obj = Transmission.query.get(data[0])
        if obj:
            obj.Transm=data[1]
        else: return True, 'Запись не найдена'
    elif table_name == 'статус аренды':
        obj = Rent_Status.query.get(data[0])
        if obj:
            obj.Status=data[1]
        else: return True, 'Запись не найдена'
    elif table_name == 'города':
        obj = City.query.get(data[0])
        if obj:
            obj.City=data[1]
        else: return True, 'Запись не найдена'
    elif table_name == 'парки':
        obj = Park.query.get(data[0])
        if obj:
            obj.ID_City=data[1]
            obj.Street=data[2]
            obj.House_Number=data[3]
            obj.Start_Time=data[4]
            obj.End_Time=data[5]
        else: return True, 'Запись не найдена'
    elif table_name == 'сотрудники':
        obj = Employee.query.get(data[0])
        if obj:
            obj.ID_Park=data[6]
            obj.Emp_Surname=data[1]
            obj.Emp_Name=data[2]
            obj.Emp_Patr=data[3]
            obj.Passport=data[4]
            obj.INN=data[5]
        else: return True, 'Запись не найдена'
    elif table_name == 'автомобили':
        obj = Auto.query.get(data[0])
        if obj:
            obj.ID_Brand=data[1]
            obj.ID_Model=data[2]
            obj.ID_Fuel=data[3]
            obj.ID_Transm=data[4]
            obj.ID_Park=data[7]
            obj.Rent_Price=data[5]
            obj.Year=data[6]
            obj.Fuel_Consumption=data[10]
        else: return True, 'Запись не найдена'
    elif table_name == 'клиенты':
        obj = Client.query.get(data[0])
        if obj:
            obj.Cli_Surn=data[1]
            obj.Cli_Name=data[2]
            obj.Cli_Patr=data[3]
            obj.License=data[4]
            obj.Expirience=data[5]
            obj.Phone_Number=data[6]
            obj.Date_of_Birth=data[7]
        else: return True, 'Запись не найдена'
    elif table_name == 'аренды':
        obj = Rent.query.get(data[0])
        if obj:
            obj.ID_Client=data[1]
            obj.ID_Employee=data[3]
            obj.ID_Auto=data[5]
            obj.ID_Status=data[12]
            obj.Start_Date=data[8]
            obj.End_Date=data[9]
            obj.Rent_Price=data[10]
            obj.Pledge=data[11]
        else: return True, 'Запись не найдена'
    db.session.commit()
        
from datetime import date, timedelta, datetime
from flask import render_template, redirect, url_for, Flask, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import requests
import models
import re
import os
import pandas as pd
import concurrent.futures


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:postgres@localhost:5432/TRBD"
    )
REPORTS_DIR = os.path.join(os.getcwd(), "reports")

def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.get("/")
def index():
    return render_template(
        "main-page.html"
    )

@app.route('/report')
def report():
    table_type = request.args.get('filter', default='auto_list', type=str)
    calls = {
        'auto_list':  [models.get_rep_autoList, 'Списки автомобилей в парках'],
        'rent_by_client':  [models.get_rep_rentByClient, 'Аренда автомобилей по клиентам'],
        'stat_rent':   [models.get_rep_rentStat, 'Статистика аренды автомобилей']
    }
    data, columns = calls[table_type][0]()
    table_name = calls[table_type][1]
    return render_template('report.html', columns=columns, data=data, table_name=table_name)


def saveRep(table, query):
    with app.app_context():
        df = pd.read_sql_query(query, models.db.engine)
        df.to_excel(table+'.xlsx', index=False)


@app.route('/save_report', methods=['POST'])
def save_report():
    data = request.json
    table_name = data.get('table_name')
    
    if table_name == 'Списки автомобилей в парках':
        sql_query = """
            SELECT 
                p."ID_Park" AS "Номер парка",
                c."City" AS "Город",
                p."Street" AS "Улица",
                p."House_Number" AS "Номер дома",
                a."ID_Auto" AS "Номер автомобиля",
                b."Brand" AS "Марка",
                m."Model" AS "Модель"
            FROM 
                public."Park" as p
                JOIN public."City" as c ON p."ID_City" = c."ID_City"
                JOIN public."Auto" as a ON a."ID_Park" = p."ID_Park"
                JOIN public."Brand" as b ON a."ID_Brand" = b."ID_Brand"
                JOIN public."Model" as m ON a."ID_Model" = m."ID_Model"
        """
    elif table_name == 'Аренда автомобилей по клиентам':
        sql_query = """
            SELECT 
                c."ID_Client" AS "Номер клиента",
                c."Cli_Surn" AS "Фамилия",
                c."Cli_Name" AS "Имя",
                r."Start_Date" AS "Дата начала аренды",
                r."End_Date" AS "Дата окончания аренды",
                b."Brand" AS "Марка автомобиля",
                m."Model" AS "Модель автомобиля"
            FROM 
                public."Client" as c
                JOIN public."Rent" as r ON c."ID_Client" = r."ID_Client"
                JOIN public."Auto" as a ON a."ID_Auto" = r."ID_Auto"
                JOIN public."Brand" as b ON a."ID_Brand" = b."ID_Brand"
                JOIN public."Model" as m ON a."ID_Model" = m."ID_Model"
        """
    elif table_name == 'Статистика аренды автомобилей':
        sql_query = """
            SELECT 
                r."ID_Rent" AS "Номер аренды",
                a."ID_Auto" AS "Номер автомобиля",
                b."Brand" AS "Марка",
                m."Model" AS "Модель",
                e."ID_Employee" AS "Номер сотрудника",
                e."Emp_Surname" AS "Фамилия сотрудника",
                c."ID_Client" AS "Номер клиента",
                c."Cli_Surn" AS "Фамилия клиента"
            FROM 
                public."Rent" as r
                JOIN public."Auto" as a ON r."ID_Auto" = a."ID_Auto"
                JOIN public."Brand" as b ON a."ID_Brand" = b."ID_Brand"
                JOIN public."Model" as m ON a."ID_Model" = m."ID_Model"
                JOIN public."Employee" as e ON r."ID_Employee" = e."ID_Employee"
                JOIN public."Client" as c ON r."ID_Client" = c."ID_Client"
        """
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(saveRep, table_name, sql_query)
        future.result()
        
    # Возвращаем ответ клиенту
    response = {
        'messange': 'Таблица сохранена',
        'table_name': table_name
    }
    return jsonify(response)


@app.route('/table')
def table():
    table_type = request.args.get('filter', default='brand', type=str)
    calls = {
        'brand':  [models.get_brands, 'марка автомобиля'],
        'model':  [models.get_models, 'модель автомобиля'],
        'fuel':   [models.get_fuel, 'тип топлива автомобиля'],
        'transm': [models.get_transm, 'трансмиссия автомобиля'],
        'rentStat': [models.get_rentStat, 'статус аренды'],
        'city': [models.get_city, 'города'],
        'park': [models.get_parks, 'парки'],
        'emp': [models.get_employee, 'сотрудники'],
        'auto': [models.get_auto, 'автомобили'],
        'cli': [models.get_client, 'клиенты'],
        'rent': [models.get_rent, 'аренды']
    }
    data, columns = calls[table_type][0]()
    table_name = calls[table_type][1]
    return render_template('table.html', columns=columns, data=data, table_name=table_name)


@app.route('/comboBox_value_change', methods=['POST'])
def comboBox_value_change():
    data = request.json
    curentID = data.get('curentID')
    tableName = data.get('TableName')
    if tableName == 'автомобили':
        with Session(models.db.engine) as session:
            Values = session.query(
                models.Model.ID_Model,
                models.Model.Model
                ).where(
                    models.Model.ID_Brand == curentID
                ).all()
            for i in range(len(Values)):
                Values[i] = list(Values[i])
    elif tableName == 'аренды':
        with Session(models.db.engine) as session:
            curentID = session.query(
                models.Employee.ID_Park
            ).where(
                models.Employee.ID_Employee == curentID
            ).first()[0]
            Values = session.query(
                models.Auto.ID_Auto,
                func.concat(models.Auto.ID_Auto, '. ', models.Brand.Brand,' ', models.Model.Model)
            ).join(
                models.Brand, models.Brand.ID_Brand == models.Auto.ID_Brand
            ).join(
                models.Model, models.Model.ID_Model == models.Auto.ID_Model
            ).where(
                models.Auto.ID_Park == curentID
            ).all()
            for i in range(len(Values)):
                Values[i] = list(Values[i])
    
    # Возвращаем ответ клиенту
    response = {
        'curentID': curentID,
        'Values': Values
    }
    return jsonify(response)


@app.route('/handle_cell_click', methods=['POST'])
def handle_cell_click():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')
    table_name = data.get('table_name')
    type_col = data.get('type_col')
    IsModified = data.get('IsModified')

    pattern = False
    if table_name == 'модель автомобиля':
        type_col = [0, 2, 1]
        with Session(models.db.engine) as session:
            if IsModified:
                selected = row_data[1]
            else:
                selected = -1
                row_data = ['']*len(type_col)
            row_data[1] = session.query(
                models.Brand.ID_Brand,
                models.Brand.Brand
            ).all()
            for r in range(len(row_data[1])):
                row_data[1][r] = list(row_data[1][r])
                s = ''
                if row_data[1][r][1] == selected:
                    s = ' selected'
                row_data[1][r].append(s)
    elif table_name in ['марка автомобиля', 'тип топлива автомобиля', 'трансмиссия автомобиля', 'статус аренды', 'города']:
        type_col = [0, 1]
    elif table_name == 'парки':
        type_col = [0, 2, 1, 1, 1, 1]
        with Session(models.db.engine) as session:
            if IsModified:
                selected = row_data[1]
            else:
                selected = -1
                row_data = ['']*len(type_col)
            row_data[1] = session.query(
                models.City.ID_City,
                models.City.City
            ).all()
            for r in range(len(row_data[1])):
                row_data[1][r] = list(row_data[1][r])
                s = ''
                if row_data[1][r][1] == selected:
                    s = ' selected'
                row_data[1][r].append(s)
        pattern = ['', '', '', '', 'чч:мм', 'чч:мм']
    elif table_name == 'сотрудники':
        type_col = [0, 1, 1, 1, 1, 1, 2]
        with Session(models.db.engine) as session:
            if IsModified:
                selected = row_data[6]+', '+row_data[7]+' '+row_data[8]
            else:
                selected = -1
                row_data = ['']*len(type_col)
            row_data[6] = session.query(
                models.Park.ID_Park,
                func.concat(models.City.City, ', ', models.Park.Street, ' ', models.Park.House_Number)
            ).join(
                models.City, models.City.ID_City == models.Park.ID_City
            ).all()
            for r in range(len(row_data[6])):
                row_data[6][r] = list(row_data[6][r])
                s = ''
                if row_data[6][r][1] == selected:
                    s = ' selected'
                row_data[6][r].append(s)
        pattern = ['', '', '', '', 'xxxx xxxxxx', 'xxxxxxxxxxx']
    elif table_name == 'автомобили':
        type_col = [0, 3, 4, 2, 2, 1, 1, 2, 0, 0, 1]
        with Session(models.db.engine) as session:
            if IsModified:
                selected = row_data[1]
            else:
                selected = -1
                row_data = ['']*len(type_col)
            row_data[1] = session.query(
                models.Brand.ID_Brand,
                models.Brand.Brand
            ).all()
            for r in range(len(row_data[1])):
                row_data[1][r] = list(row_data[1][r])
                s = ''
                if IsModified:
                    if row_data[1][r][1] == selected:
                        s = ' selected'
                        brandID = row_data[1][r][0]
                row_data[1][r].append(s)

            if IsModified:
                selected = row_data[2]
            else:
                selected = -1
                brandID = row_data[1][0][0]
            row_data[2] = session.query(
                models.Model.ID_Brand,
                models.Model.Model
            ).where(
                models.Model.ID_Brand == brandID
            ).all()
            for r in range(len(row_data[2])):
                row_data[2][r] = list(row_data[2][r])
                s = ''
                if row_data[2][r][1] == selected:
                    s = ' selected'
                row_data[2][r].append(s)

            if IsModified:
                selected = row_data[3]
            else:
                selected = -1
            row_data[3] = session.query(
                models.Fuel_Type.ID_Fuel,
                models.Fuel_Type.Fuel
            ).all()
            for r in range(len(row_data[3])):
                row_data[3][r] = list(row_data[3][r])
                s = ''
                if row_data[3][r][1] == selected:
                    s = ' selected'
                row_data[3][r].append(s)

            if IsModified:
                selected = row_data[4]
            else:
                selected = -1
            row_data[4] = session.query(
                models.Transmission.ID_Transm,
                models.Transmission.Transm
            ).all()
            for r in range(len(row_data[4])):
                row_data[4][r] = list(row_data[4][r])
                s = ''
                if row_data[4][r][1] == selected:
                    s = ' selected'
                row_data[4][r].append(s)
                
            if IsModified:
                selected = row_data[7]+', '+row_data[8]+' '+row_data[9]
            else:
                selected = -1
            row_data[7] = session.query(
                models.Park.ID_Park,
                func.concat(models.City.City, ', ', models.Park.Street, ' ', models.Park.House_Number)
            ).join(
                models.City, models.City.ID_City == models.Park.ID_City
            ).all()
            for r in range(len(row_data[7])):
                row_data[7][r] = list(row_data[7][r])
                s = ''
                if row_data[7][r][1] == selected:
                    s = ' selected'
                row_data[7][r].append(s)
    elif table_name == 'клиенты':
        type_col = [0, 1, 1, 1, 1, 1, 1, 1]
        pattern = ['', '', '', '', 'xxxx xxxxxx', '', '8xxxxxxxxxx', 'гггг-мм-дд']
    elif table_name == 'аренды':
        type_col = [0, 3, 0, 2, 0, 4, 0, 0, 1, 1, 0, 1, 2]
        with Session(models.db.engine) as session:
            if IsModified:
                selected = int(row_data[1])
            else:
                selected = -1
                row_data = ['']*len(type_col)
            row_data[1] = session.query(
                models.Employee.ID_Employee,
                func.concat(models.Employee.ID_Employee, '. ', models.Employee.Emp_Surname,' ', models.Employee.Emp_Name,' ', models.Employee.Emp_Patr)
            ).all()
            for r in range(len(row_data[1])):
                row_data[1][r] = list(row_data[1][r])
                s = ''
                if row_data[1][r][0] == selected:
                    s = ' selected'
                    if IsModified:
                        curentID = session.query(
                            models.Employee.ID_Park
                        ).where(
                            models.Employee.ID_Employee == row_data[1][r][0]
                        ).first()[0]
                row_data[1][r].append(s)

            if IsModified:
                selected = int(row_data[3])
            else:
                selected = -1
            row_data[3] = session.query(
                models.Client.ID_Client,
                func.concat(models.Client.ID_Client, '. ', models.Client.Cli_Surn,' ', models.Client.Cli_Name,' ', models.Client.Cli_Patr)
            ).all()
            for r in range(len(row_data[3])):
                row_data[3][r] = list(row_data[3][r])
                s = ''
                if row_data[3][r][0] == selected:
                    s = ' selected'
                row_data[3][r].append(s)

            if IsModified:
                selected = int(row_data[5])
            else:
                selected = -1
                curentID = session.query(
                    models.Employee.ID_Park
                ).where(
                    models.Employee.ID_Employee == row_data[1][0][0]
                ).first()[0]
            row_data[5] = session.query(
                models.Auto.ID_Auto,
                func.concat(models.Auto.ID_Auto, '. ', models.Brand.Brand,' ', models.Model.Model)
            ).join(
                models.Brand, models.Brand.ID_Brand == models.Auto.ID_Brand
            ).join(
                models.Model, models.Model.ID_Model == models.Auto.ID_Model
            ).where(
                models.Auto.ID_Park == curentID
            ).all()
            for r in range(len(row_data[5])):
                row_data[5][r] = list(row_data[5][r])
                s = ''
                if row_data[5][r][0] == selected:
                    s = ' selected'
                row_data[5][r].append(s)

            if IsModified:
                selected = row_data[12]
            else:
                selected = -1
            row_data[12] = session.query(
                models.Rent_Status.ID_Status,
                models.Rent_Status.Status
            ).all()
            for r in range(len(row_data[12])):
                row_data[12][r] = list(row_data[12][r])
                s = ''
                if row_data[12][r][1] == selected:
                    s = ' selected'
                row_data[12][r].append(s)
        pattern = ['', '', '', '', '', '', '', '', 'гггг-мм-дд', 'гггг-мм-дд', '', '', '']
    if not pattern:
        pattern = ['']*len(type_col)

    # Возвращаем ответ клиенту
    response = {
        'row_data': row_data,
        'column_names': column_names,
        'table_name': table_name,
        'type_col': type_col,
        'pattern': pattern
    }
    return jsonify(response)

def check_data(table_name, data, columns):
    if table_name in ['марка автомобиля', 'тип топлива автомобиля', 'трансмиссия автомобиля', 'статус аренды', 'города']:
        if data[1] == '': return [True, f'Поле "{columns[1]}" не может быть пустым']
    elif table_name == 'модель автомобиля':
        if data[2] == '': return [True, f'Поле "{columns[2]}" не может быть пустым']
    elif table_name == 'парки':
        for i in range(2, 6):
            if data[i] == '': return [True, f'Поле "{columns[i]}" не может быть пустым']
        if not data[3].isnumeric(): return [True, f'{columns[3]} должен быть целым положительным числом']
        if not is_valid_time(data[4]): return [True, 'Введите время начала работы по шаблону']
        s = data[4].split(':')
        if int(s[0]) < 5 or int(s[0]) > 12: return [True, 'Время начала работы может быть с 5:00 до 12:00']
        if int(s[0]) == 12:
            if s[1] != '00': return [True, 'Время начала работы может быть с 5:00 до 12:00']
        if not is_valid_time(data[5]): return [True, 'Введите время окончания работы по шаблону']
        s = data[5].split(':')
        if int(s[0]) < 15 and int(s[0]) != 0: return [True, 'Время окончания работы может быть с 15:00 до 00:00']
        if int(s[0]) == 0:
            if s[1] != '00': return [True, 'Время окончания работы может быть с 15:00 до 00:00']
    elif table_name == 'сотрудники':
        for i in range(1, 6):
            if i == 3: continue
            if data[i] == '': return [True, f'Поле "{columns[i]}" не может быть пустым']
        if not bool(re.match('^[1-9]\d{3} [1-9]\d{5}', data[4])): return [True, 'Введите паспортные данные по шаблону']
        if not bool(re.match('^[1-9]\d{10}', data[5])): return [True, 'Введите ИНН по шаблону']
    elif table_name == 'автомобили':
        for i in [5, 6, 10]:
            if data[i] == '': return [True, f'Поле "{columns[i]}" не может быть пустым']
        if not data[5].isnumeric(): return [True, 'Цена аренды должна быть целым положительным числом']
        if not data[6].isnumeric(): return [True, 'Год производства должен быть числом']
        s = int(data[6])
        if s < 1960 or s > datetime.now().year: return [True, f'Год производства автомобиля болжен в период с 1960 по {datetime.now().year} год']
        if not data[10].isnumeric(): return [True, 'Расход топлива должен быть целым положительным числом']
    elif table_name == 'клиенты':
        for i in range(1, 8):
            if i == 3: continue
            if data[i] == '': return [True, f'Поле "{columns[i]}" не может быть пустым']
        if not bool(re.match('^[1-9]\d{3} [1-9]\d{5}', data[4])): return [True, 'Введите данные ВУ по шаблону']
        if not data[5].isnumeric(): return [True, 'Стаж должен быть целым положительным числом']
        if len(data[5]) > 2: return [True, 'Стаж не может быть более чем двузначным числом']
        if not bool(re.match('^8\d{10}', data[6])): return [True, 'Введите номер телефона по шаблону']
        if not is_valid_date(data[7]): return [True, 'Введите дату рождения по шаблону']
        if int(data[7].split('-')[0]) >= datetime.now().year-18: return [True, 'Клиенту не может быть меньше 18 лет']
    elif table_name == 'аренды':
        for i in [8, 9, 11]:
            if data[i] == '': return [True, f'Поле "{columns[i]}" не может быть пустым']
        if not is_valid_date(data[8]): return [True, 'Введите дату начала аренды по шаблону']
        if not is_valid_date(data[9]): return [True, 'Введите дату окончания аренды по шаблону']
        if not data[11].isnumeric(): return [True, 'Залог должен быть целым положительным числом']
        days = (datetime.strptime(data[9], "%Y-%m-%d") - datetime.strptime(data[8], "%Y-%m-%d")).days
        print(days)
        if days < 1: return [True, 'Дата окончания аренды должна быть позже даты начала']
        with Session(models.db.engine) as session:
            cost = session.query(models.Auto.Rent_Price).filter(models.Auto.ID_Auto == data[5]).scalar()
        data[10] = cost*(days+1)
    return [False]

@app.route('/add_new_row', methods=['POST'])
def add_new_row():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')
    table_name = data.get('table_name')
    
    messange = check_data(table_name, row_data, column_names)
    if messange[0]:
        response = {
            'IsCorrect': False,
            'message': messange[1]
        }
        return jsonify(response)
    models.create_newRow(table_name, row_data)

    # Возвращаем ответ клиенту
    response = {
        'IsCorrect': True,
        'message': 'Запись сохранена'
    }
    return jsonify(response)

@app.route('/save_changes', methods=['POST'])
def save_changes():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')
    table_name = data.get('table_name')

    messange = check_data(table_name, row_data, column_names)
    if messange[0]:
        response = {
            'IsCorrect': False,
            'message': messange[1]
        }
        return jsonify(response)
    models.edit_data(table_name, row_data)

    # Возвращаем ответ клиенту
    response = {
        'IsCorrect': True,
        'message': 'Изменения сохранены'
    }
    return jsonify(response)

@app.route('/delete_row', methods=['POST'])
def delete_row():
    data = request.json
    delID = data.get('del_id')
    table_name = data.get('table_name')
    
    messange, IsCor = models.delete_data(table_name, delID)

    # Возвращаем ответ клиенту
    response = {
        'IsCorrect': IsCor,
        'message': messange,
        'title': 'кастомное сообщение'
    }
    return jsonify(response)

if __name__ == "__main__":
    models.db.init_app(app)
    app.run(debug=True)
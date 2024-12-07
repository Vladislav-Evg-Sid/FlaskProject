from datetime import date, timedelta
from flask import render_template, redirect, url_for, Flask, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import func
import requests
import models


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:postgres@localhost:5432/TRBD"
    )

@app.get("/")
def index():
    return render_template(
        "main-page.html"
    )

@app.route('/table')
def table():
    table_type = request.args.get('filter', default='brand', type=str)
    if table_type == 'brand':
        data = models.get_brands()
        table_name = 'марка автомобиля'
    if table_type == 'model':
        data = models.get_models()
        table_name = 'модель автомобиля'
    if table_type == 'fuel':
        data = models.get_fuel()
        table_name = 'тип топлива автомобиля'
    if table_type == 'transm':
        data = models.get_transm()
        table_name = 'трансмиссия автомобиля'
    if table_type == 'rentStat':
        data = models.get_rentStat()
        table_name = 'статус аренды'
    if table_type == 'city':
        data = models.get_city()
        table_name = 'города'
    if table_type == 'park':
        data = models.get_parks()
        table_name = 'парки'
    if table_type == 'emp':
        data = models.get_employee()
        table_name = 'сотрудники'
    if table_type == 'auto':
        data = models.get_auto()
        table_name = 'автомобили'
    if table_type == 'cli':
        data = models.get_client()
        table_name = 'клиенты'
    if table_type == 'rent':
        data = models.get_rent()
        table_name = 'аренды'
    columns = list(data[0].keys())
    return render_template('table.html', columns=columns, data=data, table_name=table_name)

@app.route('/handle_cell_click', methods=['POST'])
def handle_cell_click():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')
    table_name = data.get('table_name')
    type_col = data.get('type_col')

    if table_name == 'модель автомобиля':
        type_col = [0, 2, 1]
        with Session(models.db.engine) as session:
            selected = row_data[1]
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
    elif table_name in ['марка автомобиля', 'тип топлива автомобиля',
                        'трансмиссия автомобиля', 'статус аренды', 'города']:
        type_col = [0, 1]
    elif table_name == 'парки':
        type_col = [0, 2, 1, 1, 1, 1]
        with Session(models.db.engine) as session:
            selected = row_data[1]
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
    elif table_name == 'сотрудники':
        type_col = [0, 1, 1, 1, 1, 1, 2]
        with Session(models.db.engine) as session:
            selected = row_data[6]+', '+row_data[7]+' '+row_data[8]
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
    elif table_name == 'автомобили':
        type_col = [0, 2, 2, 2, 2, 1, 1, 2, 0, 0, 1]
        with Session(models.db.engine) as session:
            selected = row_data[1]
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

            selected = row_data[2]
            row_data[2] = session.query(
                models.Model.ID_Brand,
                models.Model.Model
            ).all()
            for r in range(len(row_data[2])):
                row_data[2][r] = list(row_data[2][r])
                s = ''
                if row_data[2][r][1] == selected:
                    s = ' selected'
                row_data[2][r].append(s)

            selected = row_data[3]
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

            selected = row_data[4]
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
                
            selected = row_data[7]+', '+row_data[8]+' '+row_data[9]
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
    elif table_name == 'аренды':
        type_col = [0, 2, 0, 2, 0, 2, 0, 0, 1, 1, 1, 1, 2]
        with Session(models.db.engine) as session:
            selected = int(row_data[1])
            row_data[1] = session.query(
                models.Employee.ID_Employee,
                func.concat(models.Employee.ID_Employee, '. ', models.Employee.Emp_Surname,' ', models.Employee.Emp_Name,' ', models.Employee.Emp_Patr)
            ).all()
            for r in range(len(row_data[1])):
                row_data[1][r] = list(row_data[1][r])
                s = ''
                if row_data[1][r][0] == selected:
                    s = ' selected'
                row_data[1][r].append(s)

            selected = int(row_data[3])
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

            selected = int(row_data[5])
            row_data[5] = session.query(
                models.Auto.ID_Auto,
                func.concat(models.Auto.ID_Auto, '. ', models.Brand.Brand,' ', models.Model.Model)
            ).join(
                models.Brand, models.Brand.ID_Brand == models.Auto.ID_Brand
            ).join(
                models.Model, models.Model.ID_Model == models.Auto.ID_Model
            ).all()
            for r in range(len(row_data[5])):
                row_data[5][r] = list(row_data[5][r])
                s = ''
                if row_data[5][r][0] == selected:
                    s = ' selected'
                row_data[5][r].append(s)

            selected = row_data[12]
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
        

    # Возвращаем ответ клиенту
    response = {
        'row_data': row_data,
        'column_names': column_names,
        'table_name': table_name,
        'type_col': type_col
    }
    return jsonify(response)

@app.route('/save_changes', methods=['POST'])
def save_changes():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')

    # Здесь можно выполнить любой Python-код для сохранения изменений
    # Например, обновление базы данных
    print(f'Сохранены изменения: {row_data}')

    # Возвращаем ответ клиенту
    response = {
        'message': 'Изменения сохранены'
    }
    return jsonify(response)

if __name__ == "__main__":
    models.db.init_app(app)
    app.run(debug=True)
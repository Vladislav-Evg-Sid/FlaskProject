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
        data, columns = models.get_brands()
        table_name = 'марка автомобиля'
    if table_type == 'model':
        data, columns = models.get_models()
        table_name = 'модель автомобиля'
    if table_type == 'fuel':
        data, columns = models.get_fuel()
        table_name = 'тип топлива автомобиля'
    if table_type == 'transm':
        data, columns = models.get_transm()
        table_name = 'трансмиссия автомобиля'
    if table_type == 'rentStat':
        data, columns = models.get_rentStat()
        table_name = 'статус аренды'
    if table_type == 'city':
        data, columns = models.get_city()
        table_name = 'города'
    if table_type == 'park':
        data, columns = models.get_parks()
        table_name = 'парки'
    if table_type == 'emp':
        data, columns = models.get_employee()
        table_name = 'сотрудники'
    if table_type == 'auto':
        data, columns = models.get_auto()
        table_name = 'автомобили'
    if table_type == 'cli':
        data, columns = models.get_client()
        table_name = 'клиенты'
    if table_type == 'rent':
        data, columns = models.get_rent()
        table_name = 'аренды'
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
    elif table_name == 'аренды':
        type_col = [0, 3, 0, 2, 0, 4, 0, 0, 1, 1, 1, 1, 2]
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
        

    # Возвращаем ответ клиенту
    response = {
        'row_data': row_data,
        'column_names': column_names,
        'table_name': table_name,
        'type_col': type_col
    }
    return jsonify(response)

def check_data(table_name, data):
    if table_name in ['марка автомобиля', 'ы']:
        if data[1] == '': return [True, 'Поле не может быть пустым']
    elif table_name == 'модель автомобиля':
        if data[2] == '': return [True, 'Поле не может быть пустым']
    return [False]

@app.route('/save_changes', methods=['POST'])
def save_changes():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')

    for i in range(len(row_data)):
        print('*'*150)
        print(f'{column_names[i]}: {row_data[i]}')

    # Возвращаем ответ клиенту
    response = {
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
        'message': messange
    }
    return jsonify(response)

@app.route('/add_new_row', methods=['POST'])
def add_new_row():
    data = request.json
    row_data = data.get('row_data')
    column_names = data.get('column_names')
    table_name = data.get('table_name')
    
    messange = check_data(table_name, row_data)
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

if __name__ == "__main__":
    models.db.init_app(app)
    app.run(debug=True)
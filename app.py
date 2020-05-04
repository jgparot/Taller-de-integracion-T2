from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from collections import OrderedDict
import os


##      QUE ME FALTA: ####
#################### ERRORES PARA POST Y UPDATE
#################### ORDENAR LOS PARAMETROS CUANDO SE RETORNAN


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
#base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#inciar db
db = SQLAlchemy(app)
#Iniciar marshmellow
ma = Marshmallow(app)

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(100))

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion


class IngredienteSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'descripcion')


ingrediente_schema = IngredienteSchema()
ingredientes_schema = IngredienteSchema(many=True)


#CREEAR INGREDIENTE

@app.route("/ingrediente", methods=['POST'])
def add_ingrediente():
    try:
        nombre = request.json['nombre']
        descripcion = request.json['descripcion']
        if len(request.json) > 2:
            raise InvalidUsage("Input inválidos", status_code=400)
        if not (isinstance(nombre, str) and isinstance(descripcion, str)):
            raise InvalidUsage("Input inválidos", status_code=400)

        new_ingrediente = Ingrediente(nombre, descripcion)
        db.session.add(new_ingrediente)
        db.session.commit()
        return ingrediente_schema.jsonify(new_ingrediente), "201 Ingrediente " \
                                                            "creado"
    except KeyError:
        raise InvalidUsage('Input invalido', status_code=400)




#MOSTRAR 1 Ingrediente

@app.route('/ingrediente/<id_ing>', methods=['GET'])
def get_ingrediente(id_ing):
    if not id_ing.isnumeric():
        raise InvalidUsage('id invalido', status_code=400)
    ingrediente = Ingrediente.query.get(id_ing)
    if ingrediente == None:
        raise InvalidUsage('ingrediente inexistente', status_code=404)
    return ingrediente_schema.jsonify(ingrediente)

#MOSTRAR VARIOS ingredientesOS
@app.route('/ingrediente', methods=['GET'])
def get_ingredientes():
    all_ingredientes = Ingrediente.query.all()
    result = ingredientes_schema.dump(all_ingredientes)
    return jsonify(result)


#DELETE UN ingredienteO
@app.route('/ingrediente/<id_ing>', methods=['DELETE'])
def delete_ingrediente(id_ing):
    ingrediente = Ingrediente.query.get(id_ing)
    if ingrediente == None:
        raise InvalidUsage("Ingrediente inexistente", status_code=404)
    all_hamburguesas = Hamburguesa_Ingrediente.query.all()
    eliminar = True
    for i in all_hamburguesas:
        if i.id_ingrediente == int(id_ing):
            eliminar = False
    if eliminar:
        db.session.delete(ingrediente)
        db.session.commit()
        return "Ingrediente eliminado", "200 ingrediente eliminado"

    raise InvalidUsage("Ingrediente no se puede borrar, se encuentra presente en una " \
           "hamburguesa", status_code=409)



# modelo del Hamburguesao
class Hamburguesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(100))
    precio = db.Column(db.Integer)
    imagen = db.Column(db.String(100))

    def __init__(self, nombre, precio, descripcion, imagen, ingredientes=[]):
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.imagen = imagen
        self.ingredientes = ingredientes

class HamburguesaSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'precio', 'descripcion', 'imagen', 'ingredientes')

hamburguesa_schema = HamburguesaSchema()
hamburguesas_schema = HamburguesaSchema(many=True)

#CREAR hamburguesaO

@app.route("/hamburguesa", methods=['POST'])
def add_hamburguesa():
    try:
        nombre = request.json['nombre']
        descripcion = request.json['descripcion']
        precio = request.json['precio']
        imagen = request.json['imagen']

        if not (isinstance(nombre,str) and isinstance(descripcion, str) and isinstance(precio, int) and isinstance(imagen, str)):
            raise InvalidUsage("Parámetros inválidos", status_code=400)
        if len(request.json) > 4:
            raise InvalidUsage("Input inválido", status_code=400)

        new_hamburguesa = Hamburguesa(nombre, precio, descripcion, imagen)
        db.session.add(new_hamburguesa)
        db.session.commit()
        return hamburguesa_schema.jsonify(new_hamburguesa), "201 hamburguesa " \
                                                            "creada"

    except KeyError or ValueError:
        raise InvalidUsage('Input invalido', status_code=400)



#MOSTRAR 1 hamburguesaO

@app.route('/hamburguesa/<id>', methods=['GET'])
def get_hamburguesa(id):
    hamburguesa = Hamburguesa.query.get(id)
    if not id.isnumeric() or id is None:
        raise InvalidUsage('id invalido', status_code=400)
    if hamburguesa is None:
        raise InvalidUsage('hamburguesa inexistente', status_code=404)
    all_hamburguesas = Hamburguesa_Ingrediente.query.all()
    hamburguesa.ingredientes = []
    for i in all_hamburguesas:
        hamburguesa.ingredientes.append({"path": f"https://burgas-jp-api2.herokuapp.com/ingrediente/{i.id_ingrediente}"})
    #respuesta = {'id': hamburguesa.id , 'nombre': hamburguesa.nombre, 'precio': hamburguesa.precio, 'descripcion': hamburguesa.descripcion, 'imagen': hamburguesa.imagen, 'ingredientes': hamburguesa.ingredientes}
    #return jsonify(respuesta)
    #return jsonify(meter_en_dic(hamburguesa)), "200 operacion exitosa"
    return hamburguesa_schema.jsonify(hamburguesa), "200 operacion exitosa"

#MOSTRAR VARIOS hamburguesaOS
@app.route('/hamburguesa', methods=['GET'])
def get_hamburguesas():
    all_hamburguesas = Hamburguesa.query.all()
    all_hamburguesas_ingredientes = Hamburguesa_Ingrediente.query.all()
    for i in all_hamburguesas:
        i.ingredientes = []
    for i in all_hamburguesas:
        for j in all_hamburguesas_ingredientes:
            if i.id == j.id_hamburguesa:
                i.ingredientes.append({"path": f"https://burgas-jp-api2.herokuapp.com/ingrediente/{j.id_ingrediente}"})

    result = hamburguesas_schema.dump(all_hamburguesas)
    return jsonify(result)

#UPDATE UN hamburguesaO

@app.route("/hamburguesa/<id>", methods=['PATCH'])
def update_hamburguesa(id):
    if not id.isnumeric():
        raise InvalidUsage('Parámetros inválidos', status_code=400)
    hamburguesa = Hamburguesa.query.get(id)
    if hamburguesa is None:
        raise InvalidUsage('Hamburguesa inexistente', status_code=404)
    try:
        if len(request.json) == 0:
            raise InvalidUsage('Parámetros inválidos', status_code=400)
        for i in request.json:
            if i == "nombre" and isinstance(request.json['nombre'], str):
                hamburguesa.nombre = request.json['nombre']
            elif i == "descripcion" and isinstance(request.json['descripcion'], str):
                hamburguesa.descripcion = request.json['descripcion']
            elif i == "precio" and isinstance(request.json['precio'], int):
                hamburguesa.precio = request.json['precio']
            elif i == "imagen" and isinstance(request.json['imagen'], str):
                hamburguesa.imagen = request.json['imagen']
            else:
                raise InvalidUsage("Parámetros inválidos", status_code=400)
        #if not (isinstance(nombre, str) and isinstance(descripcion,
         #                                              str) and isinstance(
          #      precio, int) and isinstance(imagen, str)):
           # raise InvalidUsage("Parámetros inválidos", status_code=400)
        if len(request.json) > 4:
            raise InvalidUsage("Parámetros inválidos", status_code=400)

        db.session.commit()
        all_hamburguesas = Hamburguesa_Ingrediente.query.all()
        hamburguesa.ingredientes = []
        for i in all_hamburguesas:
            hamburguesa.ingredientes.append(
                {"path": f"https://burgas-jp-api2.herokuapp.com/ingrediente/{i.id_ingrediente}"})

        return hamburguesa_schema.jsonify(hamburguesa), "200 operacion exitosa"
    except KeyError:
        raise InvalidUsage('Parámetros inválidos', status_code=400)

#DELETE UN hamburguesaO
@app.route('/hamburguesa/<id>', methods=['DELETE'])
def delete_hamburguesa(id):
    hamburguesa = Hamburguesa.query.get(id)
    if hamburguesa is None:
        raise InvalidUsage('hamburguesa inexistente', status_code=404)
    all_hamburguesas = Hamburguesa_Ingrediente.query.all()
    a_eliminar = []
    for i in all_hamburguesas:
        if hamburguesa.id == i.id_hamburguesa:
            a_eliminar.append(i)
    for j in a_eliminar:
        db.session.delete(j)
    db.session.delete(hamburguesa)
    db.session.commit()
    return "hamburguesa eliminada"





# modelo del Hamburguesao
class Hamburguesa_Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_hamburguesa = db.Column(db.Integer)
    id_ingrediente = db.Column(db.Integer)

    def __init__(self, id_hamburguesa, id_ingrediente):
        self.id_hamburguesa = id_hamburguesa
        self.id_ingrediente = id_ingrediente


@app.route('/hamburguesa/<id>/ingrediente/<id_ing>', methods=['PUT'])
def put_ingrediente_en_hamburguesa(id, id_ing):
    hamburguesa = Hamburguesa.query.get(id)
    if hamburguesa is None:
        raise InvalidUsage('Id de la hamburguesa inválido', status_code=400)
    ingrediente = Ingrediente.query.get(id_ing)
    if ingrediente is None:
        raise InvalidUsage('Ingrediente inexistente', status_code=404)
    all_hamburguesas = Hamburguesa_Ingrediente.query.all()
    for i in all_hamburguesas:
        if i.id_ingrediente == ingrediente.id and i.id_hamburguesa == hamburguesa.id:
            return "Ingrediente agregado nuevamente", "201 Ingrediente agregado"
    new_hamburguesa_ingrediente = Hamburguesa_Ingrediente(hamburguesa.id, ingrediente.id)
    db.session.add(new_hamburguesa_ingrediente)
    db.session.commit()
    return "Ingrediente agregado", "201 Ingrediente agregado"

@app.route('/hamburguesa/<id>/ingrediente/<id_ing>', methods=['DELETE'])
def Delete_ingrediente_en_hamburguesa(id, id_ing):
    if Ingrediente.query.get(id_ing) is None:
        raise InvalidUsage('Ingrediente inexistente', status_code=404)
    if not Hamburguesa.query.get(id) or not id.isnumeric():
        raise InvalidUsage('Hamburguesa inexistente', status_code=404)
    if not id.isnumeric():
        raise InvalidUsage('Id de hamburguesa inválido', status_code=400)
    if not id_ing.isnumeric():
        raise InvalidUsage('Id de ingrediente inválido', status_code=400)
    all_hamburguesas = Hamburguesa_Ingrediente.query.all()
    eliminar = False
    for i in all_hamburguesas:
        if i.id_hamburguesa == int(id) and i.id_ingrediente == int(id_ing):
            eliminar = True
            burga = i
            break

    if eliminar:
        db.session.delete(burga)
        db.session.commit()
        return "ingrediente retirado", "200 ingrediente retirado"
    else:
        raise InvalidUsage('Ingrediente inexistente en la hamburguesa', status_code=404)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def meter_en_dic(clase):
    ord = OrderedDict()
    attr = clase.__dict__
    for i in attr:
        if i.isalpha():
            ord[i] = attr[i]

    return ord

def revisar(consulta):
    try:
        uno = consulta.json("nombre")
        dos = consulta.json("descripcion")
        tres = consulta.json("precio")
        cuatro = consulta.json("imagen")
        if not (isinstance(uno,str) or isinstance(dos, str) or isinstance(tres, int) or isinstance(cuatro, str)):
            raise InvalidUsage("Parámetros inválidos", status_code=400)
    except None:
        raise InvalidUsage("Parámetros inválidos", status_code=400)

#crrer servidor

if __name__ == '__main__':
    app.run(debug=True)


import time
from ast import FunctionDef
from asyncio.windows_events import NULL
from datetime import date, datetime
from distutils.log import info
from doctest import debug
from pickle import TRUE
from sre_constants import SUCCESS

from flask import (Blueprint, Flask, flash, redirect, render_template, request,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, String, Table, Time, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

#----------------------------- CLASSES ------------------------------#

######################################################################
##                       ORDEM DE SERVIÇO                           ##
######################################################################


class OrdemServico(db.Model):
    __tablename__ = "ordemServico"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.JSON, nullable=False)
    orcamento_id = db.Column(
        db.Integer, db.ForeignKey('orcamento.id'))
    orcamento = relationship('Orcamento')
    funcionario_id = db.Column(
        db.Integer, db.ForeignKey('funcionarios.ID'))
    funcionario = relationship('Funcionario')
    descricao = db.Column(db.String(250), default=None)

    def __init__(self, status, orcamento_id, funcionario_id, descricao):
        self.status = status
        self.orcamento_id = orcamento_id
        self.funcionario_id = funcionario_id
        self.descricao = descricao

    def status_os(self):
        status = {
            '1': 'Criado',
            '2': 'Aprovado',
            '3': 'Cancelado',
            '4': 'Em execução',
            '5': 'Finalizado'
        }
        return status

    def retorna_status_os(self, status_id):
        lista = self.status_os()
        status = lista[status_id]
        return status


######################################################################
##                          AGENDAMENTO                             ##
######################################################################


class Agendamento(db.Model):
    __tablename__ = "agendamento"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_atual = db.Column(db.DateTime, default=datetime.now)
    data_agendamento = db.Column(db.DateTime, default=None)
    veiculo_id = db.Column(
        db.Integer, db.ForeignKey('veiculos.ID'))
    veiculo = relationship('Veiculo')
    orcamento_id = db.Column(
        db.Integer, db.ForeignKey('orcamento.id'))
    orcamento = relationship('Orcamento')

    def __init__(self, data_agendamento, veiculo_id, orcamento_id):
        self.data_agendamento = data_agendamento
        self.veiculo_id = veiculo_id
        self.orcamento_id = orcamento_id


######################################################################
##                           ORÇAMENTO                              ##
######################################################################


class Orcamento(db.Model):
    __tablename__ = "orcamento"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.JSON, nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.ID'))
    veiculo = relationship('Veiculo', backref="orcamento")
    servico_id = db.Column(db.JSON, db.ForeignKey('servicos.ID'))
    servico = relationship('Servico')
    produto_id = db.Column(db.JSON, db.ForeignKey('produtos.ID'))
    produto = relationship('Produto')
    agendamento = relationship('Agendamento')
    ordemServico = relationship('OrdemServico')

    def __init__(self, status, veiculo_id, servico_id, produto_id):
        self.status = status
        self.veiculo_id = veiculo_id
        self.servico_id = servico_id
        self.produto_id = produto_id

    def retorna_valor(self, servico_id, produto_id):
        valor_total = 0
        for serv in servico_id:
            for item in servico_id[serv]:
                servico = Servico.query.get(item)
                valor_total += servico.valor
        for prod in produto_id:
            for item in produto_id[prod]:
                produto = Produto.query.get(item)
                valor_total += produto.valor
        return valor_total

    def status_orc(self):
        status = {
            '1': 'Criado',
            '2': 'Aprovado',
            '3': 'Cancelado',
        }
        return status

    def retorna_status_orc(self, status_id):
        lista = self.status_orc()
        status = lista[status_id]
        return status

######################################################################
##                           VEÍCULO                                ##
######################################################################


class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column('Marca', db.String(150), nullable=False)
    modelo = db.Column('Modelo', db.String(150), nullable=False)
    cor = db.Column('Cor', db.String(150), nullable=False)
    placa = db.Column('Placa', db.String(150), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.ID'))
    cliente = relationship('Cliente')
    orcamentos = relationship(Orcamento, backref="veiculos")
    agendamento = relationship(Agendamento, backref='veiculos')

    def __init__(self, marca, modelo, cor, placa, cliente):
        self.marca = marca
        self.modelo = modelo
        self.cor = cor
        self.placa = placa
        self.cliente = cliente


######################################################################
##                           CLIENTE                                ##
######################################################################


class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    email = db.Column('Email', db.String(150), nullable=False)
    telefone = db.Column('Telefone', db.String(150), nullable=False)
    celular = db.Column('Celular', db.String(150), nullable=False)
    veiculos = relationship(Veiculo, backref="clientes")

    def __init__(self, nome, email, telefone, celular):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.celular = celular


######################################################################
##                         FUNCIONÁRIO                              ##
######################################################################

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    email = db.Column('Email', db.String(150), nullable=False)
    telefone = db.Column('Telefone', db.String(150), nullable=False)
    celular = db.Column('Celular', db.String(150), nullable=False)
    dataAniversario = db.Column(
        'DataAniversario', db.String(10), nullable=False)
    dataContrato = db.Column('DataContrato', db.String(10), nullable=False)
    funcao = db.Column('Funcao', db.String(150), nullable=False)
    senha = db.Column('Senha', db.String(50))
    ordemServico = relationship('OrdemServico', backref="funcionarios")

    def __init__(self, nome, email, telefone, celular, dataAniversario, dataContrato, funcao, senha):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.celular = celular
        self.dataAniversario = dataAniversario
        self.dataContrato = dataContrato
        self.funcao = funcao
        self.senha = None

######################################################################
##                           SERVIÇO                                ##
######################################################################


class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    descricao = db.Column('Descricao', db.String(250), nullable=False)
    valor = db.Column('Valor', db.Float, nullable=False)
    orcamentos = relationship(Orcamento, backref="servicos")

    def __init__(self, nome, descricao, valor):
        self.nome = nome
        self.descricao = descricao
        self.valor = valor


######################################################################
##                           PRODUTO                                ##
######################################################################


class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    descricao = db.Column('Descricao', db.String(250), nullable=False)
    valor = db.Column('Valor', db.Float, nullable=False)
    orcamentos = relationship(Orcamento, backref="produtos")

    def __init__(self, nome, descricao, valor):
        self.nome = nome
        self.descricao = descricao
        self.valor = valor


#------------------------------ ROTAS -------------------------------#


######################################################################
##                            LOGIN                                 ##
######################################################################

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        # remember = True if request.form.get('remember') else False

        user = Funcionario.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        # if not user or not check_password_hash(user.senha, password):
        if user == None:
            flash('Usuario ou senha incorreto')
            return redirect(url_for('login_post'))

        if user.senha == password:
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('index'))

        # if the above check passes, then we know the user has the right credentials
        flash('Usuario ou senha incorreto')
        return redirect(url_for('login_post'))


# region
@app.route('/validalogin/<string:_email>/<string:_senha>', methods=['GET'])
def valida_login(_email, _senha):
    funcionario = Funcionario.query.filter_by(email=_email).first()

    if funcionario.senha == None:
        return SUCCESS
    elif funcionario.senha == _senha:
        return "Sucesso"
    elif funcionario == None:
        return "Não encontrado"


######################################################################
##                            INDEX                                 ##
######################################################################

@app.route('/')
def index():
    agendamento = Agendamento.query.all()
    cliente = Cliente.query.all()
    veiculo = Veiculo.query.all()
    orcamento = Orcamento.query.all()
    data_tratada = datetime.now()
    return render_template("index.html", agendamento=agendamento, cliente=cliente, veiculo=veiculo, orcamento=orcamento, data_tratada=data_tratada)


######################################################################
##                           CLIENTE                                ##
######################################################################

@app.route('/cadastrar_clientes', methods=['GET', 'POST'])
def adiciona_cliente():
    if request.method == 'POST':
        veiculos_cadastrados = Veiculo.query.all()
        cliente = Cliente(request.form['nome'], request.form['email'],
                          request.form['telefone'], request.form['celular'])
        veiculo = Veiculo(request.form['marca'], request.form['modelo'],
                          request.form['cor'], request.form['placa'], cliente)

        for veic_cad in veiculos_cadastrados:
            if veiculo.placa == veic_cad.placa:
                mensagem_erro = 'Este veículo já foi cadastrado, revise os dados!'
                return render_template('cadastrar_clientes.html', mensagem_erro=mensagem_erro)
        else:
            db.session.add(cliente)
            db.session.add(veiculo)
            db.session.commit()
            mensagem_ok = f'{cliente.nome.upper()} foi cadastrado(a) com SUCESSO!'
            return render_template('cadastrar_clientes.html', mensagem_ok=mensagem_ok)
    return render_template('cadastrar_clientes.html')


@app.route('/resultado_clientes', methods=['GET', 'POST'])
def resultado_cliente():
    cliente = Cliente.query.all()
    veiculo = Veiculo.query.all()
    mensagem_info = 'Pesquise por informações do cliente ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao_cliente']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo_cliente']
        return render_template("resultado_clientes.html", clientes=cliente, veiculos=veiculo, opcao_cliente=opcao, campo_cliente=campo)
    return render_template("resultado_clientes.html", mensagem_info=mensagem_info)


@app.route('/editar_clientes/<int:id>', methods=['GET', 'POST'])
def edita_cliente(id):
    cliente = Cliente.query.get(id)
    veiculo = Veiculo.query.all()
    if request.method == 'POST':
        # salva com as novas informações inseridas
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        cliente.telefone = request.form['telefone']
        cliente.celular = request.form['celular']
        db.session.commit()
        # validação
        mensagem = f"{cliente.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_clientes.html", mensagem_editar=mensagem, veiculos=veiculo)
    return render_template('editar_clientes.html', cliente=cliente, veiculos=veiculo)


@app.route('/deletar_clientes/<int:id>')
def deleta_cliente(id):
    cliente = Cliente.query.get(id)
    db.session.delete(cliente)  # deleta os dados daquele cliente
    db.session.commit()
    # validação
    mensagem = f"{cliente.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    # return redirect(f'')
    return render_template("resultado_clientes.html", mensagem_deletar=mensagem)


@app.route('/info_clientes/<int:id>')
def info_cliente(id):
    cliente = Cliente.query.get(id)
    veiculo = Veiculo.query.all()
    return render_template('info_clientes.html', cliente=cliente, veiculos=veiculo)


######################################################################
##                           VEÍCULO                                ##
######################################################################

@app.route('/cadastrar_veiculo', methods=['GET', 'POST'])
def cadastro_veiculo():
    cliente = Cliente.query.all()
    mensagem_info = 'Pesquise por informações do cliente ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao_cliente']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo_cliente']
        return render_template("cadastrar_veiculo.html", clientes=cliente, opcao_cliente=opcao, campo_cliente=campo)
    return render_template("cadastrar_veiculo.html", mensagem_info=mensagem_info)


@app.route('/veiculos/<int:id>', methods=['GET', 'POST'])
def adiciona_veiculo(id):
    cliente = Cliente.query.get(id)
    veiculo_cliente = Veiculo.query.all()
    if request.method == 'POST':
        veiculo = Veiculo(request.form['marca'], request.form['modelo'],
                          request.form['cor'], request.form['placa'], cliente)
        if veiculo.marca == '' or veiculo.modelo == '' or veiculo.cor == '' or veiculo.placa == '':
            mensagem = 'Não deixe campos obrigatórios em branco!'
            return render_template('veiculos.html', cliente=cliente, veiculos=veiculo_cliente, mensagem=mensagem)
        else:
            db.session.add(veiculo)
            db.session.commit()
            mensagem_sucesso = f'Veículo cadastrado com SUCESSO!'
            flash(mensagem_sucesso, 'info')
            return redirect(f'/veiculos/{cliente.id}')
            # return render_template('veiculos.html', cliente = cliente, veiculos = veiculo_cliente, mensagem_sucesso = mensagem_sucesso)
    return render_template('veiculos.html', cliente=cliente, veiculos=veiculo_cliente)


@app.route('/editar_veiculo/<int:id>', methods=['GET', 'POST'])
def edita_veiculo(id):
    veiculo = Veiculo.query.get(id)
    id_cliente = veiculo.cliente_id
    cliente = Cliente.query.get(id_cliente)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        veiculo.marca = request.form['marca']
        veiculo.modelo = request.form['modelo']
        veiculo.cor = request.form['cor']
        veiculo.placa = request.form['placa']
        db.session.commit()
        mensagem_sucesso = f'Veículo editado com SUCESSO!'
        flash(mensagem_sucesso, 'info')
        return render_template("veiculos.html", mensagem_sucesso=mensagem_sucesso, cliente=cliente, veiculo=veiculo)
    return render_template("editar_veiculo.html", cliente=cliente, veiculo=veiculo)


@app.route('/deletar_veiculo/<int:id>')
def deleta_veiculo(id):
    veiculo = Veiculo.query.get(id)
    id_cliente = veiculo.cliente_id
    cliente = Cliente.query.get(id_cliente)
    db.session.delete(veiculo)
    db.session.commit()
    mensagem = f"Veículo placa {veiculo.placa} foi DELETADO(A)!"  # validação
    flash(mensagem, 'error')
    return redirect(f'/veiculos/{cliente.id}')
    # return render_template("veiculos.html", cliente = cliente, mensagem_deletar = mensagem)


######################################################################
##                        FUNCIONÁRIOS                              ##
######################################################################

@app.route('/cadastrar_funcionario', methods=['GET', 'POST'])
def adiciona_funcionario():
    if request.method == 'POST':
        funcionario = Funcionario(request.form['nome'], request.form['email'], request.form['telefone'],
                                  request.form['celular'], request.form['dataAniversario'], request.form['dataContrato'], request.form['funcao'], senha=None)
        db.session.add(funcionario)
        db.session.commit()
        mensagem_sucesso = f'{funcionario.nome.upper()} foi cadastrado(a) com **SUCESSO!**'
        return render_template('cadastrar_funcionario.html', mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_funcionario.html')


@app.route('/resultado_funcionarios', methods=['GET', 'POST'])
def resultado_funcionario():
    funcionario = Funcionario.query.all()
    mensagem_info = 'Pesquise por informações acima ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo']
        return render_template("resultado_funcionarios.html", funcionarios=funcionario, opcao=opcao, campo=campo)
    return render_template("resultado_funcionarios.html", mensagem_info=mensagem_info, funcionarios=funcionario)


@app.route('/editar_funcionarios/<int:id>', methods=['GET', 'POST'])
def edita_funcionario(id):
    funcionario = Funcionario.query.get(id)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        funcionario.nome = request.form['nome']
        funcionario.email = request.form['email']
        funcionario.telefone = request.form['telefone']
        funcionario.celular = request.form['celular']
        funcionario.dataAniversario = request.form['dataAniversario']
        funcionario.dataContrato = request.form['dataContrato']
        funcionario.funcao = request.form['funcao']
        funcionario.senha = None
        db.session.commit()
        # validação
        mensagem = f"{funcionario.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_funcionarios.html", mensagem_editar=mensagem)
    return render_template('editar_funcionarios.html', funcionario=funcionario)


@app.route('/deletar_funcionarios/<int:id>')
def deleta_funcionario(id):
    funcionario = Funcionario.query.get(id)
    db.session.delete(funcionario)
    db.session.commit()
    # validação
    mensagem = f"{funcionario.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_funcionarios.html", mensagem_deletar=mensagem)


@app.route('/info_funcionarios/<int:id>')
def info_funcionario(id):
    funcionario = Funcionario.query.get(id)
    dataAniversario_formatada = datetime.strptime(
        funcionario.dataAniversario, '%Y-%m-%d')
    dataContrato_formatada = datetime.strptime(
        funcionario.dataContrato, '%Y-%m-%d')
    return render_template('info_funcionarios.html', funcionario=funcionario, dataAniversario_formatada=dataAniversario_formatada, dataContrato_formatada=dataContrato_formatada)


######################################################################
##                           PRODUTO                                ##
######################################################################

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def adiciona_produto():
    if request.method == 'POST':
        produto = Produto(
            request.form['nome'], request.form['descricao'], float(request.form['valor']))
        db.session.add(produto)
        db.session.commit()
        mensagem_sucesso = f'{produto.nome.upper()} foi cadastrado(a) com SUCESSO!'
        return render_template('cadastrar_produto.html', mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_produto.html')


@app.route('/resultado_produto', methods=['GET', 'POST'])
def resultado_produto():
    produto = Produto.query.all()
    mensagem_info = 'Pesquise por informações acima ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo']
        return render_template("resultado_produto.html", produtos=produto, opcao=opcao, campo=campo)
    return render_template("resultado_produto.html", produtos=produto, mensagem_info=mensagem_info)


@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def edita_produto(id):
    produto = Produto.query.get(id)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.valor = request.form['valor']
        db.session.commit()
        # validação
        mensagem = f"{produto.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_produto.html", mensagem_editar=mensagem)
    return render_template('editar_produto.html', produto=produto)


@app.route('/deletar_produto/<int:id>')
def deleta_produto(id):
    produto = Produto.query.get(id)
    db.session.delete(produto)
    db.session.commit()
    # validação
    mensagem = f"{produto.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_produto.html", mensagem_deletar=mensagem)


@app.route('/info_produto/<int:id>')
def info_produto(id):
    produto = Produto.query.get(id)
    return render_template('info_produto.html', produto=produto)


######################################################################
##                           SERVIÇO                                ##
######################################################################

@app.route('/cadastrar_servico', methods=['GET', 'POST'])
def adiciona_servico():
    if request.method == 'POST':
        servico = Servico(
            request.form['nome'], request.form['descricao'], request.form['valor'])
        db.session.add(servico)
        db.session.commit()
        mensagem_sucesso = f'{servico.nome.upper()} foi cadastrado(a) com SUCESSO!'
        return render_template('cadastrar_servico.html', mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_servico.html')


@app.route('/resultado_servico', methods=['GET', 'POST'])
def resultado_servico():
    servico = Servico.query.all()
    mensagem_info = 'Pesquise por informações acima ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo']
        return render_template("resultado_servico.html", servicos=servico, opcao=opcao, campo=campo)
    return render_template("resultado_servico.html", servicos=servico, mensagem_info=mensagem_info)


@app.route('/editar_servico/<int:id>', methods=['GET', 'POST'])
def edita_servico(id):
    servico = Servico.query.get(id)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        servico.nome = request.form['nome']
        servico.descricao = request.form['descricao']
        servico.valor = request.form['valor']
        db.session.commit()
        # validação
        mensagem = f"{servico.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_servico.html", mensagem_editar=mensagem)
    return render_template('editar_servico.html', servico=servico)


@app.route('/deletar_servico/<int:id>')
def deleta_servico(id):
    servico = Servico.query.get(id)
    db.session.delete(servico)
    db.session.commit()
    # validação
    mensagem = f"{servico.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_servico.html", mensagem_deletar=mensagem)


@app.route('/info_servico/<int:id>')
def info_servico(id):
    servico = Servico.query.get(id)
    return render_template('info_servico.html', servico=servico)


######################################################################
##                           ORÇAMENTO                              ##
######################################################################

# PEGA AS INFORMAÇÕES DE CLIENTE
@app.route('/cadastrar_orcamento', methods=['GET', 'POST'])
def adiciona_orcamento_cliente():
    cliente = Cliente.query.all()
    if request.method == 'POST':
        opcao = request.form['opcao_cliente']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo_cliente']
        return render_template("cadastrar_orcamento_cliente.html", clientes=cliente, opcao_cliente=opcao, campo_cliente=campo)
    return render_template("cadastrar_orcamento_cliente.html")


# PEGA AS INFORMAÇÕES DO VEÍCULO
@app.route('/cadastrar_orcamento/<int:id_cliente>', methods=['GET', 'POST'])
def adiciona_orcamento_veiculo(id_cliente):
    cliente = Cliente.query.get(id_cliente)
    veiculo = Veiculo.query.all()
    return render_template('cadastrar_orcamento_veiculo.html', cliente=cliente, veiculos=veiculo)


# MONTA O ORÇAMENTO FINAL COM TODAS AS INFORMAÇÕES
@app.route('/orcamento/<int:id_orcamento>')
def retorna_orcamento(id_orcamento):
    orcamento = Orcamento.query.get(id_orcamento)
    veiculo = Veiculo.query.get(orcamento.veiculo_id)
    servico = Servico.query.all()
    produto = Produto.query.get(orcamento.produto_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    return render_template('orcamento.html', cliente=cliente, veiculo=veiculo, servico=servico, produto=produto, orcamento=orcamento)


# COMMITAR NO BANCO AS INFORMAÇÕES DE PRODUTOS E SERVIÇOS
@app.route('/cadastrar_orcamento/<int:id_cliente>/<int:id_veiculo>', methods=['GET', 'POST'])
def orcamento_itens(id_cliente, id_veiculo):
    cliente = Cliente.query.get(id_cliente)
    veiculo = Veiculo.query.get(id_veiculo)
    servico = Servico.query.all()
    produto = Produto.query.all()
    dict_servicos = {}
    dict_produtos = {}
    i = 0
    if request.method == 'POST':
        for getid in request.form.getlist('incluir_servico'):
            dict_servicos[i] = getid
            i += 1

        i = 0

        for getid in request.form.getlist('incluir_produto'):
            dict_produtos[i] = getid
            i += 1

        data = datetime.today().strftime('%Y-%m-%d')
        status = {'1': data}

        orcamento = Orcamento(status, id_veiculo, dict_servicos, dict_produtos)

        if dict_servicos == {} and dict_produtos == {}:
            mensagem_erro = f'Não é possível criar orçamento sem itens! Por favor revise os dados!'
            valor_total = 0
            return render_template('cadastrar_orcamento_itens.html', mensagem_erro=mensagem_erro, cliente=cliente, veiculo=veiculo, servico=servico, produto=produto, orcamento=orcamento, valor_total=valor_total)
        else:
            db.session.add(orcamento)
            db.session.commit()

        valor_total = orcamento.retorna_valor(
            orcamento.servico_id, orcamento.produto_id)

        mensagem_sucesso = f'Orçamento nº{orcamento.id} foi cadastrado(a) com SUCESSO!'
        # return render_template('orcamento.html', servico=servico, cliente=cliente, veiculo=veiculo, produto=produto)
        return render_template('orcamento.html', mensagem_ok=mensagem_sucesso, cliente=cliente, veiculo=veiculo, servico=servico, produto=produto, orcamento=orcamento, valor_total=valor_total)
    return render_template('cadastrar_orcamento_itens.html', cliente=cliente, veiculo=veiculo, servico=servico, produto=produto)


@app.route('/consultar_orcamentos', methods=['GET', 'POST'])
def consulta_orcamento():
    cliente = Cliente.query.all()
    veiculo = Veiculo.query.all()
    orcamento = Orcamento.query.all()
    servico = Servico.query.all()
    produto = Produto.query.all()
    mensagem_info = 'Pesquise por informações acima ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        cliente = Cliente.query.all()
        opcao = request.form['opcao_cliente']
        campo = request.form['campo_cliente']
        msg_erro = 'Não contém dados com esse registro. Realize uma nova busca.'
        return render_template("consultar_orcamentos.html", cliente=cliente, veiculo=veiculo, orcamento=orcamento, servico=servico, produto=produto, opcao_cliente=opcao, campo_cliente=campo, msg_erro=msg_erro)
    return render_template("consultar_orcamentos.html", mensagem_info=mensagem_info)


@app.route('/editar_orcamento/<int:id>', methods=['GET', 'POST'])
def edita_orcamento(id):
    orcamento = Orcamento.query.get(id)
    veiculo = Veiculo.query.get(orcamento.veiculo_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    servico = Servico.query.all()
    produto = Produto.query.all()
    dict_servicos = {}
    dict_produtos = {}
    i = 0
    if request.method == 'POST':
        for getid in request.form.getlist('incluir_servico'):
            dict_servicos[i] = getid
            i += 1

        i = 0

        for getid in request.form.getlist('incluir_produto'):
            dict_produtos[i] = getid
            i += 1

        if dict_servicos == {}:
            pass
        else:
            orcamento.servico_id = dict_servicos

        if dict_produtos == {}:
            pass
        else:
            orcamento.produto_id = dict_produtos

        if request.form['status'] == 'Selecione o status...':
            pass
        else:
            data = datetime.today().strftime('%Y-%m-%d')
            id_status = request.form['status']
            dic = {}
            dic[id_status] = data
            orcamento.status = dic

        db.session.commit()

        mensagem = f"Orçamento nº {orcamento.id} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("consultar_orcamentos.html", cliente=cliente, veiculo=veiculo, mensagem_editar=mensagem, orcamento=orcamento, servico=servico, produto=produto)
    return render_template('editar_orcamento.html', cliente=cliente, veiculo=veiculo, orcamento=orcamento, servico=servico, produto=produto)


@app.route('/deletar_orcamento/<int:id>')
def deleta_orcamento(id):
    orcamento = Orcamento.query.get(id)
    db.session.delete(orcamento)
    db.session.commit()
    # validação
    mensagem = f"Orçamento número {orcamento.id} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("consultar_orcamentos.html", orcamento=orcamento, mensagem_deletar=mensagem)


@app.route('/info_orcamentos/<int:id>')
def info_orcamento(id):
    orcamento = Orcamento.query.get(id)
    veiculo = Veiculo.query.get(orcamento.veiculo_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    servico = Servico.query.all()
    produto = Produto.query.all()
    valor_total = orcamento.retorna_valor(
        orcamento.servico_id, orcamento.produto_id)
    return render_template('info_orcamentos.html', cliente=cliente, veiculo=veiculo, orcamento=orcamento, servico=servico, produto=produto, valor_total=valor_total)


######################################################################
##                          AGENDAMENTO                             ##
######################################################################

@app.route('/cadastrar_agendamento', methods=['GET', 'POST'])
def adiciona_agendamento():
    if request.method == 'POST':
        veiculo = Veiculo.query.all()
        orcamento = Orcamento.query.get(request.form['id_orcamento'])
        busca_idVeiculo = request.form['placa_veiculo']
        idVeiculo = 0
        for carro in veiculo:
            if carro.placa == busca_idVeiculo:
                idVeiculo = carro.id
        if idVeiculo == 0:
            mensagem_erro = 'Placa não encontrada!'
            return render_template('cadastrar_agendamento.html', mensagem_erro=mensagem_erro)
        elif idVeiculo != orcamento.veiculo_id:
            mensagem_erro = 'Placa do veículo não corresponde ao orçamento!'
            return render_template('cadastrar_agendamento.html', mensagem_erro=mensagem_erro)
        else:
            recebe_data = request.form['data_agendamento']
            recebe_hora = request.form['hora_agendamento']
            data = recebe_data + ' ' + recebe_hora
            data_agendamento = datetime.strptime(data, '%Y-%m-%d %H:%M')
            agendamento = Agendamento(
                data_agendamento, idVeiculo, request.form['id_orcamento'])
            db.session.add(agendamento)
            db.session.commit()
            return redirect(url_for('info_agendamento', id=agendamento.id))
    return render_template('cadastrar_agendamento.html')


@app.route('/info_agendamento/<id>')
def info_agendamento(id):
    agendamento = Agendamento.query.get(id)
    veiculo = Veiculo.query.get(agendamento.veiculo_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    orcamento = Orcamento.query.get(agendamento.orcamento_id)
    data_agendada = f'{agendamento.data_agendamento.day}/{agendamento.data_agendamento.month}/{agendamento.data_agendamento.year}'
    if agendamento.data_agendamento.minute == 0:
        hora_agendada = f'{agendamento.data_agendamento.hour}h00'
    else:
        hora_agendada = f'{agendamento.data_agendamento.hour}h{agendamento.data_agendamento.minute}'
    return render_template('info_agendamento.html', agendamento=agendamento, veiculo=veiculo, cliente=cliente, orcamento=orcamento, data_agendada=data_agendada, hora_agendada=hora_agendada)


@app.route('/consultar_agendamentos', methods=['GET', 'POST'])
def consulta_agendamento():
    agendamento = Agendamento.query.all()
    cliente = Cliente.query.all()
    veiculo = Veiculo.query.all()
    orcamento = Orcamento.query.all()
    recebe_data_tratada = datetime.now()
    if request.method == 'POST':
        recebe_data = request.form['data_agendamento']
        if recebe_data == '':
            recebe_data_tratada = datetime.now()
            return render_template("consultar_agendamentos.html", agendamento=agendamento, cliente=cliente, veiculo=veiculo, orcamento=orcamento, recebe_data_tratada=recebe_data_tratada)
        else:
            recebe_data_tratada = datetime.strptime(recebe_data, '%Y-%m-%d')
            return render_template("consultar_agendamentos.html", agendamento=agendamento, cliente=cliente, veiculo=veiculo, orcamento=orcamento, recebe_data_tratada=recebe_data_tratada)
    return render_template("consultar_agendamentos.html", agendamento=agendamento, cliente=cliente, veiculo=veiculo, orcamento=orcamento, recebe_data_tratada=recebe_data_tratada)


@app.route('/editar_agendamento/<int:id>', methods=['GET', 'POST'])
def edita_agendamento(id):
    agendamento = Agendamento.query.get(id)
    veiculo = Veiculo.query.get(agendamento.veiculo_id)
    orcamento = Orcamento.query.get(agendamento.orcamento_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    if request.method == 'POST':
        agendamento = Agendamento.query.get(id)
        recebe_data = request.form['data_agendamento']
        recebe_hora = request.form['hora_agendamento']
        data = recebe_data + ' ' + recebe_hora
        nova_data = datetime.strptime(data, '%Y-%m-%d %H:%M')
        agendamento.data_agendamento = nova_data
        db.session.commit()
        # validação
        mensagem = f"Agendamento nº{agendamento.id} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template('consultar_agendamentos.html', mensagem_editar=mensagem)
    return render_template('editar_agendamento.html', cliente=cliente, agendamento=agendamento, veiculo=veiculo, orcamento=orcamento)


@app.route('/deletar_agendamento/<int:id>')
def deleta_agendamento(id):
    agendamento_del = Agendamento.query.get(id)
    db.session.delete(agendamento_del)
    db.session.commit()
    # validação
    mensagem = f"Agendamento número {agendamento_del.id} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("consultar_agendamentos.html", agendamento_del=agendamento_del, mensagem_deletar=mensagem)


######################################################################
##                      ORDEM DE SERVIÇO                            ##
######################################################################

@app.route('/cadastrar_os', methods=['GET', 'POST'])
def adiciona_os():
    funcionario = Funcionario.query.all()
    if request.method == 'POST':
        if request.form['funcionario'] == 'Escolha o funcionário...':
            mensagem_erro = f'Você precisa selecionar um funcionário para criar a O.S.'
            return render_template('cadastrar_os.html', funcionario=funcionario, mensagem_erro=mensagem_erro)
        else:
            funcionario = Funcionario.query.all()
            data = datetime.today().strftime('%Y-%m-%d')
            status = {'1': data}
            ordemServico = OrdemServico(
                status, request.form['orcamento'], request.form['funcionario'], request.form['descricao'])

            db.session.add(ordemServico)
            db.session.commit()
            mensagem_sucesso = f'OS nº {ordemServico.id} foi cadastrada com SUCESSO!'
            return render_template('cadastrar_os.html', funcionario=funcionario, mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_os.html', funcionario=funcionario)


@app.route('/resultado_os', methods=['GET', 'POST'])
def resultado_os():
    ordemServico = OrdemServico.query.all()
    servico = Servico.query.all()
    funcionario = Funcionario.query.all()
    mensagem_info = 'Pesquise por informações acima ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao']
        campo = request.form['campo']
        ordemServico = OrdemServico.query.all()
        orcamento = Orcamento.query.all()
        cliente = Cliente.query.all()
        veiculo = Veiculo.query.all()
        funcionario = Funcionario.query.all()
        servico = Servico.query.all()
        return render_template('resultado_os.html', opcao=opcao, campo=campo, ordemServico=ordemServico, orcamento=orcamento, cliente=cliente, veiculo=veiculo, funcionario=funcionario, servico=servico)
    return render_template('resultado_os.html', mensagem_info=mensagem_info, ordemServico=ordemServico, servico=servico, funcionario=funcionario)


@app.route('/editar_os/<int:id>', methods=['GET', 'POST'])
def edita_os(id):
    ordemServico = OrdemServico.query.get(id)
    orcamento = Orcamento.query.get(ordemServico.orcamento_id)
    veiculo = Veiculo.query.get(orcamento.veiculo_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    funcionario = Funcionario.query.all()
    servico = Servico.query.all()
    if request.method == 'POST':
        ordemServico = OrdemServico.query.get(id)

        if request.form['funcionario'] == 'Escolha o funcionário...' or ordemServico.funcionario_id == request.form['funcionario']:
            pass
        else:
            ordemServico.funcionario_id = request.form['funcionario']

        if request.form['descricao'] == '' or ordemServico.descricao == request.form['descricao']:
            pass
        else:
            ordemServico.descricao = request.form['descricao']

        if request.form['status'] == 'Selecione o status...' or ordemServico.funcionario_id == request.form['funcionario']:
            pass
        else:
            data = datetime.today().strftime('%Y-%m-%d')
            id_status = request.form['status']
            dic = {}
            dic[id_status] = data
            ordemServico.status = dic

        db.session.commit()
        mensagem = f"Ordem de Serviço nº{ordemServico.id} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"

        return render_template('resultado_os.html', ordemServico=ordemServico, mensagem_editar=mensagem)
    return render_template('editar_os.html', cliente=cliente, ordemServico=ordemServico, orcamento=orcamento, veiculo=veiculo, funcionario=funcionario, servico=servico)


@app.route('/info_os/<int:id>')
def info_os(id):
    ordemServico = OrdemServico.query.get(id)
    orcamento = Orcamento.query.get(ordemServico.orcamento_id)
    veiculo = Veiculo.query.get(orcamento.veiculo_id)
    cliente = Cliente.query.get(veiculo.cliente_id)
    funcionario = Funcionario.query.get(ordemServico.funcionario_id)
    servico = Servico.query.all()
    return render_template('info_os.html', ordemServico=ordemServico, orcamento=orcamento, veiculo=veiculo, cliente=cliente, funcionario=funcionario, servico=servico)


@app.route('/deletar_os/<int:id>')
def deleta_os(id):
    deletar_os = OrdemServico.query.get(id)
    db.session.delete(deletar_os)
    db.session.commit()
    # validação
    mensagem = f"Ordem de Serviço nº {deletar_os.id} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_os.html", mensagem_deletar=mensagem)


######################################################################
##                             MAIN                                 ##
######################################################################
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.secret_key = "superchavesecreta"
    app.run(debug=True, port=4000)

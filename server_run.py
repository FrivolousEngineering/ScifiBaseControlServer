from Server.Server import Server


from Server.NodeBlueprint import node_blueprint
app = Server()

app.register_blueprint(node_blueprint)

app.run(debug=True)
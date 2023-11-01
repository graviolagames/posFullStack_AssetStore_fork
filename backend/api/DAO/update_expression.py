class UpdateExpression:
    expression = ""
    attribute_names = ""
    attribute_values = ""
    def __init__(self,expression,attribute_names,attribute_values):
        self.expression = expression
        self.attribute_names = attribute_names
        self.attribute_values = attribute_values

from marshmallow import Schema, fields


class ConfigSchema(Schema):
    validation = fields.Dict()

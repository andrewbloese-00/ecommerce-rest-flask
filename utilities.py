from flask import jsonify
def respond(payload):
    return jsonify({
        "success": True,
        "data": payload
    })

def respond_fail(err):
    return jsonify({
        "success": False,
        "error": err
    })

def get_attrs( attributesStr , json ):
    body = {}
    for attr in attributesStr.split(","):
        print(attr ,end=": ")
        print(json.get(attr))
        body[attr]=json.get(attr)
    
    return body
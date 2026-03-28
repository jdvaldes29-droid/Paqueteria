#from app.supabase_client import supabase
#from flask import Flask, jsonify

#app = Flask(__name__)

#@app.route("/ubicaciones")

#def ubicaciones():

#    res = supabase.table("ubicaciones") \
#        .select("latitud,longitud,repartidor_id") \
#        .order("timestamp", desc=True) \
#        .limit(50) \
#        .execute()

#    return jsonify(res.data)
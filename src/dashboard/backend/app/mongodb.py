from pymongo import MongoClient

def get_database():
  uri = """mongodb+srv://dbuser:dbuser@
           cluster0.w9bpnhg.mongodb.net/?retryWrites=true&w=majority"""
  client = MongoClient(uri)
  return client['Cluster0']

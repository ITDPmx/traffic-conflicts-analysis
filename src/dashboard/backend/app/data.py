from mongodb import get_database
from datetime import datetime, timedelta
import random
import people
from bson.objectid import ObjectId

def random_date(start_date, end_date):
  """Get a random date within the given timestamps"""
  start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
  end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

  days_diff = (end_datetime - start_datetime).days

  random_days = random.randint(0, days_diff)

  random_datetime = start_datetime + timedelta(days=random_days)

  random_date = random_datetime.strftime('%Y-%m-%d')
  return random_date

def insert_activities():
  """Insert random activities"""
  coll =  get_database().activities
  activities = coll.find({}, {'_id': False})
  i = 0
  while i < 7:
    for activity in activities:
      activity['taken_at'] = random_date('2023-05-20', '2023-06-03')
      activity['counts']['running'] = random.randint(3, 10)
      activity['counts']['playing'] = random.randint(4, 15)
      activity['counts']['reading'] = random.randint(2, 5)
      activity['counts']['walking'] = random.randint(3, 10)
      coll.insert_one(activity)
    i+=1

def insert_people():
  """Insert random people entities"""
  points = people.gen_people_points()
  coll = get_database().people
  coll.insert_many(points)

def insert_processed_images():
  """Insert random image entities"""
  coll = get_database().processed_images
  processed_images = coll.find({}, {'_id': False})
  for img in processed_images:
    img['taken_at'] = random.randint(1684562400000, 1685734341242)
    img['peope_count'] = random.randint(4, 15)
    coll.insert_one(img)

def delete_duplicate_activities():
  """Get rid of duplicate activities"""
  coll =  get_database().activities
  activities = coll.find({})
  dates = set()
  for act in activities:
    if act['taken_at'] in dates:
      coll.delete_one({'_id': ObjectId(act['_id'])})
    else:
      dates.add(act['taken_at'])

def add_activities_to_points():
  """Insert activities to each person entity"""
  db = get_database()
  coll = db.people
  ppl = db.people.find({})
  activities = ['running', 'reading', 'playing', 'walking']

  for p in ppl:
    activity = activities[random.randint(0, 3)]
    coll.update_one(
      {'_id': ObjectId(p['_id'])}, 
      {"$set": {'activity': activity}})

def get_date_count(start_timestamp_ms, end_timestamp_ms):
    """Count dates from timestamps"""
    start_date = datetime.fromtimestamp(start_timestamp_ms/1000)
    end_date = datetime.fromtimestamp(end_timestamp_ms/1000)

    date_diff = end_date - start_date
    date_count = date_diff.days+1

    return date_count